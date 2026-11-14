"""The forecast-coverage verdict: every coverage check read once, as one answer.

Three read-only checks each say something different about whether the forecast
ledger covers what it should:

- the **missed-forecast monitor** (:mod:`fedcourtsai.pipeline.missed`): events
  the pipeline owed a forecast and resolved without one, and decided events on
  a selected row with no outcome record;
- the **unforecast-outcomes census** (:mod:`fedcourtsai.pipeline.unforecast`):
  grants and application rulings selection left out;
- the **federal-label cross-check** (:mod:`fedcourtsai.pipeline.federal_label`):
  pending petitions a looser reading places federal, and, when handed the
  Solicitor General's posted cert petitions, the ones on that listing the
  caption rule does not band ``federal``.

Each runs on its own and prints its own report. This module runs all three
over one corpus read, adds the cells the predict attempt cap has given up on
while their event is still open (:func:`attempt_capped_cells`), and folds them
into one verdict: ``ok`` or not, the alarms
by name, and a flat block of counts a caller can keep as a series. The
verdict is what a scheduled caller publishes and what an alarm issue is
latched on, so the monitor's findings outlive the run that computed them.

**What alarms.** Every event the monitor classes ``missed``; every other
decided event on a selected row still without an outcome record
:data:`NO_OUTCOME_GRACE_DAYS` days after its decision date (the outcome writer
converges within a window or two, so a younger gap is the writer's lag; a row
with no decision date at all is counted, since nothing dates its grace
period); each alarm the two censuses raise; and every attempt-capped cell of
an open event. One event raises one alarm from the monitor. The monitor is read over
:data:`MISSED_WINDOW_DAYS` rather than its per-round week, so a resolution
recorded late is still seen.

Reads the corpus index and the committed ledger; writes nothing itself.

**The alarm issue.** :func:`latch` keeps one long-lived issue,
:data:`ISSUE_TITLE` under the non-triggering :data:`ISSUE_LABEL` label, to
match a verdict (:mod:`fedcourtsai.alarm_issue`). A missed forecast cannot be
repaired once its event has resolved, so it stays an alarm until it ages out
of the monitor's window and the issue is often open for weeks at a time.
Rewriting an issue body notifies nobody, so a refresh that brings an alarm the
issue did not already name also comments, naming the new ones.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from .. import alarm_issue, corpus, ids
from ..agent_feedback import GhRunner, _gh
from ..matrix import event_has_predictions
from ..registry import enabled_predictors
from .federal_label import FederalLabelReport, SgPetitionListing, federal_label_check
from .missed import DateSource, DeclineReason, scan_predictionless_resolutions
from .unforecast import UnforecastReport, unforecast_outcomes

#: The alarm issue: one long-lived issue under a label that starts nothing.
ISSUE_TITLE: Final = "Forecast coverage failing"
ISSUE_LABEL: Final = "forecast-coverage"
ALARM_ISSUE: Final = alarm_issue.AlarmIssue(
    title=ISSUE_TITLE,
    label=ISSUE_LABEL,
    label_description="Long-lived forecast coverage alarm (run-analytics)",
)

#: The most alarms an issue body or a comment lists by name; the rest are
#: counted. A long predict outage can owe hundreds of forecasts, and a body
#: over the size an issue may have would fail the refresh on the worst day.
ALARMS_LISTED: Final = 150
#: The longest issue body, in characters, with room for the note that says it
#: was cut.
ALARM_BODY_CHARS: Final = 60_000

#: How far back the verdict reads the missed-forecast monitor.
MISSED_WINDOW_DAYS = 35

#: How far back the verdict reads the unforecast-outcomes census.
UNFORECAST_WINDOW_DAYS = 14

#: A decided event on a selected row may lack its outcome record this long
#: before the gap is an alarm.
NO_OUTCOME_GRACE_DAYS = 3


class CoverageAlarm(BaseModel):
    """One alarm condition, attributed to the check that raised it."""

    model_config = ConfigDict(extra="forbid")

    check: Literal[
        "missed_forecast",
        "no_outcome_record",
        "unforecast_outcomes",
        "federal_label",
        "sg_petition_list",
        "attempt_capped",
    ]
    subject: str = Field(description="The case and event, or the docket, the alarm names")
    detail: str


class AttemptCappedCell(BaseModel):
    """One (predictor, event) cell the predict sweep has stopped re-queuing."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    event_id: str
    predictor_id: str
    failures: int = Field(ge=1, description="Committed `attempt.json` failure facts on the cell")


