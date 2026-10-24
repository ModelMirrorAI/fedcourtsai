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
rather than replayed at one moment alone, so every kept case is put to both.

Read-only and outcome-blind in what it *selects on*: the judgment is read only
to require that one exists and to carry it to the scorer, never to choose among
cases.

**A replay cell** (:func:`provision_replay_cell`) is provisioned the way a forward
cell at the same moment is, into a scratch data root and never the ledger: the
record goes through :func:`.provision.place_at_moment` at the moment's cutoff and
:func:`.provision.write_cell_record` in ``replay`` mode, so the snapshot and the
filed documents are what a forward cell placed at that moment reads, and the
event is written open. Two things a forward cell does not need are added,
because a decided docket is being replayed. The snapshot's top-level outcome
fields are stripped (:func:`.provision.redact_snapshot`), as the cert replay
strips them. And the placed snapshot is fenced with the forward merits leakage
scan (:func:`.outcome.forward_leakage`): a cell whose kept entries still show
the judgment is not written, and is counted. Two things a forward cell has are
missing, so a replay figure reads as a lower bound on the same predictor's
forward information set: the related dockets a forward cell is given, and the
counsel blocks, which the redaction strips from every replay snapshot.

**A sweep** (:func:`provision_replay_cells`) provisions every kept case at both
moments into a fresh scratch tree and returns the ledger of what was written
and what was fenced. A fence drops one moment's cell, not the case, so the two
moments' cell sets can differ; a comparison *between* the moments reads only
the cases written at both (:attr:`MeritsReplaySweep.paired`), or a lift from
grant to briefed would be partly a difference in which cases were asked.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from . import corpus, provision
from .paths import CasePaths
from .pipeline import moments
from .pipeline.decision_record import assigned_by_term, rode_the_order
from .pipeline.documents import KIND_MERITS_BRIEF_RESPONDENT, consolidation_lead
from .pipeline.judgment import judgment_disturbed
from .pipeline.outcome import forward_leakage
from .schemas import Judgment, MeritsDecisionMethod, Moment, PredictableEvent, Stage
from .serialize import write_yaml

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


#: Why a replay cell was not written.
FenceReason = Literal["no-snapshot", "shows-the-judgment", "briefs-not-staged", "bad-document-kind"]


class MeritsReplayCell(BaseModel):
    """One replay cell written into the scratch root, and the size of its cut."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    event_id: str
    moment: Moment
    cutoff: date
    snapshot_date: date
    provenance: Literal["as-stored", "dated", "truncated"] = Field(
        description="`dated`: a stored snapshot from before the cutoff; `truncated`: "
        "the latest one with its later entries removed"
    )
    dropped_entries: int = Field(ge=0, description="Docket entries the cut removed")
    dropped_documents: int = Field(ge=0, description="Filed documents the cut removed")
    documents: list[str] = Field(description="The document kinds staged, in order")


class MeritsReplayFenced(BaseModel):
    """A replay cell the provisioner refused to write, and why."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    event_id: str
    moment: Moment
    reason: FenceReason
    detail: str
    judgment: Judgment = Field(
        description="The case's judgment, so the fences can be read against it"
    )
    disturbed: bool


