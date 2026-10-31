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

**Scoring** (:func:`score_merits_backtest`) reads each cell's P(disturbed)
against the judgment, per predictor and moment, and against an **as-of** base
rate (:func:`as_of_base_rate`): the disturbed share of the population's lead
dockets argued in the cell's Term or the few before it and decided strictly
before the cell's cutoff. The forward channel's ``merits_base_rate`` pools by
grant Term, which on a replay admits judgments handed down after the cutoff; the
as-of rate admits none, at the cost of being a different baseline, so a skill
figure here is never set beside a forward one.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from . import corpus, provision
from .backtest import BacktestPrediction
from .cert_backtest import (
    _engine_lanes,
    _merged,
    _ProvisionedPetition,
    _run_lanes,
    _runners_by_predictor,
    replay_model,
)
from .config import get_settings
from .paths import CasePaths
from .pipeline import moments
from .pipeline.decision_record import assigned_by_term, rode_the_order
from .pipeline.documents import (
    KIND_MERITS_BRIEF_RESPONDENT,
    LOWER_COURT_KINDS,
    consolidation_lead,
)
from .pipeline.judgment import judgment_disturbed
from .pipeline.outcome import forward_leakage
from .pipeline.runner import RunRequest
from .schemas import (
    CertBacktestDisclosure,
    Judgment,
    MeritsBacktest,
    MeritsBacktestBaseline,
    MeritsBacktestCellLoss,
    MeritsBacktestDispatch,
    MeritsBacktestEntry,
    MeritsBacktestMomentScore,
    MeritsBacktestPaired,
    MeritsBacktestTermCount,
    MeritsDecisionMethod,
    Moment,
    PredictableEvent,
    Stage,
    UsageRole,
)
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


def replay_event(
    case: MeritsReplayCase, cut: MeritsReplayCutoff, *, resolved: bool = False
) -> PredictableEvent:
    """The merits moment's event definition for ``case`` at ``cut``.

    Unresolved by default, the pre-decision view a replay cell sees; a grading
    overlay asks for the resolved one.
    """
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
        resolved=resolved,
    )


def docket_term(case: MeritsReplayCase) -> int | None:
    """The case's docket Term: the replay clock's Term half, self-excluding."""
    return corpus.scotus_term_year(case.docket_number)


def _term_clock(case: MeritsReplayCase) -> str | None:
    term = docket_term(case)
    return None if term is None else str(term)


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
    # The decision-below fill walks undecided cases only, so a decided case in
    # this population holds the lower-court kinds only by accident of timing;
    # staging them would give some replay cells an input the others lack.
    documents = [
        doc
        for doc in corpus.documents_for_case(conn, case.case_id)
        if doc.kind not in LOWER_COURT_KINDS
    ]
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
    write_yaml(paths.event(cut.event_id).event_file, replay_event(case, cut))
    written = provision.write_cell_record(
        paths,
        case.case_id,
        placement,
        mode="replay",
        cutoff=cut.cutoff,
        decided_before=_term_clock(case),
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
    moments: Sequence[Moment] = MERITS_BACKTEST_MOMENTS,
) -> MeritsReplaySweep:
    """Provision every case at each of ``moments`` into a fresh ``work_root``.

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
            if cut.moment not in moments:
                continue
            result = provision_replay_cell(conn, case, cut, work_root)
            if isinstance(result, MeritsReplayCell):
                cells.append(result)
            else:
                fenced.append(result)
    return MeritsReplaySweep(cells=cells, fenced=fenced)


#: The salt every draw rank mixes in. Pre-registered and fixed, so a reader can
#: recompute a recorded draw from its report's ``draw_key``.
MERITS_DRAW_SALT = "fedcourtsai/merits-backtest/draw"


def draw_rank(key: str, case_id: str) -> str:
    """A case's place in the draw order: a function of the salt, the key and the id only."""
    return hashlib.sha256(f"{MERITS_DRAW_SALT}|{key}|{case_id}".encode()).hexdigest()


