"""End-to-end local cascade: provision → predict → evaluate → validate, offline.

The repeatable, local form of the Phase-0 "one full cascade proven" milestone:
one command drives a single case through the whole derived-artifact pipeline over
the *fixture* corpus (or a real one — pulled locally, or queried in place
on the corpus remote via the ranged corpus backend) without GitHub Actions. It is the
iteration loop that otherwise only exists inside ``run-predict`` / ``run-evaluate``.

It reuses the production seams rather than reimplementing them: the engine-runner
seam (:mod:`fedcourtsai.pipeline.runner`) produces each predict/evaluate cell at
the canonical paths, the predictor/evaluator registries pick the actors, and the
packed corpus supplies the snapshot, the event definitions, and the ground truth.
With the default offline ``stub`` engine the whole cascade is deterministic and
network-free; the ``claude-code`` / ``codex`` engines drive the same cells through
the real headless agents against the identical contract, so a green local run
faithfully predicts a green CI run.

The steps mirror what ``run-predict`` / ``run-evaluate`` do around the agent call:

1. **Materialize** each target event's git ``event.yaml`` definition plus, for a
   resolved event, the ground-truth ``outcome.json`` the evaluator scores against
   (what ``materialize-event`` writes).
2. **Provision** each cell's gitignored ``record/`` through the shared
   :func:`fedcourtsai.provision.write_cell_record` seam — the snapshot placed at
   the event's declared moment, the ``context.json`` freezing the cell's mode and
   conditioning, and the documents cut with the snapshot, both staged copies
   through the contact-detail scrubs: exactly what ``provision-snapshot`` writes
   — then **predict** the event with every enabled predictor. Per cell, because
   the record *is* the cell's information set and two targets of one case
   declare two of them.
3. **Evaluate** every resolved target's predictions with every enabled evaluator,
   over a record re-provisioned the way ``run-evaluate`` provisions one (latest
   payload, no moment cut: a judge grades an event that has already resolved),
   bracketed by the blind-grading steps (:mod:`fedcourtsai.blinding`): the
   candidates are staged under opaque aliases before the agent runs and its
   output is un-aliased after, before ``validate``.
4. **Validate** the produced ledger (schema + git-only referential checks), the
   same gate CI runs on the resulting PR.

A docket is routed to the actors of its **population**, as the matrices route
it (:func:`fedcourtsai.prediction_slices.routing_population`): the Court's
fleet for every docket no enabled slice admits, and a slice's own actors for
a docket it lists. A slice docket is forecast on the trial stage's events
alone, one named event per run. Where the watchlist pass has not yet written
the event, the cascade can **rehearse** it (``rehearse_trial``): the docket's
events are planned in the run by the pass's own reader
(:func:`fedcourtsai.pipeline.trial_events.rehearse_docket`), read on the later
of today and the stage's switch-on day, and the named one is forecast from a
record provisioned as ``provision-snapshot`` provisions a forward trial cell.
The corpus is only read; the event exists in the run's data root and nowhere
else.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import yaml

from .. import corpus, ids, provision, store
from ..ai_watchlist import AI_WATCHLIST_FILENAME, load_ai_watchlist
from ..blinding import (
    latest_prediction_dirs,
    provision_blinded_predictions,
    unblind_evaluations,
)
from ..config import load_predict_config
from ..paths import CasePaths, EventPaths
from ..prediction_slices import SCOTUS_POPULATION_KEY, load_slices, routing_population
from ..registry import evaluators_for, predictors_for
from ..schemas import (
    AuthorshipTally,
    Judgment,
    Outcome,
    PredictableEvent,
    PredictorConfig,
    SameQuestionList,
    Stage,
    TrialRecord,
    UsageRole,
)
from ..serialize import write_json, write_yaml
from ..trial_adjudications import TRIAL_ADJUDICATIONS_FILENAME, load_trial_adjudications
from ..trial_local_rules import TRIAL_LOCAL_RULES_FILENAME, load_trial_local_rules
from ..validate import run_ledger_referential_checks, validate_ledger
from . import moments, same_question, trial_events, trial_record, vide_links, vided
from .documents import BIO_URL_JOIN, COMBINED_KINDS, select_documents, unheld_document_kinds
from .outcome import (
    NO_ORDER_MARKERS,
    OrderMarkers,
    build_merits_outcome,
    disposition_basis,
    forward_leakage,
    granted_flag,
    interim_resolution_signals,
    is_machine_readable,
    known_decision_method,
    read_order_markers,
    resolution_signals,
)
from .runner import Runner, RunRequest, get_runner


class CascadeError(RuntimeError):
    """The cascade cannot run as requested (missing corpus, case, or event)."""


@dataclass(frozen=True)
class CascadeReport:
    """What one ``local-cascade`` run produced, for the CLI to render.

    Not a schema artifact — a transient summary of the cell files written and the
    final ledger verdict, so a maintainer (or a test) can see the cascade ran end
    to end and produced a valid ledger.

    ``snapshot`` / ``context`` / ``documents`` describe the ``record/`` as the run
    left it, which is the last provisioning's: each one replaces the record, so
    these name what is on disk rather than everything that was ever written
    there. They are reported at all because a cell's inputs are the one thing a
    smoke run cannot re-derive afterwards — a missing ``context`` is exactly the
    gap a green cascade otherwise hides.

    ``placements`` is the part that survives that replacement: one row per
    provisioning, recorded as it happened. The end state alone would be
    misleading on any case with both an open and a resolved event — the evaluate
    half re-provisions last, so the surviving record is the *judge's*, and a
    reader of the final ``context.json`` would conclude every cell ran uncut.

    ``unforecastable`` names the ``forward`` targets the predict fan-out would
    not forecast (:func:`_unforecastable`).

    ``rehearsed`` names the targets planned in the run rather than read from
    the corpus's events (a trial rehearsal), and ``trial`` the
    ``record/trial.json`` the last provisioning wrote, where it wrote one.
    """

    case_id: str
    engine: str
    run_id: str
    snapshot: Path | None
    context: Path | None
    documents: tuple[Path, ...]
    placements: tuple[CellPlacement, ...]
    events: tuple[str, ...]
    unforecastable: tuple[str, ...]
    predictions: tuple[Path, ...]
    outcomes: tuple[Path, ...]
    evaluations: tuple[Path, ...]
    valid: bool
    problems: tuple[str, ...]
    rehearsed: tuple[str, ...] = ()
    trial: Path | None = None


def _select_events(events: list[corpus.CorpusEvent], event: str | None) -> list[corpus.CorpusEvent]:
    """The case's events to run: the one named, or all of them by default."""
    if event is not None:
        chosen = [e for e in events if e.event_id == event]
        if not chosen:
            available = ", ".join(e.event_id for e in events) or "none"
            raise CascadeError(f"event {event!r} is not defined for this case (have: {available})")
        return chosen
    if not events:
        raise CascadeError("the case has no predictable events in the corpus")
    return events


