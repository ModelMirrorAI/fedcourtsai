"""Merits back-test: the decided argued cases a merits replay draws from, and their cutoffs.

The merits counterpart of :mod:`fedcourtsai.cert_backtest`'s population draw.
A merits replay forecasts the judgment of a case the Court has already decided,
from the record as it stood at one of the merits stage's declared moments, so
what it needs from the corpus is, per case, the moments it can be replayed at
and the day each one's record is cut.

**The population** is the decision record's own (:func:`.decision_record.assigned_by_term`):
granted modern cert dockets assigned to the October Term they were argued in.
From each Term it keeps the plenary docket a merits forecast is about — a grant
that opens a merits proceeding, did not ride the cert order (a GVR or summary
disposition leaves nothing to forecast), was argued, and carries a parsed merits
judgment. A DIG and an affirmance by an equally divided Court stay in: forward
merits cells are scored on them as *undisturbed*, and the merits base rate
counts them the same way (:class:`~fedcourtsai.schemas.Judgment`). A terminated
grant is never in a Term, since nothing was decided.

**One case per docket the filings are on.** A consolidated member whose filings
move to its lead docket has the lead's record, so the member is set aside by
name and the lead stands for both. A member is told from its lead by the
docket's own consolidation entry (:func:`.documents.consolidation_lead`), read
off its newest stored snapshot; a docket with no stored snapshot cannot be told
and is set aside rather than guessed at. Cases consolidated for argument alone,
still briefed apart, carry no such entry, so each is its own case. A member
whose lead the draw does not keep is set aside under its own reason, so an
argued case dropped whole is visible as one.

**The moments** are the merits stage's grant and briefed moments, each opening
where its forward counterpart does — the grant at ``date_cert_granted``, the
briefed moment at ``merits_brief_filed``, the respondent's merits brief — and
each cut the day after it opens, exclusive, as a forward cell's record is. A
case is kept only where both open, in order, before argument: a case without a
briefed date, or whose dates disagree with each other, is set aside by name
rather than replayed at one moment alone, so every kept case faces both.

Read-only and outcome-blind in what it *selects on*: the judgment is read only
to require that one exists and to carry it to the scorer, never to choose among
cases.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from datetime import date, timedelta
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from . import corpus
from .pipeline import moments
from .pipeline.decision_record import assigned_by_term, rode_the_order
from .pipeline.documents import consolidation_lead
from .pipeline.judgment import judgment_disturbed
from .schemas import Judgment, MeritsDecisionMethod, Moment, Stage

#: The merits moments a replay is cut at, in time order.
MERITS_BACKTEST_MOMENTS: tuple[Moment, ...] = (Moment.grant, Moment.briefed)

#: Why a decided argued docket is not replayed.
ExclusionReason = Literal[
    "consolidated-member",
    "lead-not-replayed",
    "no-snapshot",
    "no-briefed-date",
    "dates-out-of-order",
]

#: Reads a case's newest stored snapshot payload, or ``None``.
SnapshotReader = Callable[[str], dict[str, Any] | None]


class MeritsReplayCutoff(BaseModel):
    """One moment a case is replayed at: the event it forecasts and its record's cut."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    moment: Moment
    event_id: str = Field(description="The merits moment's declared event id")
    opened_at: date = Field(description="Where the forward moment opens on this case")
    cutoff: date = Field(
        description="The record's exclusive cut: entries dated before it are kept "
        "(`opened_at` plus one day, as a forward cell's record is cut)"
    )