def draw_cases(cases: Sequence[MeritsReplayCase], limit: int, key: str) -> list[MeritsReplayCase]:
    """The first ``limit`` cases in ``key``'s hash order, or every case at ``0``.

    No outcome, date or docket number feeds the order, so a limited draw is a
    simple random sample of the population, and the same vintage draws the same
    cases.
    """
    ordered = sorted(cases, key=lambda case: draw_rank(key, case.case_id))
    return ordered if limit <= 0 else ordered[:limit]


def population_for(
    population: MeritsBacktestPopulation, terms: Sequence[int]
) -> MeritsBacktestPopulation:
    """``population`` narrowed to ``terms``, in the order named."""
    order = {term: index for index, term in enumerate(terms)}
    return MeritsBacktestPopulation(
        pulled_through=population.pulled_through,
        terms=sorted(
            (term for term in population.terms if term.term in order),
            key=lambda term: order[term.term],
        ),
        cases=[case for case in population.cases if case.term in order],
        excluded=[item for item in population.excluded if item.term in order],
    )


#: Argued Terms before a cell's own that its as-of baseline pools.
MERITS_REPLAY_BASELINE_TERMS = 3

#: The fewest pooled judgments an as-of baseline rests on, the forward merits
#: floor (:data:`.pipeline.base_rates.MERITS_BASE_RATE_MIN_PARSED`) restated
#: here so the report can carry it beside the rule.
MERITS_REPLAY_BASELINE_MIN = 30


def baseline_pool_terms(terms: Sequence[int]) -> list[int]:
    """Every argued Term an as-of baseline for ``terms`` may pool, oldest first."""
    if not terms:
        return []
    return list(range(min(terms) - MERITS_REPLAY_BASELINE_TERMS, max(terms) + 1))


def as_of_base_rate(
    pool: Sequence[MeritsReplayCase],
    cutoff: date,
    term: int,
    *,
    lookback_terms: int = MERITS_REPLAY_BASELINE_TERMS,
    min_decided: int = MERITS_REPLAY_BASELINE_MIN,
) -> float | None:
    """The disturbed share of ``pool`` a cell cut at ``cutoff`` could have known.

    Pools the cases argued in ``term`` or the ``lookback_terms`` before it and
    decided strictly before ``cutoff``. ``None`` below ``min_decided`` pooled
    judgments.
    """
    known = [
        case.disturbed
        for case in pool
        if term - lookback_terms <= case.term <= term and case.decided < cutoff
    ]
    if len(known) < min_decided:
        return None
    return sum(known) / len(known)


def _brier(probability: float, disturbed: bool) -> float:
    return (probability - float(disturbed)) ** 2


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _moment_score(
    moment: Moment,
    cells: Sequence[MeritsReplayCell],
    predicted: Mapping[str, BacktestPrediction],
    cases: Mapping[str, MeritsReplayCase],
    baselines: Mapping[tuple[str, Moment], float | None],
    terms: Sequence[int],
    disclosed: Sequence[CertBacktestDisclosure],
) -> MeritsBacktestMomentScore:
    briers: list[float] = []
    hits: list[float] = []
    disturbed: list[float] = []
    skill_own: list[float] = []
    skill_base: list[float] = []
    per_term: Counter[int] = Counter({term: 0 for term in terms})
    lost = 0
    for cell in cells:
        prediction = predicted.get(cell.case_id)
        if prediction is None:
            lost += 1
            continue
        case = cases[cell.case_id]
        brier = _brier(prediction.probability_granted, case.disturbed)
        briers.append(brier)
        hits.append(float((prediction.probability_granted >= 0.5) == case.disturbed))
        disturbed.append(float(case.disturbed))
        per_term[case.term] += 1
        base = baselines.get((cell.case_id, moment))
        if base is not None:
            skill_own.append(brier)
            skill_base.append(_brier(base, case.disturbed))
    base_sum = sum(skill_base)
    share = _mean(disturbed)
    return MeritsBacktestMomentScore(
        moment=moment,
        events_scored=len(briers),
        lost=lost,
        terms={str(term): n for term, n in sorted(per_term.items())},
        accuracy=_mean(hits),
        disturbed_share=share,
        majority_accuracy=None if share is None else max(share, 1.0 - share),
        mean_brier_score=_mean(briers),
        baselined=len(skill_own),
        baselined_brier_score=_mean(skill_own),
        cells_flagged=sum(1 for d in disclosed if d.case_id in predicted),
        exposure_candidates=sum(
            1
            for d in disclosed
            if d.case_id in predicted and any(f.outcome_exposure_candidate for f in d.flags)
        ),
        baseline_brier_score=_mean(skill_base),
        brier_skill=(1.0 - sum(skill_own) / base_sum) if skill_own and base_sum > 0 else None,
    )