class CoverageVerdict(BaseModel):
    """The forecast-coverage verdict for one day."""

    model_config = ConfigDict(extra="forbid")

    as_of: date
    ok: bool = Field(description="True when no alarm holds")
    alarms: list[CoverageAlarm]
    counts: dict[str, int | float | None] = Field(
        description="The figures worth keeping as a series, one flat block"
    )
    missed_since: date
    missed: list[dict[str, object]] = Field(
        description="The monitor's `missed` events over the window, as it reports them"
    )
    no_outcome_on_selected_row: list[dict[str, object]] = Field(
        description="Decided events on a selected row with no outcome record, over the window"
    )
    unforecast: UnforecastReport
    federal_label: FederalLabelReport
    attempt_capped: list[AttemptCappedCell] = Field(
        default_factory=list,
        description="Cells of an open event that reached the predict attempt cap with "
        "no committed prediction",
    )


def attempt_capped_cells(
    conn: corpus.ReadConnection,
    data_root: Path,
    predictor_ids: Sequence[str],
    *,
    max_attempts: int,
) -> list[AttemptCappedCell]:
    """The cells the attempt cap has given up on while their event is still open.

    A cell of an enabled predictor holding ``max_attempts`` or more committed
    failure facts (:func:`fedcourtsai.matrix.cell_failure_count`) is no longer
    re-queued by the selection sweep. Where that predictor has no committed
    prediction on the event, and the event is open, a forecast is owed, will
    not be retried, and can still be made. Open is read both ways: the event
    has no ``outcome.json``, and the corpus holds it unresolved on a row that
    is not latched out of predict scope, so an event already decided whose
    outcome record lags is left to the monitor's own alarms. The
    missed-forecast monitor reports the same cell only once the event
    resolves. Not listed: a reopened event whose capped predictor holds a
    prediction that no board counts, which the reopen deriver gives up on by
    a different test. ``max_attempts`` of 0 is the cap switched off, and
    lists nothing.
    """
    cases_dir = data_root / "cases"
    if max_attempts <= 0 or not cases_dir.exists():
        return []
    enabled = set(predictor_ids)
    # <cases>/<court>/<docket>/events/<event>/predictions/<predictor>/<run>/attempt.json
    failures: Counter[tuple[Path, str]] = Counter()
    for path in cases_dir.glob("*/*/events/*/predictions/*/*/attempt.json"):
        # A docket directory is the case's numeric id; anything else is not a cell.
        if path.parents[1].name in enabled and path.parents[5].name.isdigit():
            failures[(path.parents[3], path.parents[1].name)] += 1
    capped: list[AttemptCappedCell] = []
    for (event_dir, predictor_id), count in failures.items():
        if count < max_attempts or (event_dir / "outcome.json").exists():
            continue
        court, docket = event_dir.parents[2].name, int(event_dir.parents[1].name)
        if event_has_predictions(
            data_root, court, docket, event_dir.name, predictor_id=predictor_id
        ):
            continue
        case_id = ids.case_id(court, docket)
        if not _open_in_corpus(conn, case_id, event_dir.name):
            continue
        capped.append(
            AttemptCappedCell(
                case_id=case_id,
                event_id=event_dir.name,
                predictor_id=predictor_id,
                failures=count,
            )
        )
    capped.sort(key=lambda c: (c.case_id, c.event_id, c.predictor_id))
    return capped