def _unforecastable(
    targets: Sequence[corpus.CorpusEvent], row: corpus.CorpusRow, forecastable: Sequence[str]
) -> list[str]:
    """The ``forward`` targets the predict fan-out would not forecast.

    ``forecastable`` is the :func:`fedcourtsai.store.forecastable_event_ids`
    answer. A target outside it — a distribution cell whose conference has sat,
    say — is one ``run-predict`` never mints: run here, it is placed at a moment
    that has already closed and may read filings after it, a cell shape
    production does not have. The cascade still runs it, since the engine
    smoke's case resolver does not screen on it, and names it so a summary over
    such a cell says so. A ``replay`` target is the local loop's replay of a
    decided event, which the fan-out's open-event test does not describe.
    """
    admitted = set(forecastable)
    return [
        e.event_id
        for e in targets
        if _cell_mode(e, row) == "forward" and e.event_id not in admitted
    ]


#: Which half of the cascade a provisioning served. The predict half places each
#: cell at the moment its event declares; the evaluate half provisions the case,
#: as ``run-evaluate`` does.
_Role = Literal["predict", "evaluate"]


@dataclass(frozen=True)
class CellPlacement:
    """What one provisioning handed one cell — the record as that cell saw it.

    Reported rather than inferred from the tree, because the tree holds only the
    last provisioning's record. ``role`` says which half of the cascade the
    provisioning served; ``event_id`` is empty for the evaluate half, which
    provisions the case rather than a moment. ``unheld`` names the document
    kinds the placed docket selects and the cell could be handed, but the
    content store does not hold at the selected link (:func:`_unheld_kinds`), so
    a missing filing shows in the report rather than only in the agent's flags.
    """

    role: _Role
    event_id: str
    mode: str
    provenance: str
    cutoff: date | None
    documents: int
    unheld: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Record:
    """The ``record/`` one provisioning left on disk, for the report to name."""

    snapshot: Path
    context: Path
    documents: tuple[Path, ...]
    placement: CellPlacement
    trial: Path | None = None


def _place_cell(
    case_id: str, event_id: str, read: provision.CellRead
) -> provision.Placement | None:
    """Where one cell is placed, refused here rather than at its write.

    Pure computation over a read already taken, so the cascade places every
    predict target before the first one runs: a moment that cannot be placed
    (an interim arrival whose opening entry cannot be anchored, or a moment
    whose trigger entry no stored payload carries —
    :class:`~fedcourtsai.provision.TriggerAbsent`) or a document
    kind that cannot name a file refuses the whole run before any token is
    spent, rather than after the earlier targets' cells have run.

    ``None`` where the corpus holds no snapshot for the case: there is nothing to
    place, and the cascade runs its cells on an empty record — the local analogue
    of the unprovisioned cell ``run-predict`` refuses, which ``require_record``
    turns into a refusal before this is reached. On that path nothing is written
    or cleared, as ``provision-snapshot`` writes nothing when it has no snapshot,
    so a dirty dev tree keeps whatever an earlier run left there and the report
    says ``context: not provisioned``.
    """
    if read.latest is None:
        return None
    snapshot_date, payload = read.latest
    try:
        placement = provision.place_at_moment(
            case_id,
            event_id,
            read.cutoff,
            read,
            payload=payload,
            snapshot_date=snapshot_date,
            documents=read.documents,
        )
        provision.screen_document_kinds(placement.documents)
    except provision.ProvisionError as exc:
        raise CascadeError(str(exc)) from exc
    return placement


def _provision_record(  # noqa: PLR0913
    case_paths: CasePaths,
    case_id: str,
    event_id: str,
    mode: str,
    read: provision.CellRead,
    role: _Role,
    placement: provision.Placement,
    related: Sequence[provision.RelatedRead] = (),
    *,
    authorship_tally: AuthorshipTally | None = None,
    same_question_list: SameQuestionList | None = None,
    anchor_pool: provision.AnchorPool | None = None,
    statpack_digest: str | None = None,
    trial: TrialRecord | None = None,
) -> _Record:
    """Write one cell's ``record/`` exactly as the workflow's provisioning step does.

    The snapshot placed at the cell's moment, the ``context.json`` that freezes its
    mode and conditioning, and the documents cut with the snapshot — through the
    same placement and writer ``provision-snapshot`` uses, contact scrubs,
    the ``Vide``-linked companions under ``record/related/``, a merits cell's
    authorship tally, a cert cell's same-question list and its frozen anchor,
    a forward trial cell's ``trial.json``,
    and the statpack build every predict cell was placed against, included. A
    cascade that wrote only the snapshot would hand the agent no frozen mode,
    band or cutoff, and the cell would have to guess the posture that
    provisioning exists to settle.
    """
    try:
        written = provision.write_cell_record(
            case_paths,
            case_id,
            placement,
            mode=mode,
            cutoff=read.cutoff,
            related=[
                provision.place_related(
                    item,
                    read.cutoff,
                    event=event_id,
                    mode=mode,
                    vintage=placement.snapshot_date,
                )
                for item in related
            ],
            authorship_tally=authorship_tally,
            same_question=same_question_list,
            anchor_pool=anchor_pool,
            statpack_digest=statpack_digest,
            trial=trial,
        )
    except provision.ProvisionError as exc:
        raise CascadeError(str(exc)) from exc
    return _Record(
        trial=case_paths.trial_record if written.trial is not None else None,
        snapshot=written.snapshot,
        context=case_paths.cell_context,
        documents=tuple(case_paths.document(doc.kind) for doc in placement.documents),
        placement=CellPlacement(
            role=role,
            event_id=event_id,
            mode=mode,
            provenance=placement.provenance,
            cutoff=read.cutoff,
            documents=len(placement.documents),
            unheld=_unheld_kinds(placement, read.documents, event_id),
        ),
    )


