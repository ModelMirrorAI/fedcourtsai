"""The trial stage's events, opened and resolved by the watchlist pass.

``docs/trial-stage.md`` (*How the stage registers*) gives the rule. After the
watchlist refresh has stored the listed dockets, this pass reads each district
docket with the opener (:mod:`fedcourtsai.pipeline.trial_opener`) and the
resolver (:mod:`fedcourtsai.pipeline.trial_resolver`) and does three things:

- **Opens** the event of a motion that is fully briefed and that the court has
  not ruled on, and the final-disposition event of a listed case that is still
  open. Only a moment that is switched on is written
  (:class:`~fedcourtsai.pipeline.moments.TrialMomentSpec`); for a moment that
  is not, the pass reports what it would open and writes nothing. An event
  opens no earlier than the day its moment was switched on.
- **Resolves** an event it wrote, when the resolver reads the ruling or a
  maintainer has recorded it (:mod:`fedcourtsai.trial_adjudications`): the
  outcome is written beside the event and the event is closed.
- **Lists for triage** an event it wrote whose docket has moved on in a way
  the resolver cannot read. Nothing is written for it and it stays open.

A motion the court ruled on before the pass first read it opens nothing: its
outcome already exists, so no forecast of it could be a forward one.

The planning half (:func:`plan_docket`) is pure; :func:`run_pass` reads the
corpus and writes through the two paths every other event uses
(:func:`~fedcourtsai.pipeline.outcome.persist_moment_events` and
:func:`~fedcourtsai.pipeline.outcome.record_outcomes`), so a re-run can
neither duplicate an event nor reopen or overwrite a resolved one.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .. import corpus, ids
from ..ai_watchlist import AiWatchlist
from ..paths import CasePaths
from ..schemas import (
    TRIAL_JUDGMENTS_FOR_PLAINTIFF,
    TRIAL_RULINGS_GRANTED,
    Disposition,
    Moment,
    Outcome,
)
from ..trial_adjudications import Adjudication
from . import moments, trial_opener
from . import trial_resolver as resolver
from .ai_candidates import DISTRICT_COURT
from .outcome import Resolution, persist_moment_events, record_outcomes
from .trial_opener import DistrictRule, LocalRule, Opening
from .trial_resolver import JudgmentResolution, MotionResolution, Unresolved


@dataclass(frozen=True)
class Triage:
    """An open event the pass could not resolve, and why."""

    case_id: str
    event_id: str
    reason: str
    #: The numbers of the docket entries weighed.
    entries: tuple[int, ...] = ()


@dataclass
class DocketPlan:
    """What the pass does on one docket."""

    case_id: str
    #: Events to write: their moment is switched on.
    opens: list[corpus.CorpusEvent] = field(default_factory=list)
    #: Events the pass would write were their moment switched on.
    would_open: list[corpus.CorpusEvent] = field(default_factory=list)
    outcomes: dict[str, Outcome] = field(default_factory=dict)
    triage: list[Triage] = field(default_factory=list)
    #: Motions the opener reads as open that a later entry may already rule
    #: on: no event is written, whatever the switch says.
    held_ruled: list[Triage] = field(default_factory=list)


def _source(entry_number: int | None, *, adjudicated: bool = False) -> str:
    cited = f"docket entry {entry_number}" if entry_number is not None else "docket entry"
    return f"{cited} (adjudicated)" if adjudicated else cited


def _motion_outcome(
    case_id: str,
    event_id: str,
    *,
    ruling: str,
    leave: str | None,
    resolved_at: date,
    source: str,
) -> Outcome:
    return Outcome(
        case_id=case_id,
        event_id=event_id,
        resolved_at=resolved_at,
        actual_disposition=Disposition.other,
        actual_granted=int(ruling in TRIAL_RULINGS_GRANTED),
        trial_ruling=ruling,
        trial_leave=leave,
        source=source,
    )


def _judgment_outcome(
    case_id: str, event_id: str, *, judgment: str, resolved_at: date, source: str
) -> Outcome:
    return Outcome(
        case_id=case_id,
        event_id=event_id,
        resolved_at=resolved_at,
        actual_disposition=Disposition.other,
        actual_granted=int(judgment in TRIAL_JUDGMENTS_FOR_PLAINTIFF),
        trial_judgment=judgment,
        source=source,
    )


def _adjudicated_outcome(row: Adjudication) -> Outcome:
    spec = moments.trial_spec_for(row.event_id)
    assert spec is not None  # the list's own check
    source = _source(row.entry_number, adjudicated=True)
    if spec.per_motion:
        return _motion_outcome(
            row.case_id,
            row.event_id,
            ruling=row.result,
            leave=row.leave,
            resolved_at=row.resolved_at,
            source=source,
        )
    return _judgment_outcome(
        row.case_id, row.event_id, judgment=row.result, resolved_at=row.resolved_at, source=source
    )


def _event(
    case_id: str,
    title: str,
    moment: Moment,
    *,
    entry_number: int | None,
    opened_at: date,
    docket_entry_id: int | None = None,
) -> corpus.CorpusEvent:
    spec = moments.trial_spec(moment)
    return corpus.CorpusEvent(
        event_id=moments.trial_event_id(moment, entry_number),
        case_id=case_id,
        court=case_id.partition("/")[0],
        kind=spec.kind,
        stage=spec.stage,
        moment=spec.moment,
        title=title or case_id,
        description=spec.description,
        docket_entry_id=docket_entry_id,
        opened_at=opened_at,
        decision_target=spec.decision_target,
        resolved=False,
    )


def _place(plan: DocketPlan, event: corpus.CorpusEvent, opens_on: date, today: date) -> None:
    """File a new event under the list its moment's switch puts it on.

    A moment whose switch-on day has not come is not switched on yet.
    """
    assert event.moment is not None  # `_event` sets it
    spec = moments.trial_spec(event.moment)
    if spec.opens_from is None or not moments.trial_switched_on(event.event_id, today):
        plan.would_open.append(event.model_copy(update={"opened_at": opens_on}))
    else:
        plan.opens.append(event.model_copy(update={"opened_at": max(opens_on, spec.opens_from)}))


def _settle(
    plan: DocketPlan,
    stored: corpus.CorpusEvent,
    *,
    adjudication: Adjudication | None,
    resolution: MotionResolution | JudgmentResolution | Unresolved | None,
    today: date,
    missing: str | None = None,
) -> None:
    """Resolve one open stored event, send it to triage, or leave it open."""
    case_id, event_id = stored.case_id, stored.event_id
    outcome: Outcome | None = None
    if adjudication is not None and adjudication.resolved_at > today:
        plan.triage.append(
            Triage(
                case_id,
                event_id,
                f"its adjudication is dated {adjudication.resolved_at}, after the day read",
                (adjudication.entry_number,),
            )
        )
        return
    if adjudication is not None:
        outcome = _adjudicated_outcome(adjudication)
    elif missing is not None:
        plan.triage.append(Triage(case_id, event_id, missing))
        return
    elif isinstance(resolution, Unresolved):
        plan.triage.append(
            Triage(
                case_id,
                event_id,
                resolution.reason,
                tuple(c.entry_number for c in resolution.candidates if c.entry_number is not None),
            )
        )
        return
    elif resolution is not None:
        cited = resolution.cited
        if cited.date_filed is None:
            entries = () if cited.entry_number is None else (cited.entry_number,)
            plan.triage.append(
                Triage(case_id, event_id, "the entry the resolver read is undated", entries)
            )
            return
        source = _source(cited.entry_number)
        if isinstance(resolution, MotionResolution):
            outcome = _motion_outcome(
                case_id,
                event_id,
                ruling=resolution.ruling.value,
                leave=None if resolution.leave is None else resolution.leave.value,
                resolved_at=cited.date_filed,
                source=source,
            )
        else:
            outcome = _judgment_outcome(
                case_id,
                event_id,
                judgment=resolution.outcome.value,
                resolved_at=cited.date_filed,
                source=source,
            )
    if outcome is None:
        return
    if stored.opened_at is not None and outcome.resolved_at < stored.opened_at:
        plan.triage.append(
            Triage(
                case_id,
                event_id,
                f"the result is dated {outcome.resolved_at}, before the event opened "
                f"on {stored.opened_at}",
            )
        )
        return
    plan.outcomes[event_id] = outcome


def plan_docket(  # noqa: PLR0913 - one docket and everything read beside it
    case_id: str,
    title: str,
    entries: Sequence[Mapping[str, Any]],
    stored: Mapping[str, corpus.CorpusEvent],
    *,
    today: date,
    local_rule: LocalRule | DistrictRule | None = None,
    lead_owned: frozenset[int] = frozenset(),
    adjudicated: Mapping[tuple[str, str], Adjudication] | None = None,
    judgment: bool = False,
    lead_unread: bool = False,
) -> DocketPlan:
    """What the pass opens, resolves and sends to triage on one docket. Pure.

    ``entries`` are the docket's stored entries and ``stored`` its corpus
    events by id. ``lead_owned`` are the motion entries a lead docket also
    holds, whose events are the lead's. ``judgment`` says the docket is a
    listed case's own, the one docket whose final disposition is an event.
    ``lead_unread`` says the docket is a member whose lead docket is not
    stored: no motion opens on it until the lead can be read, since the pass
    cannot yet say which of its motions are the lead's.
    """
    settled = adjudicated or {}
    plan = DocketPlan(case_id)
    openings, _declined = trial_opener.read_docket(entries, today=today, local_rule=local_rule)
    read: dict[str, Opening] = {
        moments.trial_event_id(Moment(o.event.moment.value), o.event.entry_number): o
        for o in openings
    }
    for event_id, opening in read.items():
        existing = stored.get(event_id)
        if existing is not None:
            continue
        if lead_unread or opening.event.entry_number in lead_owned:
            continue
        if not opening.is_event or opening.resolution is not None:
            continue
        assert opening.opens_on is not None  # `is_event`
        # The net a forward cell on this motion would be refused on. An event
        # opened past it could never be forecast, and the commoner cause is a
        # ruling in a form the resolver passes over, which an event would
        # then carry as open.
        sign = resolver.motion_disposal_signal(opening.event, entries)
        if sign is not None:
            weighed = (
                () if isinstance(sign, str) or sign.entry_number is None else (sign.entry_number,)
            )
            plan.held_ruled.append(
                Triage(case_id, event_id, "a later entry may already rule on the motion", weighed)
            )
            continue
        _place(
            plan,
            _event(
                case_id,
                title,
                Moment(opening.event.moment.value),
                entry_number=opening.event.entry_number,
                opened_at=opening.opens_on,
                docket_entry_id=opening.filed.entry_id,
            ),
            opening.opens_on,
            today,
        )
    judgment_id = moments.trial_event_id(Moment.trial_judgment)
    final: JudgmentResolution | Unresolved | None = None
    if judgment or judgment_id in stored:
        final = resolver.resolve_judgment(
            [e for e in entries if (resolver.cite(e).date_filed or date.min) <= today]
        )
    if judgment and judgment_id not in stored and final is None:
        _place(
            plan,
            _event(case_id, title, Moment.trial_judgment, entry_number=None, opened_at=today),
            today,
            today,
        )
    for event_id, existing in sorted(stored.items()):
        spec = moments.trial_spec_for(event_id)
        if spec is None or existing.resolved:
            continue
        adjudication = settled.get((case_id, event_id))
        if not spec.per_motion:
            _settle(plan, existing, adjudication=adjudication, resolution=final, today=today)
            continue
        found = read.get(event_id)
        _settle(
            plan,
            existing,
            adjudication=adjudication,
            resolution=None if found is None else found.resolution,
            today=today,
            missing=None if found is not None else "the opener no longer reads this motion",
        )
    return plan


# --- the pass ----------------------------------------------------------------


@dataclass
class TrialPassReport:
    """What one pass over the watchlist's district dockets did."""

    read_on: date
    dockets_read: list[str] = field(default_factory=list)
    #: Listed district dockets the corpus holds no stored entries for.
    dockets_missing: list[str] = field(default_factory=list)
    #: ``(case id, event id)`` of each event written, resolved, or held back.
    opened: list[tuple[str, str]] = field(default_factory=list)
    would_open: list[tuple[str, str]] = field(default_factory=list)
    resolved: list[tuple[str, str]] = field(default_factory=list)
    triage: list[Triage] = field(default_factory=list)
    #: Motions not opened because a later entry may already rule on them.
    held_ruled: list[Triage] = field(default_factory=list)
    #: Member dockets whose lead docket is not stored: no motion opens on them.
    held_for_lead: list[str] = field(default_factory=list)
    #: case id -> the type of the error that stopped the pass on that docket.
    failed: dict[str, str] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        def pairs(found: list[tuple[str, str]]) -> list[dict[str, str]]:
            return [{"case_id": case_id, "event_id": event_id} for case_id, event_id in found]

        def listed(items: list[Triage]) -> list[dict[str, Any]]:
            return [
                {
                    "case_id": item.case_id,
                    "event_id": item.event_id,
                    "reason": item.reason,
                    "entries": list(item.entries),
                }
                for item in items
            ]

        return {
            "opener_rule": trial_opener.OPENER_RULE,
            "resolver_rule": resolver.RESOLVER_RULE,
            "read_on": self.read_on.isoformat(),
            "dockets_read": len(self.dockets_read),
            "dockets_missing": list(self.dockets_missing),
            "held_for_lead": list(self.held_for_lead),
            "opened": pairs(self.opened),
            "would_open": pairs(self.would_open),
            "resolved": pairs(self.resolved),
            "failed": dict(sorted(self.failed.items())),
            "triage": listed(self.triage),
            "held_ruled": listed(self.held_ruled),
        }

    def summary_line(self) -> str:
        return (
            f"trial events ({trial_opener.OPENER_RULE}, {resolver.RESOLVER_RULE}): "
            f"{len(self.dockets_read)} docket(s) read, {len(self.opened)} opened, "
            f"{len(self.resolved)} resolved, {len(self.triage)} to triage, "
            f"{len(self.would_open)} not opened (moment switched off), "
            f"{len(self.held_ruled)} not opened (may already be ruled on)"
            + (f", {len(self.failed)} docket(s) failed" if self.failed else "")
        )