def _open_in_corpus(conn: corpus.ReadConnection, case_id: str, event_id: str) -> bool:
    """Whether the corpus holds the event unresolved on a row still in predict scope."""
    row = corpus.get_row(conn, case_id)
    if row is None or row.predict_excluded:
        return False
    return any(
        e.event_id == event_id and not e.resolved for e in corpus.events_for_case(conn, case_id)
    )


def coverage_verdict(
    conn: corpus.ReadConnection,
    data_root: Path,
    predictors_path: Path,
    *,
    today: date,
    max_attempts: int = 0,
    sg_listing: SgPetitionListing | None = None,
) -> CoverageVerdict:
    """Run the coverage checks as of ``today`` and fold them into one verdict.

    ``max_attempts`` is the predict sweep's per-cell attempt cap, which the
    attempt-capped list is read against; ``sg_listing`` hands the federal-label
    cross-check the Solicitor General's posted cert petitions.
    """
    missed_since = today - timedelta(days=MISSED_WINDOW_DAYS)
    monitor = scan_predictionless_resolutions(
        conn, data_root, predictors_path, since=missed_since, until=today
    )
    unforecast = unforecast_outcomes(
        conn, data_root, since=today - timedelta(days=UNFORECAST_WINDOW_DAYS), until=today
    )
    label = federal_label_check(conn, today=today, sg_listing=sg_listing)
    capped = attempt_capped_cells(
        conn,
        data_root,
        [p.id for p in enabled_predictors(predictors_path)],
        max_attempts=max_attempts,
    )

    alarms = [
        CoverageAlarm(
            check="missed_forecast",
            subject=f"{e.case_id} {e.event_id}",
            detail=f"resolved {e.resolved_at.isoformat()}, {e.reason}"
            + (f": {e.detail}" if e.detail else ""),
        )
        for e in monitor.missed
    ]
    grace = today - timedelta(days=NO_OUTCOME_GRACE_DAYS)
    missed_keys = {(e.case_id, e.event_id) for e in monitor.missed}
    unrecorded = [u for u in monitor.no_outcome_record if u.selected]
    # A row dated only from its newest observation has no decision date: the
    # date moves forward with every poll, so the grace period never runs out
    # on it. Those, and the events no source can date, are counted, not alarmed.
    undatable = [u for u in unrecorded if u.date_source is DateSource.last_observed]
    alarms += [
        CoverageAlarm(
            check="no_outcome_record",
            subject=f"{u.case_id} {u.event_id}",
            detail=f"decided {u.resolved_at.isoformat()} on a selected row, no outcome.json",
        )
        for u in unrecorded
        if u.resolved_at is not None
        and u.resolved_at <= grace
        and u.date_source is not DateSource.last_observed
        and (u.case_id, u.event_id) not in missed_keys
    ]
    alarms += [
        CoverageAlarm(
            check="unforecast_outcomes",
            subject=a.split(":", 1)[0] if ":" in a else "Term-to-date grant recall",
            detail=a,
        )
        for a in unforecast.alarms
    ]
    sg = label.sg_petition_list
    sg_alarms = set(sg.alarms) if sg else set()
    alarms += [
        CoverageAlarm(
            check="sg_petition_list" if a in sg_alarms else "federal_label",
            subject=a.split(":", 1)[0],
            detail=a,
        )
        for a in label.alarms
    ]
    alarms += [
        CoverageAlarm(
            check="attempt_capped",
            subject=f"{c.case_id} {c.event_id} {c.predictor_id}",
            detail=f"recorded failed {c.failures} times, at the attempt cap "
            f"of {max_attempts}: no committed prediction, no outcome yet, and no retry coming",
        )
        for c in capped
    ]
    counts: dict[str, int | float | None] = {
        "missed_events": len(monitor.missed),
        "declined_events": len(monitor.declined),
        "declined_not_funded_events": sum(
            e.reason == DeclineReason.not_funded for e in monitor.declined
        ),
        "no_outcome_record_on_selected_row_events": len(unrecorded),
        "no_outcome_record_undatable_on_selected_row_events": len(undatable)
        + len(monitor.undated_selected),
        "grant_outcomes_window": unforecast.window.outcomes,
        "grant_forecast_window": unforecast.window.forecast,
        "grant_outcomes_term_to_date": unforecast.term_to_date.outcomes,
        "grant_forecast_term_to_date": unforecast.term_to_date.forecast,
        "grant_reachable_outcomes_term_to_date": unforecast.term_to_date.reachable_outcomes,
        "grant_reachable_recall_term_to_date": unforecast.term_to_date.reachable_recall,
        "cert_unforecast": len(unforecast.cert_unforecast),
        "interim_outcomes": unforecast.interim_outcomes,
        "interim_unforecast": len(unforecast.interim_unforecast),
        "pending_paid_petitions": label.pending,
        "pending_federal_band": label.federal,
        "federal_label_flagged": len(label.flagged),
        "sg_listed_petitions": sg.listed if sg and sg.read else None,
        "sg_listed_pending": sg.pending if sg and sg.read else None,
        "sg_listed_not_federal": len(sg.not_federal) if sg and sg.read else None,
        "attempt_capped_open_cells": len(capped),
    }
    return CoverageVerdict(
        as_of=today,
        ok=not alarms,
        alarms=alarms,
        counts=counts,
        missed_since=missed_since,
        missed=[e.as_json() for e in monitor.missed],
        no_outcome_on_selected_row=[u.as_json() for u in unrecorded],
        unforecast=unforecast,
        federal_label=label,
        attempt_capped=capped,
    )