def _unheld_kinds(
    placement: provision.Placement,
    stored: Sequence[corpus.CaseDocument],
    event_id: str,
) -> tuple[str, ...]:
    """The kinds the placed docket selects that the store does not hold, for one cell.

    The freshness check's own test (:func:`unheld_document_kinds`) over the
    placed payload, so a filing after the cut is never counted, narrowed to the
    kinds the cell could be handed at all (:func:`provision.moment_admits_kind`):
    a withheld kind no cell reads is not a gap in this one. The selection reads
    the case's own docket, without a consolidation lead's merits filings.

    A combined kind (:data:`COMBINED_KINDS`) is held where its stored set
    contains every link the cut selects. The freshness test compares whole set
    keys, so a cell placed between two oppositions would otherwise read its
    stored set, which holds the later brief too, as a gap.
    """
    refs = select_documents(placement.payload)
    stored_urls = {document.kind: document.url for document in stored}
    unheld = unheld_document_kinds(refs, stored_urls)
    return tuple(
        kind
        for kind in unheld
        if provision.moment_admits_kind(kind, event_id)
        and not (
            kind in COMBINED_KINDS
            and kind in stored_urls
            and {ref.url for ref in refs if ref.kind == kind}
            <= set(stored_urls[kind].split(BIO_URL_JOIN))
        )
    )


def _read_related(
    db_path: Path,
    backend: corpus.CorpusBackend,
    case_id: str,
    placed: Mapping[str, provision.Placement | None],
) -> dict[str, tuple[provision.RelatedRead, ...]]:
    """Each placed target's related dockets, read as ``provision-snapshot`` reads them.

    Its ``Vide``-linked dockets, then those sharing one of its VIDED
    filings, off the payload each target was placed on, after every target is
    placed, on one connection opened only where some target has either.
    """
    linked = {
        event_id: (
            vide_links.vide_docket_numbers(placement.payload),
            vided.vided_keys(placement.payload) or [],
        )
        for event_id, placement in placed.items()
        if placement is not None
    }
    if not any(numbers or keys for numbers, keys in linked.values()):
        return {}
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        return {
            event_id: provision.read_related(
                numbers,
                own_case=case_id,
                resolve=lambda wanted: corpus.live_scotus_case_ids_by_docket_numbers(conn, wanted),
                snapshot=lambda linked_case: corpus.latest_snapshot(conn, linked_case),
            )
            + provision.read_vided(
                keys,
                own_case=case_id,
                linked=numbers,
                find=lambda wanted: corpus.vided_companions(conn, wanted, own_case=case_id),
                snapshot=lambda linked_case: corpus.latest_snapshot(conn, linked_case),
            )
            for event_id, (numbers, keys) in linked.items()
        }


def _read_authorship_tallies(
    db_path: Path,
    backend: corpus.CorpusBackend,
    placed: Mapping[str, provision.Placement | None],
    reads: Mapping[str, provision.CellRead],
    modes: Mapping[str, str],
) -> dict[str, AuthorshipTally]:
    """Each placed target's authorship tally, read as ``provision-snapshot`` reads it.

    On one connection opened only where the tally is not held back and some
    target's moment carries one.
    """
    wanted = [
        (event_id, placement)
        for event_id, placement in placed.items()
        if placement is not None and provision.carries_authorship_tally(event_id)
    ]
    if provision.AUTHORSHIP_TALLY_WITHHELD or not wanted:
        return {}
    found: dict[str, AuthorshipTally] = {}
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        for event_id, placement in wanted:
            try:
                tally = provision.authorship_tally_for(
                    conn,
                    event_id,
                    cutoff=reads[event_id].cutoff,
                    snapshot_date=placement.snapshot_date,
                    mode=modes[event_id],
                )
            except ValueError:
                # The cell goes without, as `provision-snapshot` provisions it.
                continue
            if tally is not None:
                found[event_id] = tally
    return found


def _read_same_question_lists(
    db_path: Path,
    backend: corpus.CorpusBackend,
    case_id: str,
    placed: Mapping[str, provision.Placement | None],
    reads: Mapping[str, provision.CellRead],
    modes: Mapping[str, str],
) -> dict[str, SameQuestionList]:
    """Each placed forward cert target's same-question list, as the plan job builds it.

    Read only where the list is not held back and some target carries one. An
    uncut cell's list is cut at the day after its snapshot, where the plan job
    cuts at the day after the plan: the cascade's fixture corpus has no today.
    """
    if provision.SAME_QUESTION_WITHHELD:
        return {}
    wanted = [
        same_question.CellCutoff(
            case_id=case_id,
            event_id=event_id,
            cutoff=reads[event_id].cutoff or placement.snapshot_date + timedelta(days=1),
        )
        for event_id, placement in placed.items()
        if placement is not None
        and modes[event_id] == "forward"
        and provision.carries_same_question(event_id)
    ]
    if not wanted:
        return {}
    with corpus.connect_readonly(db_path, backend=backend) as conn:
        petitions = same_question.read_petitions(conn)
    lists = same_question.cell_lists(same_question.QuestionFrame(petitions), wanted)
    return {item.event_id: item for item in lists.lists}


