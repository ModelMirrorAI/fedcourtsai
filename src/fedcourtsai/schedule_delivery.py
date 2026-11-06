"""Whether GitHub's scheduler delivered each scheduled workflow's cron slots.

``fedcourts ops-report --schedule-runs`` reads the schedule-event runs GitHub
created for every workflow that declares a ``schedule:`` trigger and sets them
against the slots those crons promise, over the last day and the last week. The
public status page's lane state reads the newest run of *any* event, so a
dispatched or chained run hides a dropped tick there; this section reads
schedule-event runs alone, so it counts what the scheduler itself delivered.

Each run is matched to the newest slot at or before its creation time (see
:class:`~fedcourtsai.schemas.DeliveryWindow` for how that reads a backlog). A
slot younger than :data:`SETTLE` is not counted yet, because GitHub may still
deliver it.
"""

from __future__ import annotations

import bisect
import statistics
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .ops import parse_iso
from .schemas import DeliveryWindow, ScheduleDelivery, WorkflowDelivery
from .site_status import LATE_GRACE, Cron, parse_cron, workflow_crons

#: How old a slot must be before it counts as delivered or dropped. The status
#: page's own grace, so the two surfaces agree on when a tick is overdue.
SETTLE = LATE_GRACE

#: The two trailing windows the section reports.
DAY = timedelta(hours=24)
WEEK = timedelta(days=7)

_DEFAULT_BRANCH = "main"


def slots_between(crons: Sequence[Cron], start: datetime, end: datetime) -> list[datetime]:
    """Every instant in ``(start, end]`` that any of ``crons`` fires, oldest first."""
    found: set[datetime] = set()
    day = start.date()
    while day <= end.date():
        sunday_first = (day.weekday() + 1) % 7
        for cron in crons:
            if cron.weekdays is not None and sunday_first not in cron.weekdays:
                continue
            for hour in cron.hours:
                for minute in cron.minutes:
                    tick = datetime(day.year, day.month, day.day, hour, minute, tzinfo=UTC)
                    if start < tick <= end:
                        found.add(tick)
        day += timedelta(days=1)
    return sorted(found)