def _paired(
    by_moment: Mapping[Moment, Mapping[str, BacktestPrediction]],
    cases: Mapping[str, MeritsReplayCase],
) -> MeritsBacktestPaired:
    grant, briefed = by_moment.get(Moment.grant, {}), by_moment.get(Moment.briefed, {})
    both = sorted(set(grant) & set(briefed))
    early = [_brier(grant[c].probability_granted, cases[c].disturbed) for c in both]
    late = [_brier(briefed[c].probability_granted, cases[c].disturbed) for c in both]
    early_mean, late_mean = _mean(early), _mean(late)
    return MeritsBacktestPaired(
        cases=len(both),
        disturbed=sum(cases[c].disturbed for c in both),
        grant_mean_brier=early_mean,
        briefed_mean_brier=late_mean,
        brier_change=(
            late_mean - early_mean if early_mean is not None and late_mean is not None else None
        ),
    )


def score_merits_backtest(
    population: MeritsBacktestPopulation,
    pool: Sequence[MeritsReplayCase],
    outcome: MeritsReplayOutcome,
    *,
    run_id: str | None = None,
    dispatch: MeritsBacktestDispatch | None = None,
) -> MeritsBacktest:
    """The merits back-test report over one replay's cells and what came back from them.

    ``outcome.predictions`` maps predictor id, then moment, then case id to the
    cell's prediction; a written cell with no prediction is counted ``lost`` for
    that predictor and moment. A prediction for a cell the sweep did not write is
    ignored: the sweep is the set scored. ``pool`` is the population the as-of
    baselines are drawn from (:func:`baseline_pool_terms` says which Terms it
    needs). The disclosures are counted over the scored cells and never move one
    out of the scores.
    """
    sweep, predictions, ran_on = outcome.sweep, outcome.predictions, outcome.ran_on
    disclosures = outcome.disclosures
    cases = {case.case_id: case for case in population.cases}
    terms = [term.term for term in population.terms]
    baselines = {
        (cell.case_id, cell.moment): as_of_base_rate(pool, cell.cutoff, cases[cell.case_id].term)
        for cell in sweep.cells
    }
    by_moment = {
        moment: [cell for cell in sweep.cells if cell.moment is moment]
        for moment in MERITS_BACKTEST_MOMENTS
    }
    entries = []
    for predictor_id in sorted(predictions):
        written = {
            moment: {
                cell.case_id: predictions[predictor_id][moment][cell.case_id]
                for cell in by_moment[moment]
                if cell.case_id in predictions[predictor_id].get(moment, {})
            }
            for moment in MERITS_BACKTEST_MOMENTS
        }
        engine, model = ran_on.get(predictor_id, (None, None))
        entries.append(
            MeritsBacktestEntry(
                predictor_id=predictor_id,
                engine=engine,
                model=model,
                moments=[
                    _moment_score(
                        moment,
                        by_moment[moment],
                        written[moment],
                        cases,
                        baselines,
                        terms,
                        [
                            found
                            for at, found in disclosures
                            if at is moment and found.predictor_id == predictor_id and found.scored
                        ],
                    )
                    for moment in MERITS_BACKTEST_MOMENTS
                ],
                paired=_paired(written, cases),
            )
        )
    return MeritsBacktest(
        pulled_through=population.pulled_through,
        run_id=run_id,
        dispatch=dispatch,
        terms=[
            MeritsBacktestTermCount(
                term=term.term,
                cases=term.cases,
                argued_unjudged=term.argued_unjudged,
                excluded=term.excluded,
                excluded_disturbed=sum(
                    item.disturbed for item in population.excluded if item.term == term.term
                ),
            )
            for term in population.terms
        ],
        cells={moment.value: len(by_moment[moment]) for moment in MERITS_BACKTEST_MOMENTS},
        fenced=sweep.fence_counts(),
        paired_cases=len(sweep.paired),
        baseline=MeritsBacktestBaseline(
            lookback_terms=MERITS_REPLAY_BASELINE_TERMS, min_decided=MERITS_REPLAY_BASELINE_MIN
        ),
        unavailable=sorted(outcome.unavailable),
        lost_cells=sorted(
            outcome.lost_cells, key=lambda loss: (loss.predictor_id, loss.case_id, loss.moment)
        ),
        entries=entries,
    )