def _cell_mode(event: corpus.CorpusEvent, row: corpus.CorpusRow) -> str:
    """The mode a cascade cell runs in: ``forward`` unless the event is already over.

    The distinction the prompt contract keys its retrieval etiquette on, and the
    one thing an unprovisioned cell has to guess. An event is over when the
    corpus marks it resolved **or** its row records its stage decided
    (:func:`fedcourtsai.corpus.stage_shows_decided`): re-extraction never closes
    a stored event, so a moment detection declined stays open on a decided row,
    and its outcome exists all the same — which is exactly what ``replay``
    means. Every other target is a genuinely pending forecast, as
    ``run-predict`` provisions.
    Left to the cell, the guess defaults to ``forward``, so a cascade over a
    decided case would run a replay while its record claimed a live one.

    What a cascade replay cell does **not** get is the back-test's
    ``DECIDED_BEFORE`` clock, which masks the corpus priors a real replay cell may
    retrieve (``.github/prompts/predict.md``). The moment cut bounds its docket
    and its documents — the conditioning ``context.json`` records — but its priors
    are unmasked, which is the local loop's known narrowing against
    :mod:`fedcourtsai.cert_backtest`, the lane that produces scored replays.
    Nor is the lower-court filter of :mod:`fedcourtsai.merits_backtest` applied:
    a cascade replay cell on a decided case is handed whichever decision-below
    documents the fill happened to store before the case was decided.
    """
    decided = event.resolved or corpus.stage_shows_decided(row, event.stage)
    return "replay" if decided else "forward"


def _cell_read(
    conn: corpus.ReadConnection,
    case_id: str,
    event: corpus.CorpusEvent,
    events: list[corpus.CorpusEvent],
    found: tuple[date, dict[str, Any]] | None,
    documents: list[corpus.CaseDocument],
) -> provision.CellRead:
    """One predict target's provisioning inputs, with the dated snapshot its cut wants.

    Placed at the declared moment in **either mode**, the rule
    ``provision-snapshot`` follows too: a replay cell left uncut would read the
    latest payload and every stored document — the disposing order and the
    merits briefs included — under a ``context.json`` saying ``replay``, which is
    the shape of a correctly provisioned replay cell and none of its
    conditioning.

    A target whose moment has no dated trigger (``provision.moment_cutoff`` is
    ``None``) asks the corpus for no dated snapshot and takes no cut in either
    mode. That includes the cert petition baseline, whose opening date is
    docketing rather than the moment it declares, so a replay cell on a
    resolved one reads the latest payload and every stored document, the
    disposing order included — the narrowing the back-test's own point-in-time
    provisioner closes and this local loop does not.
    """
    cutoff = provision.moment_cutoff(event.event_id, events)
    return provision.CellRead(
        latest=found,
        documents=documents,
        events=events,
        row=None,
        cutoff=cutoff,
        dated=corpus.snapshot_at(conn, case_id, before=cutoff) if cutoff is not None else None,
    )


def _materialize_targets(
    case_paths: CasePaths,
    row: corpus.CorpusRow,
    targets: list[corpus.CorpusEvent],
    found: tuple[date, dict[str, Any]] | None,
) -> list[Path]:
    """The git ``event.yaml`` per target, and the ground truth for a resolved one.

    What ``materialize-event`` projects into the ledger, plus the outcome the live
    channel's resolution writer would have recorded — the cascade replays an event
    the corpus already marks resolved, so it builds that outcome from the stored
    row rather than from an open→resolved transition.

    The order-text markers come from the corpus's **latest** payload, never from
    whatever a cell was placed at: a cut snapshot is cut precisely at the order
    that resolved the event, so grading off it would read every resolved case as
    unassessed. With no stored snapshot they stay at their not-assessed defaults
    rather than being guessed from the row.
    """
    basis: Literal["standard", "mootness"] = "standard"
    order = NO_ORDER_MARKERS
    if found is not None:
        basis = disposition_basis(found[1])
        order = read_order_markers(
            found[1], disposition=row.disposition, date_cert_granted=row.date_cert_granted
        )
    outcomes: list[Path] = []
    for ev in targets:
        events = case_paths.event(ev.event_id)
        write_yaml(events.event_file, _event_definition(ev))
        if ev.resolved:
            outcome = _outcome_for_resolved(row, ev, basis, order=order)
            if outcome is not None:
                write_json(events.outcome, outcome)
                outcomes.append(events.outcome)
    return outcomes


def _provisioning_backend(backend: corpus.CorpusBackend | None) -> corpus.CorpusBackend:
    """Resolve and vet the backend for the cascade's *own* provisioning reads."""
    chosen = corpus.resolve_backend(backend)
    if chosen not in ("local", "ranged"):
        raise CascadeError(
            f"cascade provisioning reads need a local or ranged corpus backend, not "
            f"{chosen!r}; pass an explicit override (--corpus-backend on local-cascade) "
            "— the spawned agent still inherits the ambient corpus settings"
        )
    return chosen


def _routed_population(config_root: Path, case_id: str, *, rehearse: bool = False) -> str:
    """The population whose actors ``case_id``'s cells go to, as the matrices route it.

    An enabled slice's id for a docket its committed list names, the Court's
    population for every other docket
    (:func:`fedcourtsai.prediction_slices.routing_population`). ``rehearse``
    is refused on a docket of the Court's population, which has no trial event
    to plan.
    """
    try:
        slices = load_slices(config_root, load_predict_config(config_root).slices)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise CascadeError(f"cannot read the enabled prediction slices: {exc}") from exc
    population = routing_population(case_id, slices)
    if rehearse and population == SCOTUS_POPULATION_KEY:
        raise CascadeError(
            "--rehearse-trial plans a trial event on a docket an enabled prediction slice "
            f"admits; {case_id} is not one"
        )
    return population


@dataclass(frozen=True)
class _Days:
    """The two days a run reads on: today, and the day a rehearsal reads its docket."""

    today: date
    #: The later of today and the stage's switch-on day. The pass writes no
    #: trial event before :data:`~fedcourtsai.pipeline.moments.TRIAL_SWITCH_ON`,
    #: so a rehearsal run earlier reads the docket as the pass will on its
    #: first writing day.
    read_on: date

    @classmethod
    def on(cls, today: date) -> _Days:
        return cls(today=today, read_on=max(today, moments.TRIAL_SWITCH_ON))


def _select_predictors(
    config_root: Path,
    predictor: str | None,
    population: str = SCOTUS_POPULATION_KEY,
    case_id: str = "",
) -> list[PredictorConfig]:
    """The enabled predictors of ``population`` to fan out over: the one named, or all."""
    predictors = predictors_for(config_root / "predictors.yaml", population)
    if predictor is None:
        return predictors
    chosen = [p for p in predictors if p.id == predictor]
    if not chosen:
        available = ", ".join(p.id for p in predictors) or "none"
        routed = (
            f": {case_id} is routed to the {population!r} population's predictors"
            if case_id
            else ""
        )
        raise CascadeError(f"predictor {predictor!r} is not enabled (have: {available}){routed}")
    return chosen


