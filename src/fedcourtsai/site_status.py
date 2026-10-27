"""The public status page's daily snapshot: is the pipeline up, what has it made.

``fedcourts ops-report --status-out`` renders :class:`PublicStatus` on the
run-ops schedule beside the ops report, and the run-ops job publishes it to the
``ops-metrics`` branch, where the public site reads it at build time. Four
sections, in the order the page shows them:

- **Lanes** — one row per scheduled pipeline workflow, judged against the
  schedule the workflow file itself declares, so a changed cron moves the
  judgement with it rather than drifting from a table kept here.
- **Production** — the cell census over the trailing 7 days, 30 days and the
  October Term to date, the same windows and the same census as the weekly
  digest's production blocks.
- **Coverage** — the public ledger's size and the live watchlist's document
  readiness.
- **Back-tests** — each committed back-test's headline, with its artifact and
  vintage, and the reading rule that has to travel with it.

The site states what this file states and computes nothing, so every figure is
formatted here. It carries no spend figure and no agent-written text.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Literal

import yaml

from .ops import (
    _BACKTEST_HEADLINE_COURT,
    _DOCKET_CLASS_LABELS,
    ProducedWindow,
    Vintaged,
    WeeklyAnalytics,
    WeeklyProduction,
    _brier,
    _pct,
    _signed_pct,
    parse_iso,
)
from .schemas import (
    Backtest,
    BacktestCourtScore,
    CertBacktest,
    LaneState,
    LiveFrontier,
    MeritsBacktest,
    OpsReport,
    PublicStatus,
    SalienceReplay,
    StatusBacktest,
    StatusCoverage,
    StatusLane,
    StatusProduction,
    StatusStageCells,
    StatusTable,
)


@dataclass(frozen=True)
class Lane:
    """A scheduled workflow the status page reports, and how it is described."""

    stem: str
    label: str
    what: str


#: The lanes the page shows, in pipeline order. Each names a workflow file under
#: ``.github/workflows/`` that declares a schedule; a test holds that true.
LANES: tuple[Lane, ...] = (
    Lane(
        "run-pull",
        "Docket refresh",
        "Polls the Supreme Court's docket pages for new filings and orders, and "
        "enriches tracked dockets from CourtListener.",
    ),
    Lane(
        "run-seed",
        "Historical walker",
        "Adds decided petitions from past Terms to the corpus the base rates are read from.",
    ),
    Lane(
        "run-predict",
        "Predict",
        "Runs each model on the events that are owed a forecast.",
    ),
    Lane(
        "run-evaluate",
        "Evaluate",
        "Grades the forecasts on events whose outcome is now known.",
    ),
    Lane(
        "summarize",
        "Case summaries",
        "Writes the plain-language summaries of the predicted cases.",
    ),
    Lane(
        "run-analytics",
        "Boards",
        "Rebuilds the big-case board daily and the metrics roll-ups weekly.",
    ),
    Lane(
        "run-ops",
        "Status report",
        "Checks the committed data and writes this page's snapshot.",
    ),
)

#: How long after a schedule tick a lane may still not have started before it
#: reads as late. GitHub starts scheduled runs late under load, often by tens of
#: minutes, so a tighter bound would report the platform's delay as an outage.
LATE_GRACE = timedelta(hours=2)

#: How far back a schedule tick is looked for. A week covers every weekly cron.
_TICK_LOOKBACK_DAYS = 8

#: The conclusions that mean a run executed and did not succeed. A cancelled run
#: is left out: the corpus writers share one concurrency group, so a run that
#: was superseded in the queue ends `cancelled` with nothing wrong.
_FAILED = frozenset({"failure", "timed_out", "startup_failure"})

_DEFAULT_BRANCH = "main"

_WEEKDAYS = ("Sundays", "Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays")


@dataclass(frozen=True)
class Cron:
    """The minute, hour and weekday sets of one five-field cron expression.

    Day-of-month and month must be ``*``: no workflow here schedules by them, and
    a field this parser does not model is refused rather than read as ``*``.
    """

    minutes: frozenset[int]
    hours: frozenset[int]
    weekdays: frozenset[int] | None  # 0 = Sunday; None = every day


def _field(text: str, low: int, high: int) -> frozenset[int]:
    """One cron field: ``*``, numbers, ``a-b`` ranges and ``/n`` steps, comma-listed."""
    values: set[int] = set()
    for part in text.split(","):
        base, _, step_text = part.partition("/")
        step = int(step_text) if step_text else 1
        if base == "*":
            start, stop = low, high
        elif "-" in base:
            first, last = base.split("-", 1)
            start, stop = int(first), int(last)
        else:
            start = int(base)
            stop = high if step_text else start
        if not low <= start <= stop <= high or step < 1:
            raise ValueError(f"cron field {text!r} is outside {low}-{high}")
        values.update(range(start, stop + 1, step))
    return frozenset(values)


def parse_cron(expression: str) -> Cron:
    """Parse a GitHub Actions schedule cron (UTC, five fields)."""
    fields = expression.split()
    if len(fields) != 5:
        raise ValueError(f"cron {expression!r} does not have five fields")
    minute, hour, day, month, weekday = fields
    if day != "*" or month != "*":
        raise ValueError(f"cron {expression!r} schedules by day of month or month")
    days = _field(weekday, 0, 7)
    return Cron(
        minutes=_field(minute, 0, 59),
        hours=_field(hour, 0, 23),
        weekdays=None if weekday == "*" else frozenset(d % 7 for d in days),
    )


def last_tick(crons: Sequence[Cron], at_or_before: datetime) -> datetime | None:
    """The newest instant at or before ``at_or_before`` that any of ``crons`` fires."""
    newest: datetime | None = None
    for offset in range(_TICK_LOOKBACK_DAYS + 1):
        day = (at_or_before - timedelta(days=offset)).date()
        sunday_first = (day.weekday() + 1) % 7
        for cron in crons:
            if cron.weekdays is not None and sunday_first not in cron.weekdays:
                continue
            for hour in cron.hours:
                for minute in cron.minutes:
                    tick = datetime(day.year, day.month, day.day, hour, minute, tzinfo=UTC)
                    if tick <= at_or_before and (newest is None or tick > newest):
                        newest = tick
        if newest is not None:
            return newest
    return None


def workflow_crons(workflows_root: Path, stem: str) -> list[str]:
    """The ``on.schedule`` crons the workflow file declares, in file order."""
    loaded = yaml.safe_load((workflows_root / f"{stem}.yml").read_text())
    # PyYAML reads a bare `on:` key as the boolean True.
    triggers = loaded.get("on", loaded.get(True)) if isinstance(loaded, dict) else None
    schedule = triggers.get("schedule") if isinstance(triggers, dict) else None
    if not isinstance(schedule, list):
        return []
    return [str(item["cron"]) for item in schedule if isinstance(item, dict) and "cron" in item]


def _joined(items: Sequence[str]) -> str:
    """``a``, ``a and b``, ``a, b and c``."""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + f" and {items[-1]}"


def describe_schedule(crons: Sequence[str]) -> str:
    """The schedule in words: the daily times, then any weekly extra."""
    parsed = [parse_cron(expression) for expression in crons]
    daily = sorted(
        (hour, minute)
        for cron in parsed
        if cron.weekdays is None
        for hour in cron.hours
        for minute in cron.minutes
    )
    parts: list[str] = []
    if len(daily) > 4:
        parts.append(f"{len(daily)} times a day")
    elif daily:
        parts.append(f"daily at {_joined([f'{h:02d}:{m:02d}' for h, m in daily])} UTC")
    weekly: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for cron in parsed:
        if cron.weekdays is not None:
            weekly.setdefault(tuple(sorted(cron.weekdays)), []).extend(
                (hour, minute) for hour in cron.hours for minute in cron.minutes
            )
    for weekdays, times in weekly.items():
        days = " and ".join(_WEEKDAYS[d] for d in weekdays)
        at = _joined([f"{hour:02d}:{minute:02d}" for hour, minute in sorted(times)])
        parts.append(f"{days} at {at} UTC")
    return ", plus ".join(parts) if parts else "no schedule"


def _stamp(run: Mapping[str, object]) -> datetime | None:
    created = run.get("createdAt")
    if not isinstance(created, str):
        return None
    parsed = parse_iso(created)
    if parsed is None:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _on_default_branch(run: Mapping[str, object]) -> bool:
    """A run of the production pipeline. A run list without branches counts as one."""
    branch = run.get("headBranch")
    return branch is None or branch == _DEFAULT_BRANCH


def _conclusive(run: Mapping[str, object]) -> bool:
    if run.get("status") != "completed":
        return False
    conclusion = run.get("conclusion")
    return conclusion == "success" or conclusion in _FAILED


def lane_status(
    lane: Lane,
    *,
    crons: Sequence[str],
    runs: Iterable[Mapping[str, object]],
    generated_at: datetime,
) -> StatusLane:
    """Judge one lane against its own schedule and its own run history."""
    own = sorted(
        (
            (stamp, run)
            for run in runs
            if run.get("workflowName") == lane.stem
            and _on_default_branch(run)
            and (stamp := _stamp(run)) is not None
            and stamp <= generated_at
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )
    started = own[0][0] if own else None
    conclusive = [(stamp, run) for stamp, run in own if _conclusive(run)]
    week = [run for stamp, run in conclusive if stamp > generated_at - timedelta(days=7)]
    expected = last_tick([parse_cron(c) for c in crons], generated_at - LATE_GRACE)
    last = conclusive[0] if conclusive else None
    state: LaneState
    if started is None:
        state = "no-runs"
    elif expected is not None and started < expected:
        state = "late"
    elif last is not None and last[1].get("conclusion") in _FAILED:
        state = "failing"
    else:
        state = "up"
    return StatusLane(
        lane=lane.stem,
        label=lane.label,
        what=lane.what,
        schedule=describe_schedule(crons),
        state=state,
        last_started_at=started,
        last_conclusion=str(last[1].get("conclusion")) if last else None,
        last_concluded_at=last[0] if last else None,
        expected_since=expected,
        runs_7d=len(week),
        successes_7d=sum(1 for run in week if run.get("conclusion") == "success"),
    )


def build_lanes(
    runs: Sequence[Mapping[str, object]], *, workflows_root: Path, generated_at: datetime
) -> list[StatusLane]:
    """Every lane in :data:`LANES`, each judged against its workflow's schedule."""
    return [
        lane_status(
            lane,
            crons=workflow_crons(workflows_root, lane.stem),
            runs=runs,
            generated_at=generated_at,
        )
        for lane in LANES
    ]