def _aware(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    parsed = parse_iso(value)
    if parsed is None:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def schedule_runs(rows: Iterable[object]) -> dict[str, list[datetime]]:
    """The creation times of schedule-event runs on `main`, keyed by workflow stem.

    ``rows`` is the REST ``workflow_runs`` list, or the pages ``gh api --paginate
    --slurp`` writes (each an object carrying ``workflow_runs``), or a list of
    either. A run is keyed by its workflow file's stem (``path``), not its display
    name, so a renamed workflow keeps its record.
    """
    out: dict[str, list[datetime]] = {}

    def visit(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                visit(child)
            return
        if not isinstance(item, Mapping):
            return
        if "workflow_runs" in item:
            visit(item["workflow_runs"])
            return
        if item.get("event") != "schedule":
            return
        branch = item.get("head_branch")
        if branch is not None and branch != _DEFAULT_BRANCH:
            return
        path = item.get("path")
        created = _aware(item.get("created_at"))
        if not isinstance(path, str) or created is None:
            return
        stem = Path(path.split("@", 1)[0]).stem
        out.setdefault(stem, []).append(created)

    visit(list(rows))
    return {stem: sorted(times) for stem, times in out.items()}


def _minutes(delta: timedelta) -> int:
    return int(delta.total_seconds() // 60)


def match_slots(slots: Sequence[datetime], runs: Sequence[datetime]) -> dict[datetime, datetime]:
    """Each slot with a run, mapped to the first run matched to it.

    A run is matched to the newest slot at or before it; a run before every slot
    is matched to none. ``slots`` and ``runs`` are sorted oldest first.
    """
    first: dict[datetime, datetime] = {}
    for run in runs:
        index = bisect.bisect_right(slots, run) - 1
        if index >= 0:
            first.setdefault(slots[index], run)
    return first


def delivery_window(
    slots: Sequence[datetime],
    matched: Mapping[datetime, datetime],
    *,
    now: datetime,
    span: timedelta,
) -> DeliveryWindow:
    """The settled slots of the trailing ``span`` and how many were delivered."""
    end = now - SETTLE
    counted = [slot for slot in slots if end - span < slot <= end]
    late = [_minutes(matched[slot] - slot) for slot in counted if slot in matched]
    return DeliveryWindow(
        hours=int(span.total_seconds() // 3600),
        slots=len(counted),
        delivered=len(late),
        dropped=len(counted) - len(late),
        lateness_p50_min=int(statistics.median(late)) if late else None,
        lateness_max_min=max(late) if late else None,
    )


def workflow_delivery(
    stem: str, *, crons: Sequence[str], runs: Sequence[datetime], now: datetime
) -> WorkflowDelivery:
    """One workflow's delivery record, with the reasons it needs a look."""
    parsed = [parse_cron(expression) for expression in crons]
    # A week of slots plus a day before it, so a run in the week's first hours
    # matches the slot it served rather than none.
    slots = slots_between(parsed, now - WEEK - SETTLE - DAY, now)
    seen = [run for run in runs if run <= now]
    matched = match_slots(slots, seen)
    day = delivery_window(slots, matched, now=now, span=DAY)
    week = delivery_window(slots, matched, now=now, span=WEEK)
    last = seen[-1] if seen else None
    settled = [slot for slot in slots if slot <= now - SETTLE]
    flags: list[str] = []
    if settled and settled[-1] not in matched and (last is None or last < now - DAY):
        since = "ever in the feed" if last is None else f"since {last:%Y-%m-%d %H:%MZ}"
        flags.append(
            f"no scheduled run {since}; the slot at {settled[-1]:%Y-%m-%d %H:%MZ} was not delivered"
        )
    if day.slots and 2 * day.delivered < day.slots:
        flags.append(f"{day.delivered} of {day.slots} slots in the last 24 h delivered")
    return WorkflowDelivery(
        workflow=stem,
        crons=list(crons),
        day=day,
        week=week,
        last_scheduled_at=last,
        flags=flags,
    )


def scheduled_workflows(workflows_root: Path) -> dict[str, list[str]]:
    """Every workflow file under ``workflows_root`` that declares a cron, by stem."""
    out: dict[str, list[str]] = {}
    for path in sorted(workflows_root.glob("*.yml")):
        crons = workflow_crons(workflows_root, path.stem)
        if crons:
            out[path.stem] = crons
    return out


def build_schedule_delivery(
    rows: Iterable[object], *, workflows_root: Path, now: datetime
) -> ScheduleDelivery:
    """Every scheduled workflow's delivery record, in file-name order.

    A workflow whose crons this reader does not model is left out rather than
    failing the section; the status page's own reader refuses the same shapes.
    """
    runs = schedule_runs(rows)
    workflows: list[WorkflowDelivery] = []
    for stem, crons in scheduled_workflows(workflows_root).items():
        try:
            workflows.append(workflow_delivery(stem, crons=crons, runs=runs.get(stem, []), now=now))
        except ValueError:
            continue
    return ScheduleDelivery(settle_minutes=_minutes(SETTLE), workflows=workflows)


def _lateness(window: DeliveryWindow) -> str:
    if window.lateness_p50_min is None or window.lateness_max_min is None:
        return "—"
    return f"{window.lateness_p50_min} / {window.lateness_max_min} min"


def render_schedule_delivery(delivery: ScheduleDelivery) -> str:
    """The run-ops summary section: one row per scheduled workflow, flagged ones first."""
    flagged = [w for w in delivery.workflows if w.flags]
    lines = [
        "## Schedule delivery",
        "",
        "Cron slots each scheduled workflow declares, against the schedule-event runs "
        "GitHub created for them. A run is matched to the newest slot at or before it, "
        "so a backlog reads as dropped slots; lateness is run creation against the slot "
        f"(median / max). Slots younger than {delivery.settle_minutes} min are not "
        "counted yet.",
        "",
    ]
    if not delivery.workflows:
        return "\n".join([*lines, "_No scheduled workflow found._", ""])
    if flagged:
        lines += [
            f"**{len(flagged)} workflow(s) flagged:**",
            "",
            *(f"- `{w.workflow}`: {'; '.join(w.flags)}" for w in flagged),
            "",
        ]
    else:
        lines += ["_No workflow flagged._", ""]
    lines += [
        "| Workflow | 24 h delivered | 24 h lateness | 7 d delivered | 7 d lateness |",
        "|----------|---------------:|--------------:|--------------:|-------------:|",
    ]
    ordered = flagged + [w for w in delivery.workflows if not w.flags]
    for w in ordered:
        lines.append(
            f"| {w.workflow} | {w.day.delivered}/{w.day.slots} | {_lateness(w.day)} | "
            f"{w.week.delivered}/{w.week.slots} | {_lateness(w.week)} |"
        )
    return "\n".join([*lines, ""])