def _route(
    config_root: Path, case_id: str, predictor: str | None, *, rehearse: bool, today: date | None
) -> tuple[str, list[PredictorConfig], _Days]:
    """The docket's population, its predictors the run fans out over, and the run's days.

    ``today`` is UTC today where the caller names none.
    """
    population = _routed_population(config_root, case_id, rehearse=rehearse)
    predictors = _select_predictors(config_root, predictor, population, case_id)
    return population, predictors, _Days.on(today or datetime.now(UTC).date())


def _rehearsal_plan(
    conn: corpus.ReadConnection, config_root: Path, case_id: str, read_on: date
) -> trial_events.DocketPlan:
    """The pass's plan for one slice docket read on ``read_on``, from a read-only connection.

    Beside the three committed files the pass itself is given: the watchlist,
    the districts' local rules and the adjudication list. A file that cannot be
    read refuses the run, as it stops the pass.
    """
    try:
        watchlist = load_ai_watchlist(config_root / AI_WATCHLIST_FILENAME)
        rules = load_trial_local_rules(config_root / TRIAL_LOCAL_RULES_FILENAME)
        adjudicated = load_trial_adjudications(config_root / TRIAL_ADJUDICATIONS_FILENAME)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise CascadeError(
            f"cannot rehearse {case_id}: {type(exc).__name__} reading the trial stage's config"
        ) from exc
    try:
        return trial_events.rehearse_docket(
            conn, case_id, watchlist, today=read_on, local_rules=rules, adjudicated=adjudicated
        )
    except trial_events.NotRehearsable as exc:
        raise CascadeError(f"cannot rehearse {case_id}: {exc}") from exc


def _why_not_planned(
    plan: trial_events.DocketPlan | None,
    stored: Sequence[corpus.CorpusEvent],
    event: str,
    read_on: date,
) -> str:
    """Why ``event`` is not a target on a slice docket, in the pass's own terms."""
    kept = next((e for e in stored if e.event_id == event), None)
    held = next((i for i in (plan.held_ruled if plan else ()) if i.event_id == event), None)
    if kept is not None and kept.resolved:
        why = "the corpus records it resolved, and a trial event is forecast only while open"
    elif kept is not None:
        why = "it is not a trial-stage event, and a slice docket is forecast on those alone"
    elif held is not None:
        why = f"the pass holds it and writes no event ({held.reason})"
    elif plan is not None and any(e.event_id == event for e in plan.would_open):
        why = f"its moment is not switched on by {read_on.isoformat()}"
    elif moments.trial_spec_for(event) is None:
        why = "no declared trial moment writes that id"
    elif plan is None:
        why = "the corpus holds no such event for the docket"
    else:
        why = f"the opener plans no such event on the docket as read on {read_on.isoformat()}"
    return why


def _slice_targets(
    conn: corpus.ReadConnection,
    config_root: Path,
    case_id: str,
    population: str,
    stored: Sequence[corpus.CorpusEvent],
    event: str | None,
    *,
    rehearse: bool,
    read_on: date,
) -> tuple[corpus.CorpusEvent, bool]:
    """The one trial event a slice docket's run forecasts, and whether it is a rehearsal.

    A slice docket is forecast on the trial stage's events alone
    (:func:`fedcourtsai.store.forecastable_event_ids`), so the stage-less
    baseline its row carries is never a target. The candidates are the open
    trial events the corpus stores and, under ``rehearse``, the events the pass
    would write on ``read_on`` (:func:`_rehearsal_plan`). Exactly one is run and
    it is named: a real engine spends on every cell. Refused, with the reason,
    where the corpus stores none and no rehearsal was asked for, where no event
    is named, and where the named one is held by the pass, already decided, or
    not planned at all.
    """
    open_stored = [
        e
        for e in stored
        if e.stage == Stage.trial
        and moments.trial_spec_for(e.event_id) is not None
        and not e.resolved
    ]
    plan = _rehearsal_plan(conn, config_root, case_id, read_on) if rehearse else None
    if plan is None and not open_stored:
        raise CascadeError(
            f"{case_id} is a docket of the {population!r} slice and the corpus holds no open "
            "trial event for it: the watchlist pass writes them from "
            f"{moments.TRIAL_SWITCH_ON.isoformat()}. Pass --rehearse-trial to plan the "
            "docket's events in the run, as the pass would, and forecast one without "
            "writing the corpus"
        )
    planned = [] if plan is None else plan.opens
    # A stored event the plan resolves today is one the pass closes, not one it
    # leaves open to forecast.
    closing = set() if plan is None else set(plan.outcomes)
    candidates = [(e, False) for e in open_stored if e.event_id not in closing] + [
        (e, True) for e in planned
    ]
    available = ", ".join(e.event_id for e, _ in candidates) or "none"
    if event is None:
        raise CascadeError(
            f"a slice docket's run forecasts one named event: pass --event (available on "
            f"{case_id}: {available})"
        )
    chosen = next((pair for pair in candidates if pair[0].event_id == event), None)
    if chosen is None:
        why = (
            "the resolver reads its result on the docket, so the pass closes it"
            if event in closing
            else _why_not_planned(plan, stored, event, read_on)
        )
        raise CascadeError(
            f"event {event!r} cannot be forecast on {case_id}: {why} (available: {available})"
        )
    return chosen