class MeritsReplayCase(BaseModel):
    """A decided argued case a merits replay forecasts, with what the scorer reads."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    docket_number: str
    case_name: str | None
    term: int = Field(description="The October Term the case was argued in")
    ifp: bool = Field(description="An in-forma-pauperis docket")
    argued: date
    decided: date
    judgment: Judgment
    disturbed: bool = Field(description="Whether the judgment disturbed the decision below")
    method: MeritsDecisionMethod | None
    cutoffs: list[MeritsReplayCutoff]


class MeritsReplayExclusion(BaseModel):
    """A decided argued docket the replay sets aside, and why."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    docket_number: str | None
    term: int
    reason: ExclusionReason
    detail: str
    judgment: Judgment = Field(
        description="The docket's judgment, read for the audit of what the draw set "
        "aside and never selected on"
    )
    disturbed: bool


class MeritsBacktestTerm(BaseModel):
    """One October Term's share of the population."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    term: int
    assigned: int = Field(ge=0, description="Granted dockets the decision record assigns it")
    order_riding: int = Field(ge=0, description="Of those, dispositions that rode the cert order")
    argued_unjudged: int = Field(
        ge=0,
        description="Argued plenary dockets with no parsed merits judgment, which "
        "the draw cannot keep: a parse gap, counted so it is not silent",
    )
    plenary_decided: int = Field(
        ge=0, description="Argued plenary dockets with a parsed merits judgment"
    )
    cases: int = Field(ge=0, description="Cases kept for replay")
    excluded: dict[str, int] = Field(description="Dockets set aside, by reason")


class MeritsBacktestPopulation(BaseModel):
    """The merits replay's population over a set of Terms, and what it set aside."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pulled_through: date | None = Field(
        description="The corpus vintage: the newest pull stamp across the blob"
    )
    terms: list[MeritsBacktestTerm]
    cases: list[MeritsReplayCase]
    excluded: list[MeritsReplayExclusion]


def _snapshot_reader(conn: corpus.ReadConnection) -> SnapshotReader:
    def read(case_id: str) -> dict[str, Any] | None:
        found = corpus.latest_snapshot(conn, case_id)
        return None if found is None else found[1]

    return read


def _lead_of(row: corpus.CorpusRow, read: SnapshotReader) -> str | ExclusionReason | None:
    """The lead docket a consolidated member files on, ``None`` for a lead or a
    standalone docket, or ``"no-snapshot"`` where nothing stored can tell."""
    payload = read(row.case_id)
    if payload is None:
        return "no-snapshot"
    lead = consolidation_lead(payload)
    return None if lead is None else f"{lead[0]:02d}-{lead[1]}"


def _cutoffs(row: corpus.CorpusRow) -> list[MeritsReplayCutoff] | ExclusionReason:
    granted, briefed, argued = row.date_cert_granted, row.merits_brief_filed, row.merits_argued
    if briefed is None:
        return "no-briefed-date"
    if granted is None or argued is None or not granted < briefed <= argued:
        return "dates-out-of-order"
    specs = {spec.moment: spec for spec in moments.moments_for(Stage.merits)}
    opened = {Moment.grant: granted, Moment.briefed: briefed}
    return [
        MeritsReplayCutoff(
            moment=moment,
            event_id=specs[moment].event_id,
            opened_at=opened[moment],
            cutoff=opened[moment] + timedelta(days=1),
        )
        for moment in MERITS_BACKTEST_MOMENTS
    ]


def _detail(row: corpus.CorpusRow, reason: ExclusionReason, lead: str | None) -> str:
    if reason == "consolidated-member":
        return f"files on its lead docket, No. {lead}"
    if reason == "no-snapshot":
        return "no stored snapshot to tell a consolidated member from its lead"
    if reason == "no-briefed-date":
        return "no respondent's merits brief date on the row"
    return (
        f"granted {row.date_cert_granted or 'unknown'}, briefed {row.merits_brief_filed}, "
        f"argued {row.merits_argued or 'unknown'}: not in order"
    )


