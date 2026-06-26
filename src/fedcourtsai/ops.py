"""Operational analytics roll-up: pipeline health, backfill progress, spend.

A *read-only* snapshot of authoritative sources — the GitHub Actions run history,
the seed cursor, and the recorded usage ledger — so no pipeline run has to write
an ops record (which would reintroduce the concurrent-writer problem the corpus
already manages). ``fedcourts ops-report`` renders this to Markdown (the run-ops
dashboard issue) and optionally to JSON.

Unlike the deterministic leaderboard / back-test roll-ups, this is a point-in-time
view: it carries ``generated_at`` and run durations, so it is not byte-stable.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime

from .schemas import (
    BackfillCourt,
    BackfillProgress,
    ModelUsage,
    OpsReport,
    SeedProgress,
    SpendSummary,
    WorkflowHealth,
)

# Conclusions that count as a completed-but-not-successful run.
_FAILURE_CONCLUSIONS = frozenset({"failure", "timed_out", "cancelled", "startup_failure"})


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


def build_ops_report(
    *,
    generated_at: str,
    runs: Iterable[Mapping[str, object]],
    progress: SeedProgress,
    courts: Sequence[str],
    usage: Iterable[ModelUsage],
) -> OpsReport:
    """Assemble the full operational snapshot. ``generated_at`` is passed in (no clock)."""
    return OpsReport(
        generated_at=generated_at,
        health=summarize_health(runs),
        backfill=summarize_backfill(progress, courts),
        spend=summarize_spend(usage),
    )


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


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
    lines += [
        "",
        "## Backfill progress",
        f"Snapshot `{bf.snapshot or '—'}` · "
        f"courts complete **{bf.courts_complete}/{bf.courts_total}** · "
        f"cases **{bf.cases_loaded:,}/{total}** ({overall})",
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
        "",
        "> Estimated from recorded `usage.json` at the rates in `fedcourtsai.pricing`; "
        "check the provider billing dashboards for ground truth.",
    ]
    return "\n".join(lines) + "\n"