def _targets(  # noqa: PLR0913 - one docket, what the corpus holds for it, the run's knobs
    conn: corpus.ReadConnection,
    config_root: Path,
    row: corpus.CorpusRow,
    population: str,
    stored: list[corpus.CorpusEvent],
    event: str | None,
    found: tuple[date, dict[str, Any]] | None,
    *,
    rehearse: bool,
    read_on: date,
) -> tuple[list[corpus.CorpusEvent], tuple[str, ...], list[corpus.CorpusEvent]]:
    """The run's target events, the ids among them planned in the run, and the docket's events.

    The last is ``stored`` with a rehearsed target added: it is one of the
    docket's events for the rest of the run, though no corpus row holds it.

    The Court's population runs the named stored event or all of them
    (:func:`_select_events`). A slice docket runs one trial event
    (:func:`_slice_targets`), refused where its docket already shows the
    ruling (:func:`_refuse_decided_trial_cell`).
    """
    if population == SCOTUS_POPULATION_KEY:
        return _select_events(stored, event), (), stored
    target, planned = _slice_targets(
        conn,
        config_root,
        row.case_id,
        population,
        stored,
        event,
        rehearse=rehearse,
        read_on=read_on,
    )
    _refuse_decided_trial_cell(row.case_id, row.court, target, row, found)
    if not planned:
        return [target], (), stored
    return [target], (target.event_id,), [*stored, target]


def _trial_records(
    config_root: Path,
    case_id: str,
    placed: Mapping[str, provision.Placement | None],
    reads: Mapping[str, provision.CellRead],
    modes: Mapping[str, str],
    rehearsed: Sequence[str],
    days: _Days,
) -> dict[str, TrialRecord]:
    """Each placed forward trial target's ``trial.json``, as ``provision-snapshot`` builds it.

    The docket is read as of the cell's cutoff where it has one, else the day
    it is read on: today for a stored event, and for a rehearsed one the day
    the plan that opened it read the docket.
    """
    trials: dict[str, TrialRecord] = {}
    for event_id, placement in placed.items():
        if placement is None:
            continue
        try:
            built = trial_record.build_for_cell(
                config_root,
                case_id,
                event_id,
                placement.payload,
                read_on=reads[event_id].cutoff
                or (days.read_on if event_id in rehearsed else days.today),
                mode=modes[event_id],
            )
        except (OSError, ValueError, yaml.YAMLError) as exc:
            raise CascadeError(
                f"{case_id} trial record: {type(exc).__name__} reading config"
            ) from exc
        if built is not None:
            trials[event_id] = built
    return trials


def _refuse_decided_trial_cell(
    case_id: str,
    court: str,
    event: corpus.CorpusEvent,
    row: corpus.CorpusRow,
    found: tuple[date, dict[str, Any]] | None,
) -> None:
    """Refuse a slice docket's cell that ``provision-snapshot``'s forward gates would refuse.

    The record gate's row half and the snapshot-text gate
    (:func:`fedcourtsai.pipeline.outcome.forward_leakage`), over the latest
    payload: a trial cell is a forward cell or nothing, and one whose docket
    already shows the ruling would be handed its answer.
    """
    if _cell_mode(event, row) != "forward":
        raise CascadeError(
            f"event {event.event_id!r} cannot be forecast on {case_id}: the corpus records "
            "the case decided"
        )
    shown = None if found is None else forward_leakage(found[1], court, event.event_id)
    if shown is not None:
        raise CascadeError(f"event {event.event_id!r} cannot be forecast on {case_id}: {shown}")


def _outcome_for_resolved(
    row: corpus.CorpusRow,
    event: corpus.CorpusEvent,
    basis: Literal["standard", "mootness"] = "standard",
    *,
    order: OrderMarkers = NO_ORDER_MARKERS,
) -> Outcome | None:
    """Ground-truth :class:`Outcome` for an already-resolved event, or ``None``.

    ``pull``'s :func:`fedcourtsai.pipeline.outcome.detect_resolution` records an
    outcome for an event transitioning open→resolved; the cascade instead replays
    an event the corpus already marks resolved, so it builds the same outcome from
    the stored row without that open-event gate — but under the same **stage
    routing**: a merits-stage event takes the merits mapping from the row's
    ``merits_*`` columns (:func:`fedcourtsai.pipeline.outcome.build_merits_outcome`
    — the judgment axis, never the cert vocabulary), and every other event the
    cert-vocabulary mapping. Returns ``None`` when the row cannot carry the
    event's ground truth (an unreadable disposition, a missing decision date,
    or a merits event with no dated parsed judgment) — the unrecorded path,
    matching detection's rule so a guess is never recorded.
    """
    if event.stage == Stage.merits:
        if row.merits_judgment is None or row.merits_decided is None:
            return None
        try:
            # The stored column is blob-tolerant TEXT whose readers re-validate
            # against the vocabulary rather than failing the row (the field's
            # own contract); an out-of-vocabulary value degrades to the
            # unrecorded path, never a crash.
            judgment = Judgment(row.merits_judgment)
        except ValueError:
            return None
        return build_merits_outcome(
            row.case_id,
            event.event_id,
            judgment,
            row.merits_decided,
            distribution_count=row.distribution_count,
            cvsg_date=row.cvsg_date,
            source=row.citations[0] if row.citations else None,
            decision_method=known_decision_method(row.merits_decision_method),
        )
    if not (is_machine_readable(row.disposition) and row.date_decided is not None):
        return None
    assert row.disposition is not None  # narrowed by is_machine_readable above
    # Which signals block the outcome carries is keyed on the same tolerant
    # docket-form recognizer the live resolution path uses
    # (`pipeline.outcome._build_outcome`), and never both: the cert pair
    # (distribution count, CVSG) are observations nobody makes on an
    # application, and the interim escalation trio none nobody makes on a
    # petition.
    interim = row.court == "scotus" and corpus.is_scotus_application_form(row.docket_number)
    return Outcome(
        case_id=row.case_id,
        event_id=event.event_id,
        resolved_at=row.date_decided,
        actual_disposition=row.disposition,
        actual_granted=granted_flag(row.disposition),
        signals=None if interim else resolution_signals(row.distribution_count, row.cvsg_date),
        interim_signals=(
            interim_resolution_signals(
                row.application_kind,
                row.response_requested,
                row.referred_to_court,
                row.amicus_briefs,
            )
            if interim
            else None
        ),
        source=row.citations[0] if row.citations else None,
        disposition_basis=basis,
        disposition_route=None if interim else order.route,
        noted_dissent_from_denial=None if interim else order.dissent,
    )