def merits_backtest_population(
    conn: corpus.ReadConnection,
    *,
    terms: Sequence[int],
    read_snapshot: SnapshotReader | None = None,
) -> MeritsBacktestPopulation:
    """The decided argued cases of ``terms`` a merits replay draws from, in ``terms``'s order.

    Terms come in the order named, so a caller that takes the head of the list
    takes the Term it put first; within a Term, cases are ordered by argued
    date, then case id. ``read_snapshot`` serves each candidate's newest stored
    snapshot (default: the corpus's own read), which is the only payload read,
    made only for an argued plenary docket with a judgment.
    """
    wanted = list(dict.fromkeys(terms))
    if not wanted:
        raise ValueError("name at least one October Term")
    read = read_snapshot if read_snapshot is not None else _snapshot_reader(conn)
    by_term, _, _ = assigned_by_term(conn, first_term=min(wanted), last_term=max(wanted))
    counts: dict[int, tuple[int, int, int, int]] = {}
    cases: list[MeritsReplayCase] = []
    excluded: list[tuple[MeritsReplayExclusion, str | None]] = []
    for term in wanted:
        members = by_term[term]
        argued = [
            row
            for row in members
            if not rode_the_order(row)
            and corpus.opens_merits_proceeding(row)
            and row.merits_argued is not None
        ]
        plenary = [row for row in argued if row.merits_judgment is not None and row.merits_decided]
        counts[term] = (
            len(members),
            sum(rode_the_order(row) for row in members),
            len(argued) - len(plenary),
            len(plenary),
        )
        for row in sorted(plenary, key=lambda r: (r.merits_argued or date.min, r.case_id)):
            judgment = Judgment(str(row.merits_judgment))
            found = _lead_of(row, read)
            lead = found if found != "no-snapshot" else None
            outcome: list[MeritsReplayCutoff] | ExclusionReason
            if found == "no-snapshot":
                outcome = "no-snapshot"
            elif lead is not None:
                outcome = "consolidated-member"
            else:
                outcome = _cutoffs(row)
            if isinstance(outcome, str):
                exclusion = MeritsReplayExclusion(
                    case_id=row.case_id,
                    docket_number=row.docket_number,
                    term=term,
                    reason=outcome,
                    detail=_detail(row, outcome, lead),
                    judgment=judgment,
                    disturbed=judgment_disturbed(judgment),
                )
                excluded.append((exclusion, lead))
                continue
            method = row.merits_decision_method
            cases.append(
                MeritsReplayCase(
                    case_id=row.case_id,
                    docket_number=str(row.docket_number),
                    case_name=row.case_name,
                    term=term,
                    ifp=corpus.is_ifp_petition(row),
                    argued=row.merits_argued,
                    decided=row.merits_decided,
                    judgment=judgment,
                    disturbed=judgment_disturbed(judgment),
                    method=MeritsDecisionMethod(method) if method else None,
                    cutoffs=outcome,
                )
            )
    kept = {corpus.normalize_docket_number(case.docket_number) for case in cases}
    settled: list[MeritsReplayExclusion] = []
    for found_exclusion, lead in excluded:
        exclusion = found_exclusion
        if exclusion.reason == "consolidated-member" and (
            corpus.normalize_docket_number(lead) not in kept
        ):
            exclusion = exclusion.model_copy(
                update={
                    "reason": "lead-not-replayed",
                    "detail": f"files on its lead docket, No. {lead}, which this draw "
                    "does not keep",
                }
            )
        settled.append(exclusion)
    term_rows = []
    for term in wanted:
        assigned, riding, unjudged, decided = counts[term]
        reasons = Counter(e.reason for e in settled if e.term == term)
        term_rows.append(
            MeritsBacktestTerm(
                term=term,
                assigned=assigned,
                order_riding=riding,
                argued_unjudged=unjudged,
                plenary_decided=decided,
                cases=sum(case.term == term for case in cases),
                excluded=dict(sorted(reasons.items())),
            )
        )
    return MeritsBacktestPopulation(
        pulled_through=corpus.latest_pull_date(conn),
        terms=term_rows,
        cases=cases,
        excluded=settled,
    )