class MeritsReplaySweep(BaseModel):
    """Every kept case's replay cells, written or fenced, at each moment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cells: list[MeritsReplayCell]
    fenced: list[MeritsReplayFenced]

    @property
    def paired(self) -> list[str]:
        """The cases written at every moment: the only set the moments compare on."""
        written: dict[str, set[Moment]] = {}
        for cell in self.cells:
            written.setdefault(cell.case_id, set()).add(cell.moment)
        return [case for case, seen in written.items() if seen == set(MERITS_BACKTEST_MOMENTS)]

    def fence_counts(self) -> dict[str, dict[str, int]]:
        """Fenced cells per moment, by reason."""
        counts: dict[str, Counter[str]] = {m.value: Counter() for m in MERITS_BACKTEST_MOMENTS}
        for cell in self.fenced:
            counts[cell.moment.value][cell.reason] += 1
        return {moment: dict(sorted(c.items())) for moment, c in counts.items()}


def _fenced(
    case: MeritsReplayCase, cut: MeritsReplayCutoff, reason: FenceReason, detail: str
) -> MeritsReplayFenced:
    return MeritsReplayFenced(
        case_id=case.case_id,
        event_id=cut.event_id,
        moment=cut.moment,
        reason=reason,
        detail=detail,
        judgment=case.judgment,
        disturbed=case.disturbed,
    )


def _replay_event(case: MeritsReplayCase, cut: MeritsReplayCutoff) -> PredictableEvent:
    spec = moments.spec_for(cut.event_id)
    if spec is None or spec.stage is not Stage.merits:
        raise ValueError(f"{cut.event_id} is not a declared merits moment")
    return PredictableEvent(
        event_id=spec.event_id,
        case_id=case.case_id,
        kind=spec.kind,
        stage=spec.stage,
        moment=spec.moment,
        title=case.case_name or case.docket_number,
        description=spec.description,
        opened_at=cut.opened_at,
        decision_target=spec.decision_target,
        resolved=False,  # the pre-decision view: the outcome stays hidden
    )


def moment_root(work_root: Path, moment: Moment) -> Path:
    """The scratch data root one moment's replay cells are written under.

    One per moment, because a case's ``record/`` is shared by every event on it:
    the briefed moment's record written into the grant moment's tree would
    replace the record the grant cell reads.
    """
    return work_root / moment.value


def provision_replay_cell(
    conn: corpus.ReadConnection,
    case: MeritsReplayCase,
    cut: MeritsReplayCutoff,
    work_root: Path,
) -> MeritsReplayCell | MeritsReplayFenced:
    """Write one case's replay cell for one moment, or say why not.

    ``work_root`` is a scratch tree, never the ledger; the cell is written under
    its moment's own root (:func:`moment_root`): the event (open) and the cell's
    whole ``record/``. Writes nothing where the corpus holds no snapshot for the
    case, where the placed and redacted snapshot still shows the judgment, or,
    on the briefed moment, where the respondent's merits brief the moment opens
    on is not among the documents staged: a cell without it would forecast from
    the grant moment's record under the briefed moment's name. A stored document
    kind the record cannot name a file by fences the cell too, rather than
    stopping a sweep over the population at one row. A refusal leaves an earlier
    cell at the same path alone, so a caller reusing a tree is reading stale
    cells; :func:`provision_replay_cells` refuses a tree that is not empty.
    """
    latest = corpus.latest_snapshot(conn, case.case_id)
    if latest is None:
        return _fenced(
            case,
            cut,
            "no-snapshot",
            "the corpus holds no snapshot for the case",
        )
    documents = corpus.documents_for_case(conn, case.case_id)
    try:
        provision.screen_document_kinds(documents)
    except provision.ProvisionError as refused:
        return _fenced(case, cut, "bad-document-kind", str(refused))
    read = provision.CellRead(
        latest=latest,
        documents=documents,
        events=[],
        row=None,
        cutoff=cut.cutoff,
        dated=corpus.snapshot_at(conn, case.case_id, before=cut.cutoff),
    )
    snapshot_date, payload = latest
    placement = provision.place_at_moment(
        case.case_id,
        cut.event_id,
        cut.cutoff,
        read,
        payload=payload,
        snapshot_date=snapshot_date,
        documents=documents,
    )
    placement = replace(placement, payload=provision.redact_snapshot(placement.payload))
    court, _, docket = case.case_id.partition("/")
    shown = forward_leakage(placement.payload, court, cut.event_id)
    if shown is not None:
        return _fenced(
            case,
            cut,
            "shows-the-judgment",
            detail=shown,
        )
    if cut.moment is Moment.briefed and not any(
        doc.kind == KIND_MERITS_BRIEF_RESPONDENT for doc in placement.documents
    ):
        return _fenced(
            case,
            cut,
            "briefs-not-staged",
            detail="no respondent's merits brief filed before the cutoff is stored",
        )
    paths = CasePaths(moment_root(work_root, cut.moment), court, int(docket))
    write_yaml(paths.event(cut.event_id).event_file, _replay_event(case, cut))
    written = provision.write_cell_record(
        paths, case.case_id, placement, mode="replay", cutoff=cut.cutoff
    )
    return MeritsReplayCell(
        case_id=case.case_id,
        event_id=cut.event_id,
        moment=cut.moment,
        cutoff=cut.cutoff,
        snapshot_date=placement.snapshot_date,
        provenance=placement.provenance,
        dropped_entries=placement.dropped_entries,
        dropped_documents=placement.dropped_documents,
        documents=[doc.kind for doc, _ in written.staged],
    )


def provision_replay_cells(
    conn: corpus.ReadConnection,
    cases: Sequence[MeritsReplayCase],
    work_root: Path,
) -> MeritsReplaySweep:
    """Provision every case at each of its moments into a fresh ``work_root``.

    Refuses a ``work_root`` that exists and is not empty: a cell fenced on this
    pass would otherwise leave the previous pass's cell at its path, and a
    reader walking the tree would count it.
    """
    if work_root.exists() and any(work_root.iterdir()):
        raise ValueError(f"{work_root} is not empty; a replay sweep writes into a fresh tree")
    cells: list[MeritsReplayCell] = []
    fenced: list[MeritsReplayFenced] = []
    for case in cases:
        for cut in case.cutoffs:
            result = provision_replay_cell(conn, case, cut, work_root)
            if isinstance(result, MeritsReplayCell):
                cells.append(result)
            else:
                fenced.append(result)
    return MeritsReplaySweep(cells=cells, fenced=fenced)