@dataclass(frozen=True)
class MeritsReplayOutcome:
    """What one merits engine replay produced: the cells, and what came back.

    Everything the report needs, because the work root is discarded with the
    runner: the sweep (cells written and fenced), each predictor's predictions
    by moment, the backend and model behind each predictor, the predictors whose
    engine was missing, every lost cell, and what each cell wrote in
    ``flags.json``.
    """

    sweep: MeritsReplaySweep
    predictions: dict[str, dict[Moment, dict[str, BacktestPrediction]]]
    ran_on: Mapping[str, tuple[str | None, str | None]]
    unavailable: list[str]
    lost_cells: list[MeritsBacktestCellLoss]
    disclosures: list[tuple[Moment, CertBacktestDisclosure]] = field(default_factory=list)
    unkept: list[str] = field(default_factory=list)


KEPT_FORECAST_FILES = frozenset(
    {"prediction.json", "predicted_reasoning.md", "reasoning.md", "flags.json"}
)
"""The per-predictor files a kept cell contributes: what the grading pilot reads."""

KEPT_FILE_MAX_BYTES = 256 * 1024
"""A kept file larger than this is refused: a forecast is prose, not a record."""


def _is_kept_path(parts: tuple[str, ...], run_id: str) -> bool:
    """Whether a lane-relative path is an event definition or one of its forecasts."""
    in_event = len(parts) > 5 and parts[0] == "cases" and parts[3] == "events"
    if not in_event:
        return False
    if len(parts) == 6:
        return parts[5] == "event.yaml"
    return (
        len(parts) == 9
        and parts[5] == "predictions"
        and parts[7] == run_id
        and parts[8] in KEPT_FORECAST_FILES
    )


def _read_regular(path: Path) -> bytes | None:
    """A regular file's bytes, read through one handle that refuses a link; ``None`` if not.

    Opened without following a link and checked on the open handle, so a path
    swapped for a link after the walk saw it is refused rather than followed,
    and read at most one byte past the cap, so a file that grows is refused too.
    """
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError:
        return None
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            return None
        body = handle.read(KEPT_FILE_MAX_BYTES + 1)
    return body if len(body) <= KEPT_FILE_MAX_BYTES else None


def kept_forecasts(root: Path, run_id: str) -> tuple[dict[Path, bytes], list[str]]:
    """The forecast files of one finished lane tree, by path, and the paths refused.

    An allowlist over the cell layout, not an exclusion of the record: each
    event's ``event.yaml`` (``cases/<court>/<docket>/events/<event>/``) and, in
    that event's ``predictions/<predictor>/<run_id>/``, the files
    :data:`KEPT_FORECAST_FILES` names. Nothing else a cell wrote is kept,
    whatever it is called, so a copy of the record placed elsewhere in the tree
    stays behind. A kept path must be a regular file, not a link, and at most
    :data:`KEPT_FILE_MAX_BYTES`; an allowlisted path that fails either is
    refused and listed. The walk does not follow links.
    """
    kept: dict[Path, bytes] = {}
    refused: list[str] = []
    for directory, _, names in os.walk(root, followlinks=False):
        for name in names:
            path = Path(directory, name)
            rel = path.relative_to(root)
            if not _is_kept_path(rel.parts, run_id):
                continue
            body = _read_regular(path)
            if body is None:
                refused.append(rel.as_posix())
                continue
            kept[rel] = body
    return kept, sorted(refused)