def _event_definition(event: corpus.CorpusEvent) -> PredictableEvent:
    """The git ``event.yaml`` for a corpus event (the git-ledger analogue)."""
    return PredictableEvent(
        event_id=event.event_id,
        case_id=event.case_id,
        kind=event.kind,
        stage=event.stage,
        moment=event.moment,
        title=event.title or event.case_id,
        description=event.description,
        docket_entry_id=event.docket_entry_id,
        opened_at=event.opened_at,
        decision_target=event.decision_target,
        resolved=event.resolved,
    )


def _evaluate_event(  # noqa: PLR0913 - the cell coordinates, one arg each
    *,
    runner: Runner,
    request: Callable[[UsageRole, str, str, str], RunRequest],
    event_paths: EventPaths,
    data_root: Path,
    config_root: Path,
    court: str,
    docket: int,
    event_id: str,
    run_id: str,
    map_dir: Path,
    population: str = SCOTUS_POPULATION_KEY,
) -> list[Path]:
    """Score one resolved event with every enabled evaluator of its population, graded blind.

    The blind-grading bracket is the same one ``run-evaluate`` puts around its
    agent step (:mod:`fedcourtsai.blinding`): stage the candidates under opaque
    aliases first, un-alias the evaluator's output after. The local loop has to
    run the contract the evaluate prompt states, or a real-engine cascade reads a
    staging area that was never built — and the un-aliasing has to happen before
    ``run_cascade``'s closing ``validate``, since an alias resolves against no
    prediction and that is exactly the check which says so.

    Returns nothing for an event that is unresolved, or that no predictor
    produced a cell for: there is no ground truth to score against in the first
    case and nothing to score in the second.
    """
    if not event_paths.outcome.is_file() or not latest_prediction_dirs(event_paths):
        return []
    provision_blinded_predictions(
        data_root=data_root,
        config_root=config_root,
        court=court,
        docket=docket,
        event_id=event_id,
        run_id=run_id,
        map_dir=map_dir,
    )
    written: list[Path] = []
    for evaluator in evaluators_for(config_root / "evaluators.yaml", population):
        written.extend(
            runner.run(request(UsageRole.evaluator, evaluator.id, evaluator.prompt, event_id))
        )
        unblind_evaluations(
            data_root=data_root,
            config_root=config_root,
            court=court,
            docket=docket,
            event_id=event_id,
            evaluator_id=evaluator.id,
            run_id=run_id,
            map_dir=map_dir,
        )
    return written


