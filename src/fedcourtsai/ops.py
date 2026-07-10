"""Operational analytics roll-up: pipeline health, backfill progress, spend.

A *read-only* snapshot of authoritative sources — the GitHub Actions run history,
the seed cursor, the recorded usage ledger, and the committed ``flags.json`` files
agents leave under ``data/`` — so no pipeline run has to write an ops record (which
would reintroduce the concurrent-writer problem the corpus already manages).
``fedcourts ops-report`` renders this to Markdown (the run-ops dashboard issue) and
optionally to JSON.

Unlike the deterministic leaderboard / back-test roll-ups, this is a point-in-time
view: it carries ``generated_at`` and run durations, so it is not byte-stable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timedelta

from .collect import flags_table
from .schemas import (
    AgentFlags,
    AgentToolingFeedback,
    BackfillCourt,
    BackfillProgress,
    CorpusScopeAudit,
    CostEstimate,
    DataHealth,
    FlagsDigest,
    FlagSeverity,
    ModelUsage,
    OpenTriggerIssue,
    OpsReport,
    SeedProgress,
    SpendSummary,
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


def summarize_backfill(progress: SeedProgress, courts: Sequence[str]) -> BackfillProgress:
    """Project the seed cursor into whole-backfill progress across the tracked courts.

    Per-court ``percent`` is shown wherever the court's total is known (or it is
    complete); the overall ``percent`` / ``cases_total`` are reported only when
    *every* court's total is known, so a partial total never reads as the whole.
    """
    entries: list[BackfillCourt] = []
    cases_loaded = 0
    known_totals: list[int] = []
    every_total_known = True
    courts_complete = 0

    for court in courts:
        cp = progress.courts.get(court)
        offset = cp.offset if cp else 0
        total = cp.total if cp else None
        complete = cp.complete if cp else False
        cases_loaded += offset
        if complete:
            courts_complete += 1

        if total:
            percent: float | None = round(100.0 * offset / total, 1)
            known_totals.append(total)
        elif complete:
            percent = 100.0
            known_totals.append(offset)  # a complete court's offset is its total
        else:
            percent = None
            every_total_known = False

        entries.append(
            BackfillCourt(
                court=court, offset=offset, total=total, percent=percent, complete=complete
            )
        )

    cases_total = sum(known_totals) if every_total_known else None
    overall = round(100.0 * cases_loaded / cases_total, 1) if cases_total else None
    return BackfillProgress(
        snapshot=progress.snapshot,
        courts_total=len(courts),
        courts_complete=courts_complete,
        cases_loaded=cases_loaded,
        cases_total=cases_total,
        percent=overall,
        entries=entries,
    )


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


def _days_between(earlier: str, later: str) -> float | None:
    """Fractional days from ``earlier`` to ``later`` (ISO-8601), or None if unparseable."""
    start, end = _parse_iso(earlier), _parse_iso(later)
    if start is None or end is None:
        return None
    return (end - start).total_seconds() / 86400.0


def project_backfill(
    backfill: BackfillProgress, previous: OpsReport | None, generated_at: str
) -> BackfillProgress:
    """Add the load rate + projected completion date from the previous snapshot.

    Returns ``backfill`` unchanged when there is no comparable prior snapshot or no
    forward progress. The ETA needs both a positive rate and a known ``cases_total``.
    """
    if previous is None:
        return backfill
    days = _days_between(previous.generated_at, generated_at)
    if days is None or days <= 0:
        return backfill
    rate = (backfill.cases_loaded - previous.backfill.cases_loaded) / days
    if rate <= 0:
        return backfill.model_copy(update={"cases_per_day": round(rate, 1)})

    eta_date: str | None = None
    if backfill.cases_total is not None:
        remaining = max(0, backfill.cases_total - backfill.cases_loaded)
        now = _parse_iso(generated_at)
        if now is not None:
            eta_date = (now + timedelta(days=remaining / rate)).date().isoformat()
    return backfill.model_copy(update={"cases_per_day": round(rate, 1), "eta_date": eta_date})


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
    progress: SeedProgress,
    courts: Sequence[str],
    usage: Iterable[ModelUsage],
    flags: Iterable[AgentFlags] = (),
    tooling: Iterable[AgentToolingFeedback] = (),
    previous: OpsReport | None = None,
    data_health: DataHealth | None = None,
    scope_audit: CorpusScopeAudit | None = None,
    open_triggers: list[OpenTriggerIssue] | None = None,
) -> OpsReport:
    """Assemble the full operational snapshot. ``generated_at`` is passed in (no clock).

    ``previous`` (the prior snapshot, e.g. from the ``ops-metrics`` branch) drives the
    backfill rate + ETA; without it those fields stay null. ``data_health`` is the
    data-validation verdict the dashboard presents alongside run health; it is
    surfaced as supplied (the wiring layer owns producing it), null when absent.
    ``scope_audit`` is the predict-scope census (``corpus-scope-audit``), surfaced the
    same way. ``flags`` is the committed ``flags.json`` ledger the dashboard rolls into
    its open-flags digest and ``tooling`` the committed ``tooling.json`` self-reports it
    rolls into the tooling-feedback digest (each empty when none are committed).
    """
    run_list = list(runs)
    spend = summarize_spend(usage)
    backfill = project_backfill(summarize_backfill(progress, courts), previous, generated_at)
    return OpsReport(
        generated_at=generated_at,
        health=summarize_health(run_list),
        backfill=backfill,
        spend=spend,
        cost=estimate_cost(run_list, spend),
        data_health=data_health,
        flags=summarize_flags(flags),
        tooling=summarize_tooling(tooling),
        scope_audit=scope_audit,
        open_triggers=open_triggers,
    )


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


# The run:* labels whose trigger issues are transient by design: the run's ready
# PR closes them on merge, and an empty matrix closes them with a note. (run:pull
# and run:seed issues are long-lived logs/trackers, so they are not stall signals.)
TRIGGER_LABELS: tuple[str, ...] = ("run:predict", "run:evaluate", "run:reconcile")


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


def render_scope_audit(audit: CorpusScopeAudit) -> str:
    """Render the predict-scope census: open events the scope excludes, by reason.

    The dashboard window onto the seed scope reconcile: how many still-open
    SCOTUS events the corpus carries that the predict scope drops, split into a
    ``recoverable`` subset (a disposition signal — re-ingestible) and the bare rest.
    """
    lines = ["## Out-of-scope open events"]
    if audit.skipped:
        lines.append("- _skipped (no corpus pulled)_")
        return "\n".join(lines) + "\n"
    excluded = sum(e.open_events for e in audit.exclusions)
    if not excluded:
        lines.append(
            f"- None — all {audit.scotus_open_events:,} open SCOTUS event(s) are in scope."
        )
        return "\n".join(lines) + "\n"
    recoverable = sum(e.recoverable for e in audit.exclusions)
    lines += [
        f"**{excluded:,}** of {audit.scotus_open_events:,} open SCOTUS event(s) are out of "
        f"scope — **{recoverable:,}** carry a disposition signal (re-ingestible), the rest are "
        "bare. Candidates for the seed-side corpus reconcile.",
        "",
        "| reason | cases | open events | recoverable |",
        "|--------|------:|------------:|------------:|",
    ]
    for e in audit.exclusions:
        lines.append(f"| {e.reason} | {e.cases:,} | {e.open_events:,} | {e.recoverable:,} |")
    if audit.unclassified:
        in_scope = sum(u.open_events for u in audit.unclassified)
        lines += [
            "",
            f"_Not excluded ({in_scope:,} open SCOTUS event(s)) — why the scope keeps them, the "
            "scope-refinement signal:_",
            "",
            "| in-scope reason | open events |",
            "|-----------------|------------:|",
        ]
        for u in audit.unclassified:
            lines.append(f"| {u.reason} | {u.open_events:,} |")
    if audit.unparseable_docket_shapes:
        lines += [
            "",
            "_Top docket shapes in the not-parseable bucket (`9`=digit, `A`/`a`=letter) — "
            "the formats a Term-parser broadening would target:_",
            "",
            "| shape | open events |",
            "|-------|------------:|",
        ]
        for s in audit.unparseable_docket_shapes:
            lines.append(f"| `{s.shape}` | {s.count:,} |")
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

    bf = report.backfill
    overall = "—" if bf.percent is None else f"{bf.percent}%"
    total = "?" if bf.cases_total is None else f"{bf.cases_total:,}"
    pace = ""
    if bf.cases_per_day is not None:
        pace = f" · **{bf.cases_per_day:,.0f}**/day"
        if bf.eta_date is not None:
            pace += f" · ETA **{bf.eta_date}**"
    lines += [
        "",
        "## Backfill progress",
        f"Snapshot `{bf.snapshot or '—'}` · "
        f"courts complete **{bf.courts_complete}/{bf.courts_total}** · "
        f"cases **{bf.cases_loaded:,}/{total}** ({overall}){pace}",
        "",
        "| Court | Loaded | Total | % | Done |",
        "|-------|-------:|------:|--:|:----:|",
    ]
    for c in bf.entries:
        ctotal = "?" if c.total is None else f"{c.total:,}"
        pct = "?" if c.percent is None else f"{c.percent}%"
        lines.append(
            f"| {c.court} | {c.offset:,} | {ctotal} | {pct} | {'✅' if c.complete else ''} |"
        )

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

    if report.tooling is not None:
        lines += ["", render_tooling_digest(report.tooling).rstrip("\n")]

    if report.data_health is not None:
        lines += ["", render_data_health(report.data_health).rstrip("\n")]

    if report.scope_audit is not None:
        lines += ["", render_scope_audit(report.scope_audit).rstrip("\n")]

    return "\n".join(lines) + "\n"