def _production(window: ProducedWindow, key: Literal["7d", "30d", "term"]) -> StatusProduction:
    census = window.census
    end = window.window_end
    return StatusProduction(
        window=key,
        start=window.window_start or end or date.min,
        end=end or date.min,
        days=census.window_days,
        term=window.term,
        cells=census.cells,
        events=census.events,
        by_stage=[
            StatusStageCells(role=row.role, stage=row.stage, cells=row.cells) for row in census.rows
        ],
    )


def build_production(production: WeeklyProduction) -> list[StatusProduction]:
    """The three windows, without the spend the digest prints beside them."""
    return [
        _production(production.week, "7d"),
        _production(production.month, "30d"),
        _production(production.term, "term"),
    ]


def build_coverage(
    report: OpsReport, *, public_cases: int, frontier: LiveFrontier | None
) -> StatusCoverage:
    """The ledger's size from the report's census, and the watchlist's readiness."""
    substance = report.substance
    cells = substance.cells if substance is not None else None
    live = frontier if frontier is not None and not frontier.skipped else None
    corpus = report.data_health.corpus if report.data_health is not None else None
    return StatusCoverage(
        public_cases=public_cases,
        events_predicted=cells.events_predicted if cells else 0,
        predicted_resolved=cells.predicted_resolved if cells else 0,
        predictions=cells.predictions if cells else 0,
        evaluations_forward=cells.evaluations_forward if cells else 0,
        frontier_as_of=live.generated_on if live else None,
        watchlist=live.watchlist if live else None,
        documents_provisioned=live.documents_provisioned if live else None,
        next_conference=live.next_conference if live else None,
        next_conference_petitions=live.next_conference_petitions if live else None,
        corpus_dockets=corpus.corpus_rows if corpus is not None and not corpus.skipped else None,
    )