def run_cascade(  # noqa: PLR0913 - the cell contract's independent knobs, one arg each
    *,
    corpus_db_path: Path,
    data_root: Path,
    config_root: Path,
    metrics_root: Path,
    court: str,
    docket: int,
    event: str | None = None,
    engine: str = "stub",
    run_id: str,
    predictor: str | None = None,
    backend: corpus.CorpusBackend | None = None,
    require_record: bool = False,
    rehearse_trial: bool = False,
    today: date | None = None,
) -> CascadeReport:
    """Run the full predict → evaluate → validate cascade for one case.

    Reads the case and its events from the packed corpus via the read-backend
    seam (:func:`fedcourtsai.corpus.connect_readonly`) — the local file by
    default, or the immutable blob in place on the corpus remote when the
    corpus-backend setting says ``ranged``, so a ranged-configured environment
    runs the cascade with no local pull. Materializes the git event/outcome
    definitions the agents read, provisions each cell's ``record/`` the way the
    workflow's provisioning step does (snapshot placed at the event's moment,
    ``context.json``, documents), fans the selected engine out over the enabled
    predictors then evaluators, and validates the resulting ledger. Returns a
    :class:`CascadeReport`. Raises :class:`CascadeError` for a missing
    corpus/case/event, for a moment whose opening entry cannot be anchored, and —
    under ``require_record`` — for a case with no stored snapshot; and
    :class:`fedcourtsai.pipeline.runner.EngineUnavailable` / ``EngineFailed`` for
    a real-engine problem.

    ``predictor`` narrows the predictor fan-out to one enabled id — a real
    engine spends real tokens, so a smoke run wants one cell, not three.
    ``require_record`` refuses, before any cell runs and so before any token is
    spent, a case the corpus holds no snapshot for: such a cell would run with no
    snapshot, no context and no documents, and a smoke that let it through would
    report green over exactly the gap it exists to detect.
    ``backend`` overrides the ambient corpus-backend setting for the cascade's
    *own* provisioning reads only. The split matters because the spawned agent
    inherits the ambient environment (minus credentials): a workflow can point
    the agent's retrieval at the corpus query sidecar (``service`` in the
    ambient env) while these in-process reads — which the service surface
    deliberately does not serve, and :func:`~fedcourtsai.corpus.connect_readonly`
    therefore rejects — go straight to the blob via ``ranged``.
    ``metrics_root`` is where the committed statpack is read, as
    ``provision-snapshot`` reads it: a cert cell's anchor is frozen from it, and
    every predict cell records its digest.

    The docket's population picks the actors (:func:`_routed_population`), and
    ``predictor`` must name one of that population's. A docket an enabled slice
    admits runs one named trial event (:func:`_slice_targets`), and
    ``rehearse_trial`` plans that event in the run where the corpus does not
    store it yet: read on the later of ``today`` (UTC today by default) and the
    stage's switch-on day, written to ``data_root`` as the pass would write it,
    and never to the corpus. It is refused on a docket of the Court's
    population, so a rehearsal cannot be mistaken for any other run.
    """
    runner = get_runner(engine)
    anchor_pool = provision.read_anchor_pool(metrics_root, config_root)
    case_id = ids.case_id(court, docket)
    case_paths = CasePaths(data_root, court, docket)
    # Before any corpus read: a predictor of another population, or a rehearsal
    # of a docket no slice admits, is a refusal that should cost nothing.
    population, predictors, days = _route(
        config_root, case_id, predictor, rehearse=rehearse_trial, today=today
    )

    chosen_backend = _provisioning_backend(backend)
    if chosen_backend == "local" and not corpus_db_path.exists():
        raise CascadeError(
            f"no corpus at {corpus_db_path}; run `fedcourts make-fixture-corpus` first"
        )

    with corpus.connect_readonly(corpus_db_path, backend=chosen_backend) as conn:
        row = corpus.get_row(conn, case_id)
        if row is None:
            raise CascadeError(f"case {case_id} is not in the corpus at {corpus_db_path}")
        all_events = corpus.events_for_case(conn, case_id)
        found = corpus.latest_snapshot(conn, case_id)
        targets, rehearsed, all_events = _targets(
            conn,
            config_root,
            row,
            population,
            all_events,
            event,
            found,
            rehearse=rehearse_trial,
            read_on=days.read_on,
        )
        # Before the remaining reads, not after: each cut target costs a
        # dated-snapshot lookup, and a refused run should pay for nothing more.
        if require_record and found is None:
            raise CascadeError(
                f"the corpus holds no snapshot for {case_id}, so every cell would "
                "run unprovisioned — no snapshot, no context.json, no documents "
                "(--require-record)"
            )
        unforecastable = _unforecastable(
            [ev for ev in targets if ev.event_id not in rehearsed],
            row,
            (
                store.forecastable_event_ids(
                    conn, court, docket, today=days.today, slice_docket=True
                )
                if population != SCOTUS_POPULATION_KEY
                else store.forecastable_event_ids(conn, court, docket)
            ),
        )
        stored_documents = corpus.documents_for_case(conn, case_id)
        # Every target's read on this one connection — the accounting rule
        # `provision-snapshot` follows, so a ranged cascade opens one connection
        # and its egress is the whole story.
        reads = {
            ev.event_id: _cell_read(conn, case_id, ev, all_events, found, stored_documents)
            for ev in targets
        }

    # What the last provisioning left on disk, which is what the report names: the
    # record holds exactly one cell's inputs at a time, and each provisioning below
    # replaces the previous one's.
    record: _Record | None = None
    placements: list[CellPlacement] = []

    def _place(
        event_id: str,
        mode: str,
        read: provision.CellRead,
        role: _Role,
        placement: provision.Placement | None,
    ) -> None:
        """Provision one cell's record, keeping both what is on disk and what was."""
        nonlocal record
        if placement is None:
            return
        record = _provision_record(
            case_paths,
            case_id,
            event_id,
            mode,
            read,
            role,
            placement,
            related.get(event_id, ()),
            authorship_tally=tallies.get(event_id),
            same_question_list=same_question_lists.get(event_id),
            anchor_pool=(
                anchor_pool
                if provision.freezes_cert_anchor(case_paths.event(event_id).event_file, event_id)
                else None
            ),
            # Predict cells only: the evaluate placement names no event, and
            # `provision-snapshot` records no build for it either.
            statpack_digest=(anchor_pool.digest if event_id and anchor_pool is not None else None),
            trial=trials.get(event_id) if role == "predict" else None,
        )
        placements.append(record.placement)

    # Every predict target placed before any cell runs, so a refusal costs
    # nothing (see `_place_cell`).
    placed = {ev.event_id: _place_cell(case_id, ev.event_id, reads[ev.event_id]) for ev in targets}
    related = _read_related(corpus_db_path, chosen_backend, case_id, placed)
    modes = {ev.event_id: _cell_mode(ev, row) for ev in targets}
    tallies = _read_authorship_tallies(corpus_db_path, chosen_backend, placed, reads, modes)
    same_question_lists = _read_same_question_lists(
        corpus_db_path, chosen_backend, case_id, placed, reads, modes
    )

    trials = _trial_records(config_root, case_id, placed, reads, modes, rehearsed, days)

    outcomes = _materialize_targets(case_paths, row, targets, found)

    def _request(role: UsageRole, actor: str, prompt: str, event_id: str) -> RunRequest:
        return RunRequest(
            role=role,
            court_id=court,
            docket_id=docket,
            event_id=event_id,
            actor_id=actor,
            run_id=run_id,
            prompt=Path(prompt),
            data_root=data_root,
        )

    predictions: list[Path] = []
    for ev in targets:
        # Per target, because the record IS the cell's information set and two
        # targets of one case declare two of them: run-predict provisions once per
        # cell, and a cascade that provisioned once for the whole case would run
        # the later moment's cell on the earlier one's record.
        _place(ev.event_id, _cell_mode(ev, row), reads[ev.event_id], "predict", placed[ev.event_id])
        for entry in predictors:
            request = _request(UsageRole.predictor, entry.id, entry.prompt, ev.event_id)
            predictions.extend(runner.run(request))

    # The evaluate half's record is a different one, and run-evaluate says how:
    # `provision-snapshot` with no --event, so no moment cut and the latest stored
    # payload, in the default `forward` mode. A judge reads the decided docket by
    # design — it is grading an event that has already resolved — where the
    # predict cells above were placed at the moment they forecast from. Only
    # where a ground truth was materialized: with none, no evaluate cell runs.
    if outcomes:
        uncut = provision.CellRead(
            latest=found,
            documents=stored_documents,
            events=[],
            row=None,
            cutoff=None,
            dated=None,
        )
        _place("", "forward", uncut, "evaluate", _place_cell(case_id, "", uncut))

    evaluations: list[Path] = []
    for ev in targets:
        evaluations.extend(
            _evaluate_event(
                runner=runner,
                request=_request,
                event_paths=case_paths.event(ev.event_id),
                data_root=data_root,
                config_root=config_root,
                court=court,
                docket=docket,
                event_id=ev.event_id,
                run_id=run_id,
                # Runner-local, beside the ledger rather than inside it, so a
                # local cascade over a real engine keeps the key out of the tree
                # the agent browses just as CI does.
                map_dir=data_root.parent / ".blinding",
                population=population,
            )
        )

    ledger = validate_ledger(data_root)
    references = run_ledger_referential_checks(data_root)
    problems = [*ledger.problems]
    for check in references:
        problems.extend(check.problems)

    return CascadeReport(
        case_id=case_id,
        engine=engine,
        run_id=run_id,
        snapshot=record.snapshot if record else None,
        context=record.context if record else None,
        documents=record.documents if record else (),
        placements=tuple(placements),
        events=tuple(ev.event_id for ev in targets),
        unforecastable=tuple(unforecastable),
        predictions=tuple(predictions),
        outcomes=tuple(outcomes),
        evaluations=tuple(evaluations),
        valid=ledger.ok and all(c.passed for c in references),
        problems=tuple(problems),
        rehearsed=rehearsed,
        trial=record.trial if record else None,
    )