def _share(forecast: int, outcomes: int) -> str:
    return f"{forecast} of {outcomes}" + (f" ({forecast / outcomes:.0%})" if outcomes else "")


def _alarm_key(alarm: CoverageAlarm) -> str:
    """How a body names one alarm: its check and its subject, as rendered."""
    return f"**{alarm.check}** `{alarm.subject}`"


def _alarm_line(alarm: CoverageAlarm) -> str:
    return f"- {_alarm_key(alarm)}: {alarm.detail}"


def render_markdown(verdict: CoverageVerdict) -> str:
    """The verdict as the body of its alarm issue: alarms first, then each check's list.

    Identifiers and counts only — case ids, event ids, docket numbers, dates,
    bands — and never a caption or any stored docket text.
    """
    u = verdict.unforecast
    lines = [
        f"Forecast coverage as of {verdict.as_of.isoformat()}: "
        + ("no alarm." if verdict.ok else f"{len(verdict.alarms)} alarm(s)."),
        "",
    ]
    if verdict.alarms:
        lines += ["## Alarms", ""]
        lines += [_alarm_line(a) for a in verdict.alarms[:ALARMS_LISTED]]
        if len(verdict.alarms) > ALARMS_LISTED:
            lines.append(f"- and {len(verdict.alarms) - ALARMS_LISTED} more, not listed.")
        lines.append("")
    lines += [
        "## Grants and application rulings with no forecast",
        "",
        f"Paid grants a forecast preceded, {u.since.isoformat()} to {u.until.isoformat()}: "
        f"{_share(u.window.forecast, u.window.outcomes)}. "
        f"Term to date: {_share(u.term_to_date.forecast, u.term_to_date.outcomes)}, "
        f"{u.term_to_date.reachable_outcomes} reachable. These shares describe selection, "
        "are outcome-selected, and say nothing about any predictor.",
        "",
    ]
    if u.cert_unforecast:
        lines += ["| Docket | Disposition | Resolved | Reason | Band |", "|---|---|---|---|---|"]
        lines += [
            f"| {e.docket_number} | {e.disposition} | {e.resolved_at.isoformat()} "
            f"| {e.reason.value} | {e.band} |"
            for e in u.cert_unforecast
        ]
        lines.append("")
    referred = sum(1 for e in u.interim_unforecast if e.referred_to_court)
    lines += [
        f"Referred or substantive applications resolved: {u.interim_outcomes}; "
        f"{len(u.interim_unforecast)} had no forecast ({referred} of them referred to the Court).",
        "",
        "## Pending petitions a looser reading places federal",
        "",
        f"{verdict.federal_label.pending} pending paid petitions, "
        f"{verdict.federal_label.federal} in the federal band, "
        f"{len(verdict.federal_label.flagged)} flagged.",
        "",
    ]
    lines += [
        f"- {f.docket_number}: band {f.band}, {', '.join(s.value for s in f.signals)}, "
        + ("selected" if f.selected else "not selected")
        for f in verdict.federal_label.flagged
    ]
    if verdict.federal_label.flagged:
        lines.append("")
    sg = verdict.federal_label.sg_petition_list
    if sg is not None and sg.read:
        lines += [
            f"The Solicitor General's listing of its own cert petitions: {sg.listed} docket "
            "numbers on its first page"
            + (f", filed back to {sg.oldest_filed}" if sg.oldest_filed else "")
            + f"; {sg.pending} are "
            f"pending here, {len(sg.not_federal)} outside the federal band.",
            "",
        ]
    elif sg is not None:
        lines += [f"The Solicitor General's listing was not read: {sg.error}.", ""]
    lines += [
        "## Owed forecasts that never landed",
        "",
        f"Since {verdict.missed_since.isoformat()}: {len(verdict.missed)} missed, "
        f"{len(verdict.no_outcome_on_selected_row)} decided on a selected row with no "
        "outcome record (counting those still inside the "
        f"{NO_OUTCOME_GRACE_DAYS}-day grace period).",
        "",
    ]
    if verdict.attempt_capped:
        lines += [
            f"{len(verdict.attempt_capped)} cell(s) of an open event reached the predict "
            "attempt cap with no committed prediction.",
            "",
        ]
    body = "\n".join(lines).rstrip() + "\n"
    if len(body) <= ALARM_BODY_CHARS:
        return body
    kept = body[:ALARM_BODY_CHARS].rsplit("\n", 1)[0]
    return kept + "\n\nCut here to fit an issue; the run's summary carries the whole verdict.\n"