_RETROSPECTIVE = (
    "Retrospective: every outcome was public before the run, so this measures recall "
    "of known history, never foresight. It is an iteration instrument, and nothing "
    "here is a claimable performance figure."
)


def _vintage(vintaged: Vintaged[object]) -> date | None:
    return date.fromisoformat(vintaged.vintage) if vintaged.vintage else None


def _replay_row(predictor_id: str, label: str, score: BacktestCourtScore) -> list[str]:
    return [
        predictor_id,
        label,
        f"{score.events_scored:,}",
        _pct(score.accuracy),
        _pct(score.always_denied_accuracy),
        _signed_pct(score.lift_over_always_denied),
        _brier(score.mean_brier_score),
    ]


def _historical_replay(vintaged: Vintaged[Backtest]) -> StatusBacktest | None:
    board = vintaged.value
    if board is None or not board.entries:
        return None
    rows: list[list[str]] = []
    for entry in board.entries:
        classes = [s for s in entry.docket_classes if s.court == _BACKTEST_HEADLINE_COURT]
        if classes:
            rows += [
                _replay_row(
                    entry.predictor_id,
                    f"SCOTUS {_DOCKET_CLASS_LABELS[s.docket_class]}",
                    s,
                )
                for s in classes
            ]
        else:
            rows += [
                _replay_row(entry.predictor_id, "SCOTUS", court)
                for court in entry.courts
                if court.court == _BACKTEST_HEADLINE_COURT
            ]
        rows.append(
            [
                entry.predictor_id,
                "All courts pooled",
                f"{entry.events_scored:,}",
                _pct(entry.accuracy),
                _pct(entry.always_denied_accuracy),
                _signed_pct(entry.lift_over_always_denied),
                _brier(entry.mean_brier_score),
            ]
        )
    split = any(entry.docket_classes for entry in board.entries)
    mixed = (
        ""
        if split
        else " The SCOTUS row mixes cert petitions with emergency applications, so its "
        "floor is neither population's."
    )
    return StatusBacktest(
        key="historical-replay",
        name="Historical replay",
        artifact="metrics/backtest.json",
        vintage=_vintage(vintaged),
        summary=f"{board.predictors_evaluated} simple baseline predictor(s) replayed over "
        f"{board.events_scored:,} resolved events in the corpus. No model runs here.",
        table=StatusTable(
            columns=[
                "Predictor",
                "Docket",
                "Events",
                "Accuracy",
                "Always-deny floor",
                "Lift",
                "Mean Brier",
            ],
            rows=rows,
        ),
        reading=f"{_RETROSPECTIVE} Read each lift only against its own row's floor.{mixed} "
        "The pooled row mixes in courts this pipeline does not predict.",
    )