def _entries(conn: corpus.ReadConnection, case_id: str) -> list[dict[str, Any]] | None:
    found = corpus.latest_snapshot(conn, case_id)
    if found is None:
        return None
    stored = found[1].get("docket_entries")
    return stored if isinstance(stored, list) else None


def _own_dockets(watchlist: AiWatchlist) -> frozenset[str]:
    """The listed cases' own district dockets: the ones with a final-disposition event."""
    return frozenset(
        ids.case_id(case.court, case.docket_id)
        for case in watchlist.cases
        if DISTRICT_COURT.fullmatch(case.court)
    )


def _pass_docket(  # noqa: PLR0913 - one docket of the pass and what it reads
    report: TrialPassReport,
    corpus_db_path: Path,
    data_root: Path,
    case_id: str,
    lead: str | None,
    cache: dict[str, list[dict[str, Any]] | None],
    *,
    today: date,
    local_rule: DistrictRule | None,
    adjudicated: Mapping[tuple[str, str], Adjudication] | None,
    judgment: bool,
) -> None:
    court, _, docket = case_id.partition("/")
    with corpus.connect(corpus_db_path) as conn:
        if case_id not in cache:
            cache[case_id] = _entries(conn, case_id)
        entries = cache[case_id]
        if not entries:
            report.dockets_missing.append(case_id)
            return
        report.dockets_read.append(case_id)
        owned: frozenset[int] = frozenset()
        lead_unread = False
        if lead is not None:
            if lead not in cache:
                cache[lead] = _entries(conn, lead)
            lead_unread = not cache[lead]
            owned = trial_opener.owned_by_lead(cache[lead] or (), entries)
        if lead_unread:
            report.held_for_lead.append(case_id)
        row = corpus.get_row(conn, case_id)
        held = {e.event_id: e for e in corpus.events_for_case(conn, case_id)}
        title = "" if row is None else (row.case_name or row.docket_number or "")
        plan = plan_docket(
            case_id,
            title,
            entries,
            held,
            today=today,
            local_rule=local_rule,
            lead_owned=owned,
            adjudicated=adjudicated,
            judgment=judgment,
            lead_unread=lead_unread,
        )
        # A stored open event with no committed definition is a write that
        # stopped between the corpus and the ledger: written again, from the
        # corpus row.
        case = CasePaths(data_root, court, int(docket))
        unwritten = [
            event
            for event_id, event in sorted(held.items())
            if moments.trial_spec_for(event_id) is not None
            and not event.resolved
            and not case.event(event_id).event_file.exists()
        ]
        if plan.opens or unwritten:
            persist_moment_events(conn, data_root, court, int(docket), [*unwritten, *plan.opens])
    report.opened.extend((case_id, e.event_id) for e in plan.opens)
    report.would_open.extend((case_id, e.event_id) for e in plan.would_open)
    report.triage.extend(plan.triage)
    report.held_ruled.extend(plan.held_ruled)
    if plan.outcomes:
        record_outcomes(
            corpus_db_path, data_root, court, int(docket), Resolution(outcomes=plan.outcomes)
        )
    report.resolved.extend((case_id, event_id) for event_id in sorted(plan.outcomes))