def latch(
    repo: str, verdict: CoverageVerdict, body_path: Path, *, runner: GhRunner | None = None
) -> str:
    """Open, refresh or close the one alarm issue to match ``verdict``; what was done.

    A verdict with an alarm opens the issue or rewrites the open one's body in
    place from ``body_path``; a clean verdict comments on the open issue and
    closes it, and writes nothing where none is open. A refresh also comments
    when the verdict lists an alarm the issue's body did not name before,
    under that check, because the body rewrite alone reaches no one. The
    comment goes first: if the rewrite then fails, the next read comments
    again, where the other order would lose the notice for good.
    """
    runner = runner or _gh
    new: list[CoverageAlarm] = []
    if verdict.alarms:
        numbers = alarm_issue.open_alarm_issues(repo, ALARM_ISSUE, runner)
        if numbers:
            number = str(numbers[0])
            before = runner(["gh", "api", f"repos/{repo}/issues/{number}", "--jq", ".body"])
            new = [a for a in verdict.alarms[:ALARMS_LISTED] if _alarm_key(a) not in before]
            if new:
                runner(
                    [
                        "gh",
                        "issue",
                        "comment",
                        number,
                        "--repo",
                        repo,
                        "--body",
                        f"New as of {verdict.as_of.isoformat()}:\n\n"
                        + "\n".join(_alarm_line(a) for a in new),
                    ]
                )
    done = alarm_issue.latch_issue(
        repo,
        ALARM_ISSUE,
        alarming=bool(verdict.alarms),
        body_path=body_path,
        clear_comment=f"Forecast coverage has no alarm as of {verdict.as_of.isoformat()}: closing.",
        runner=runner,
    )
    return f"{done}, {len(new)} new alarm(s) commented" if new else done