def _cert(vintaged: Vintaged[CertBacktest]) -> StatusBacktest | None:
    report = vintaged.value
    if report is None or not report.entries:
        return None
    floor = report.always_not_granted_accuracy
    engines = sum(1 for entry in report.entries if entry.engine is not None)
    baselines = len(report.entries) - engines
    dispatch = report.provenance.dispatch if report.provenance is not None else None
    draw = (" drawn at random" if dispatch is not None and dispatch.spread else "") + (
        " from paid petitions" if dispatch is not None and dispatch.scope == "paid" else ""
    )
    # A report written before the granted-or-not headline carries the exact-
    # disposition axis alone, and is read on that axis rather than shown blank.
    granted_axis = floor is not None
    rows = [
        [
            entry.predictor_id,
            "model" if entry.engine is not None else "baseline",
            f"{entry.events_scored:,}",
            _pct(entry.granted_accuracy if granted_axis else entry.accuracy),
            _signed_pct(
                entry.granted_lift_over_always_denied
                if granted_axis
                else entry.lift_over_always_denied
            ),
            _brier(entry.mean_brier_score),
        ]
        for entry in report.entries
    ]
    accuracy = "Granted-or-not accuracy" if granted_axis else "Exact-disposition accuracy"
    return StatusBacktest(
        key="cert",
        name="Cert back-test",
        artifact="metrics/cert-backtest.json",
        vintage=_vintage(vintaged),
        summary=f"{engines} model(s) and {baselines} reference baseline(s) replayed over "
        f"{report.events_scored:,} decided cert petitions{draw}, with each outcome hidden. "
        + (
            f"Always-deny scores {_pct(floor)} on granted or not over this sample."
            if floor is not None
            else f"Always-deny scores {_pct(report.always_denied_accuracy)} on exact "
            "disposition over this sample."
        ),
        table=StatusTable(
            columns=["Predictor", "Kind", "Petitions", accuracy, "Lift", "Mean Brier"],
            rows=rows,
        ),
        reading=f"{_RETROSPECTIVE} The floor is this sample's own denial share, so a "
        "different draw is scored against a different floor and is not comparable. "
        "No evaluator runs here, so a cell that saw its own outcome stays in and can only "
        "flatter its model.",
    )