def run_pass(
    corpus_db_path: Path,
    data_root: Path,
    watchlist: AiWatchlist,
    *,
    today: date,
    local_rules: Mapping[str, DistrictRule] | None = None,
    adjudicated: Mapping[tuple[str, str], Adjudication] | None = None,
) -> TrialPassReport:
    """Open and resolve the trial stage's events on every listed district docket.

    Reads each docket's stored entries, so it follows the refresh that stores
    them and makes no upstream request. A docket the pass fails on is recorded
    by the error's type and skipped, so the others are still read. Writes an ``event.yaml`` for each
    event it opens and an ``outcome.json`` beside each it resolves, under
    ``data_root``, and the matching corpus rows.
    """
    rules = local_rules or {}
    report = TrialPassReport(read_on=today)
    own = _own_dockets(watchlist)
    seen: set[str] = set()
    cache: dict[str, list[dict[str, Any]] | None] = {}
    for case_id, lead in trial_opener.survey_dockets(watchlist):
        if case_id in seen:
            continue
        seen.add(case_id)
        try:
            _pass_docket(
                report,
                corpus_db_path,
                data_root,
                case_id,
                lead,
                cache,
                today=today,
                local_rule=rules.get(case_id.partition("/")[0]),
                adjudicated=adjudicated,
                judgment=case_id in own,
            )
        except Exception as exc:
            # One docket's failure must not cost the rest. The type only: a
            # message can quote the text it choked on.
            report.failed[case_id] = type(exc).__name__
    return report