def _check_keep_root(keep_root: Path, work_root: Path) -> None:
    """Refuse a keep root inside the work root, or one that already holds anything."""
    if keep_root.resolve().is_relative_to(work_root.resolve()):
        raise ValueError(f"{keep_root} is inside the work root {work_root}")
    if keep_root.exists() and any(keep_root.iterdir()):
        raise ValueError(f"{keep_root} is not empty")


def _write_kept(keep_root: Path, kept: Mapping[Path, bytes], run_id: str) -> list[str]:
    """Write the held forecasts under ``keep_root``, with the run they belong to.

    A keep root something else wrote to while the cells ran gets nothing, so
    the harness's files never ship beside a planted one; that is reported.
    """
    if keep_root.exists() and any(keep_root.iterdir()):
        return [f"{keep_root}: written during the run; nothing kept"]
    keep_root.mkdir(parents=True, exist_ok=True)
    for rel, body in sorted(kept.items()):
        (keep_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (keep_root / rel).write_bytes(body)
    (keep_root / "run-id").write_text(run_id + "\n")
    return []


def _petitions(
    sweep: MeritsReplaySweep,
    by_case: Mapping[str, MeritsReplayCase],
    *,
    run_id: str,
    data_root: Path,
    ledger_root: Path | None,
) -> list[_ProvisionedPetition]:
    """Each written cell's run contract, its two per-predictor slots left open."""
    petitions = []
    for cell in sweep.cells:
        court, _, docket = cell.case_id.partition("/")
        petitions.append(
            _ProvisionedPetition(
                case_id=cell.case_id,
                cell=RunRequest(
                    role=UsageRole.predictor,
                    court_id=court,
                    docket_id=int(docket),
                    event_id=cell.event_id,
                    actor_id="",
                    prompt=Path(),
                    run_id=run_id,
                    data_root=data_root,
                    decided_before=docket_term(by_case[cell.case_id]),
                    replay_cutoff=cell.cutoff,
                ),
                stray_paths=(
                    CasePaths(ledger_root, court, int(docket)).event(cell.event_id)
                    if ledger_root is not None
                    else None
                ),
            )
        )
    return petitions


def replay_merits_predictors(  # noqa: PLR0913 - the campaign's dispatch, each a keyword
    conn: corpus.ReadConnection,
    cases: Sequence[MeritsReplayCase],
    *,
    config_root: Path,
    work_root: Path,
    run_id: str,
    engine_override: str | None = None,
    skip_engines: frozenset[str] = frozenset(),
    workers: int = 0,
    keep_root: Path | None = None,
) -> MeritsReplayOutcome:
    """Provision every case at each moment, then run every routable predictor's cells.

    The cert back-test's engine replay (:func:`.cert_backtest.replay_predictors`)
    with a merits provisioner: the same routing, one lane per engine, the same
    loss accounting and the same read-back of ``prediction.json`` and
    ``flags.json``, with the probability read as P(disturbed). Every cell carries
    the replay clock: its docket Term as ``DECIDED_BEFORE`` and its cutoff as
    ``REPLAY_CUTOFF``.

    **One moment at a time**, in time order. A moment's cells are provisioned
    (:func:`provision_replay_cells`), copied under each engine lane's own root so
    no cell sits beside another engine's forecast, run, read back, and then
    removed from ``work_root`` before the next moment is provisioned. So a grant
    cell never has the briefed record of its own case on disk, and a briefed
    cell never has its own grant forecast there. Placement, not a wall: an
    engine with a shell can still read whatever else is on the machine.

    With ``keep_root``, each moment's forecasts (:func:`kept_forecasts`) are
    held in memory as its lane trees are removed, and written under
    ``keep_root/<lane>/<moment>/`` only once the last moment's cells have
    finished, so no forecast is on disk while a later moment's cells run.
    ``keep_root/run-id`` names the run those forecasts belong to. A
    ``keep_root`` that is not empty is refused at the start, and one found
    written to by the time the last moment ends gets nothing.

    An engine found missing, or whose quota is spent, at one moment is not
    invoked at the next: its predictors' remaining cells are recorded lost under
    the same reason, unattempted. A predictor that loses every cell keeps its
    (empty) place in ``predictions``, so the report shows it with nothing scored
    rather than leaving it out.
    """
    if keep_root is not None:
        _check_keep_root(keep_root, work_root)
    pairs = _runners_by_predictor(config_root, engine_override, skip_engines)
    ran_on = {p.id: (engine_override or str(p.engine), replay_model(r)) for p, r in pairs}
    engines = {pid: backend for pid, (backend, _) in ran_on.items()}
    ledger_root = get_settings().data_root.resolve()
    probe = ledger_root if ledger_root != work_root.resolve() else None
    by_case = {case.case_id: case for case in cases}
    predictions: dict[str, dict[Moment, dict[str, BacktestPrediction]]] = {
        p.id: {} for p, _ in pairs
    }
    unavailable: set[str] = set()
    exhausted: set[str] = set()
    lost: list[MeritsBacktestCellLoss] = []
    disclosures: list[tuple[Moment, CertBacktestDisclosure]] = []
    sweeps: list[MeritsReplaySweep] = []
    kept: dict[Path, bytes] = {}
    unkept: list[str] = []
    for moment in MERITS_BACKTEST_MOMENTS:
        staged = work_root / "provisioned"
        sweep = provision_replay_cells(conn, cases, staged, moments=[moment])
        sweeps.append(sweep)
        for predictor, _ in pairs:
            if predictor.id in unavailable or engines[predictor.id] not in exhausted:
                continue
            lost.extend(
                MeritsBacktestCellLoss(
                    predictor_id=predictor.id,
                    case_id=cell.case_id,
                    moment=moment,
                    reason="quota-exhausted",
                )
                for cell in sweep.cells
            )
        live = [
            (p, r) for p, r in pairs if p.id not in unavailable and engines[p.id] not in exhausted
        ]
        lanes = _engine_lanes(live, engines)
        lane_roots = {label: work_root / "lanes" / label for label, _ in lanes}
        provisioned = moment_root(staged, moment)
        for root in lane_roots.values():
            if provisioned.is_dir():
                shutil.copytree(provisioned, root)
            else:
                root.mkdir(parents=True)  # every cell of this moment was fenced
        shutil.rmtree(staged, ignore_errors=True)
        states = _run_lanes(
            lanes,
            _petitions(sweep, by_case, run_id=run_id, data_root=staged, ledger_root=probe),
            engines=engines,
            workers=workers,
            lane_roots=lane_roots,
        )
        for state in states:
            exhausted |= state.quota_exhausted
        merged = _merged(states)
        for predictor_id, found in merged.collected.items():
            predictions[predictor_id][moment] = found
        unavailable |= merged.unavailable
        lost.extend(
            MeritsBacktestCellLoss(
                predictor_id=loss.predictor_id,
                case_id=loss.case_id,
                moment=moment,
                reason=loss.reason,
            )
            for loss in merged.losses
        )
        disclosures.extend((moment, found) for found in merged.disclosures)
        for label, root in lane_roots.items():
            if keep_root is not None:
                found_files, refused = kept_forecasts(root, run_id)
                kept.update(
                    {Path(label, moment.value, rel): body for rel, body in found_files.items()}
                )
                unkept.extend(
                    f"{label}/{moment.value}/{rel}: a link, or over the size cap" for rel in refused
                )
            shutil.rmtree(root)
    if keep_root is not None:
        unkept.extend(_write_kept(keep_root, kept, run_id))
    return MeritsReplayOutcome(
        sweep=MeritsReplaySweep(
            cells=[cell for sweep in sweeps for cell in sweep.cells],
            fenced=[cell for sweep in sweeps for cell in sweep.fenced],
        ),
        predictions={
            pid: by_moment for pid, by_moment in predictions.items() if pid not in unavailable
        },
        ran_on=ran_on,
        unavailable=sorted(unavailable),
        lost_cells=lost,
        disclosures=disclosures,
        unkept=sorted(unkept),
    )