def _merits(vintaged: Vintaged[MeritsBacktest]) -> StatusBacktest | None:
    report = vintaged.value
    if report is None or not report.entries:
        return None
    rows = [
        [
            entry.predictor_id,
            moment.moment,
            f"{moment.events_scored:,}",
            _pct(moment.accuracy),
            _pct(moment.majority_accuracy),
            "—" if moment.brier_skill is None else f"{moment.brier_skill:+.2f}",
        ]
        for entry in report.entries
        for moment in entry.moments
    ]
    terms = ", ".join(f"OT{term}" for term in report.dispatch.terms) if report.dispatch else ""
    return StatusBacktest(
        key="merits",
        name="Merits back-test",
        artifact="metrics/merits-backtest.json",
        vintage=_vintage(vintaged),
        summary=f"{len(report.entries)} model(s) replayed over {report.paired_cases:,} "
        f"decided argued case(s){f' from {terms}' if terms else ''}, at the grant and "
        "briefing moments, forecasting whether the judgment below is disturbed.",
        table=StatusTable(
            columns=["Predictor", "Moment", "Cases", "Accuracy", "Majority floor", "Brier skill"],
            rows=rows,
        ),
        reading=f"{_RETROSPECTIVE} Read accuracy against the majority floor beside it. "
        "Brier skill is against a base rate that could have been known at each case's "
        "cutoff; a positive figure beats it. Cases are fenced or set aside in ways that "
        "can track their outcome, so every set here is a selected one.",
    )


def _salience(vintaged: Vintaged[SalienceReplay], in_force: str) -> StatusBacktest | None:
    replay = vintaged.value
    if replay is None:
        return None
    version = replay.salience_version
    terms = ", ".join(f"OT{t}" for t in replay.terms)
    stale = (
        ""
        if version == in_force
        else f" It was produced under {version} while {in_force} is the scorer in force, "
        "so it describes that version and is not a current reading of the gate."
    )
    return StatusBacktest(
        key="salience-replay",
        name="Salience-gate replay",
        artifact="metrics/salience-replay.json",
        vintage=_vintage(vintaged),
        summary=f"The gate that picks which petitions are predicted, replayed over {terms} "
        f"under {len(replay.policies)} cutoff policies.",
        reading=f"{_RETROSPECTIVE}{stale}",
    )


def build_backtests(
    analytics: WeeklyAnalytics, merits: Vintaged[MeritsBacktest]
) -> list[StatusBacktest]:
    """Each landed, non-empty back-test's headline; one never landed is left out."""
    built = [
        _historical_replay(analytics.backtest),
        _cert(analytics.cert_backtest),
        _merits(merits),
        _salience(analytics.salience_replay, analytics.salience_version_in_force),
    ]
    return [item for item in built if item is not None]


def build_status(  # noqa: PLR0913 - one keyword per independent feed
    *,
    report: OpsReport,
    runs: Sequence[Mapping[str, object]],
    workflows_root: Path,
    production: WeeklyProduction,
    analytics: WeeklyAnalytics,
    merits: Vintaged[MeritsBacktest],
    frontier: LiveFrontier | None,
    public_cases: int,
    source_sha: str | None,
) -> PublicStatus:
    """The whole snapshot, anchored on the report's own ``generated_at``."""
    when = parse_iso(report.generated_at)
    if when is None:
        raise ValueError(f"report generated_at {report.generated_at!r} is not ISO-8601")
    when = when if when.tzinfo is not None else when.replace(tzinfo=UTC)
    return PublicStatus(
        generated_at=when,
        source_sha=source_sha,
        data_ok=report.data_health.ok if report.data_health is not None else None,
        lanes=build_lanes(runs, workflows_root=workflows_root, generated_at=when),
        production=build_production(production),
        coverage=build_coverage(report, public_cases=public_cases, frontier=frontier),
        backtests=build_backtests(analytics, merits),
    )
