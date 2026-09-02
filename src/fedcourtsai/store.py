"""Filesystem queries over the packed corpus and the derived-ledger tree.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists — which dockets the corpus tracks, which of their
predictable events are open or resolved — without an agent in the loop. Both the
case set and the event state are read from the packed corpus; the git tree under
``data/`` holds only the derived ledger (outcomes, predictions, evaluations).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel

from . import corpus, ids
from .integrity import (
    FORWARD_CLAIM_POLICY,
    PROCEDURAL,
    RETROSPECTIVE,
    ForwardClaimPolicy,
    StratifiedCell,
    cell_clock,
    classify_stratum,
    forward_claim_breach,
    latest_evaluation_runs,
)
from .paths import CasePaths
from .pipeline import moments
from .pipeline.moments import first_moment
from .process_version import FROZEN_SINCE, graded_post_freeze, is_frozen
from .schemas import (
    AgentFlags,
    AgentToolingFeedback,
    Evaluation,
    EventKind,
    ModelUsage,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    Stage,
    Stratum,
)
from .serialize import read_model


def iter_tracked_cases(corpus_db_path: Path) -> list[tuple[str, int]]:
    """Return ``(court_id, docket_id)`` for every case in the packed corpus.

    The corpus is the set of tracked dockets — a case enters it the first time
    ``pull`` ingests its docket. Returns nothing if the corpus does not exist
    yet (rather than creating an empty one as a side effect of reading).
    """
    if not corpus_db_path.exists():
        return []
    found: list[tuple[str, int]] = []
    with corpus.connect(corpus_db_path) as conn:
        for row in corpus.iter_rows(conn):
            court_id, _, docket_raw = row.case_id.partition("/")
            if docket_raw.isdigit():
                found.append((court_id, int(docket_raw)))
    return found


def _case_pair(case_id: str) -> tuple[str, int] | None:
    """Split a ``<court_id>/<docket_id>`` case id into a ``(court, docket)`` pair."""
    court_id, _, docket_raw = case_id.partition("/")
    return (court_id, int(docket_raw)) if docket_raw.isdigit() else None


def cases_due_for_pull(
    corpus_db_path: Path, *, limit: int, skip_closed: bool = True, eligible_reserve: int = 0
) -> list[tuple[str, int]]:
    """The ``(court, docket)`` cases ``pull`` should refresh this run, stalest first.

    The budget governor: returns at most ``limit`` cases from the active set in
    oldest-``last_pulled``-first order (skipping closed/resolved cases by
    default), so a run provably touches no more than ``limit`` dockets and a
    large active set rotates over successive days. ``eligible_reserve`` reserves
    up to that many slots for the stalest SCOTUS dockets so the in-scope
    set rotates ahead of the general active set (see
    :func:`fedcourtsai.corpus.rotation_for_pull`). Empty if the corpus does not
    exist yet (reading must not create it).
    """
    if not corpus_db_path.exists():
        return []
    with corpus.connect(corpus_db_path) as conn:
        rows = corpus.rotation_for_pull(
            conn, limit=limit, skip_closed=skip_closed, eligible_reserve=eligible_reserve
        )
    return [pair for row in rows if (pair := _case_pair(row.case_id)) is not None]


def open_events(
    corpus_db_path: Path,
    court_id: str,
    docket_id: int,
    *,
    backend: corpus.CorpusBackend | None = None,
) -> list[str]:
    """Event ids the corpus still tracks as unresolved (``resolved = 0``).

    The event-state seam reads from the packed corpus, where the ingestion channels
    record predictable events as raw facts: a case enters the corpus with its
    event(s) open, and outcome detection flips each event's ``resolved`` flag when
    it records that event's ``outcome.json``. ``run-predict`` targets the
    case-baseline subset of these — see :func:`forecastable_events`. Empty (not
    created) if the local corpus does not exist yet; ``backend`` selects the
    read backend (see :func:`corpus.connect_readonly`).

    A case the scope reconcile has latched **out of scope** (``predict_excluded``)
    yields no predictable events here — so a stale/unresolvable or
    inconsistent case is dropped at the source, not just at the read-time matrix
    gate. The reconcile clears the latch if the case ever returns to scope.
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return []
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        return open_event_ids(conn, court_id, docket_id)


def open_event_ids(conn: corpus.ReadConnection, court_id: str, docket_id: int) -> list[str]:
    """:func:`open_events` over an already-open connection.

    The connection-level seam, split out so the corpus query service — which
    holds one long-lived connection for its whole life — can serve the same
    read without reopening the corpus per request.
    """
    case_id = ids.case_id(court_id, docket_id)
    row = corpus.get_row(conn, case_id)
    if row is not None and row.predict_excluded:
        return []
    events = corpus.events_for_case(conn, case_id)
    return [event.event_id for event in events if not event.resolved]


# The event kinds the forward tournament forecasts unconditionally: the
# case-baseline disposition events. Three stage-keyed admissions sit beside
# this set in `forecastable_event_ids` — the cert-stage CVSG order minted on a
# still-pending petition, the interim-stage motion baseline of an application
# docket, and the merits-stage order event a cert grant mints — and all are
# conditional on the row, because the kind alone does not say which
# population the cell would be scored against. A motion on a *cert* docket is
# recorded and tracked but never queued for prediction: the prompt contract,
# the salience band, and the segment base rate are all conditioned on the cert
# petition, so a cell minted for it would be forecast and scored against a
# population it does not belong to.
_FORECASTABLE_KINDS = frozenset({EventKind.petition, EventKind.appeal})


def forecastable_events(
    corpus_db_path: Path,
    court_id: str,
    docket_id: int,
    *,
    backend: corpus.CorpusBackend | None = None,
    today: date | None = None,
) -> list[str]:
    """The subset of :func:`open_events` the predict fan-out may target.

    The case-baseline disposition kinds (petition, appeal), plus three
    stage-keyed admissions: the **cert-stage CVSG order** minted on a petition
    still awaiting disposition, the **interim-stage motion baseline** of an
    in-scope application docket, and the **merits-stage order event** minted on
    a case whose cert grant opened a merits proceeding. Every predict queue and
    the predict
    matrix's default-event resolution read this seam; evaluate, outcome
    detection, the rotation, and the corpus service keep the unfiltered
    :func:`open_events`, because an open motion event outside predict scope
    still needs its ground truth tracked — it just never earns a forecast cell.
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return []
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        return forecastable_event_ids(conn, court_id, docket_id, today=today)


def _premature_distribution_cell(event: corpus.CorpusEvent, row: corpus.CorpusRow | None) -> bool:
    """Whether this is a SCOTUS distribution-moment cell with no distribution yet.

    The information-set precondition the two cert-capable arms share: the
    petition baseline's moment is the **first distribution**, so a petition the
    Court has not yet distributed has no distribution-moment cell to mint — its
    docketing-time forecast belongs to the arrival moment, on the arrival
    event. One predicate rather than a per-arm condition, because
    :func:`forecastable_event_ids` admits on an or-chain and both the
    case-baseline arm and the cert-stage arm can reach a petition-kind cert
    event: a refusal applied in one arm alone is no refusal at all — the other
    arm re-admits exactly what it refused.

    Keyed on the declared **moment** where a declaration exists, not on the
    kind: the arrival event is petition-kind too, and it is *defined* at zero
    distributions — refusing it here would refuse the very cohort the moment
    exists for. An undeclared petition-kind event keeps the kind reading,
    which on a SCOTUS cert docket names the same distribution baseline.
    Non-SCOTUS rows have no distribution concept and are never premature.
    """
    if row is None or row.court != "scotus":
        return False
    if row.distributed_for_conference is not None or row.distribution_count:
        return False
    spec = moments.spec_for(event.event_id)
    if spec is not None:
        return spec.moment is Moment.distribution
    return event.kind == EventKind.petition


def _cert_forecastable(event: corpus.CorpusEvent, row: corpus.CorpusRow | None) -> bool:
    """Whether an event is a forecastable cert-stage moment of a pending petition.

    The cert admission: an event the register declares at the **cert stage**,
    on a scotus row that is neither an application docket nor already decided,
    whose declared moment's information set exists
    (:func:`_premature_distribution_cell`). In practice this arm carries the
    **CVSG order** and the **arrival moment** — the cert moments past the
    registry's first position (the arrival moment is chronologically the
    *earliest*; registry order is not chronology) — since the petition
    baseline the register also declares is already admitted by the
    case-baseline arm. The or-chain makes that overlap harmless only
    while nothing the baseline arm refuses can enter through this one, which
    is why the distribution-moment refusal is the shared predicate rather
    than the baseline arm's own condition: an or-chain routes around any
    refusal applied on one side alone.

    The form check mirrors the case-baseline arm's mislabeled-application
    refusal: a CVSG exists only on a cert docket, but admission is keyed on
    the row, not on the shape of an id.

    The decided-row refusal mirrors the merits arm's latched-judgment check,
    reading the same pair the cohort selection reads (``disposition`` /
    :func:`fedcourtsai.corpus.resolution_date`): a disposition latched while
    the docket's events await their outcome record would otherwise mint a
    cell per predictor, per day, that provisioning then refuses.

    Deliberately **no salience condition**, matching the baseline: the gate
    applies at the queue seams (predict scope, the live sweep), and a CVSG row
    is a sal-v1 carve-out — selection follows the very signal that minted this
    event.
    """
    return (
        _declares_forecastable(event, Stage.cert)
        and row is not None
        and row.court == "scotus"
        and not corpus.is_scotus_application_form(row.docket_number)
        and row.disposition is None
        and corpus.resolution_date(row) is None
        and corpus.out_of_scope_reason(row) is None
        and not _premature_distribution_cell(event, row)
    )


def _interim_forecastable(event: corpus.CorpusEvent, row: corpus.CorpusRow | None) -> bool:
    """Whether an event is the forecastable interim baseline of an in-scope case.

    The interim admission: a **motion-kind** event carrying the **interim
    stage**, on an **application-form** row the row-only scope rules keep in
    scope — which, per :func:`fedcourtsai.corpus.is_non_cert_scotus_form`,
    admits only an application whose latched ask reads substantive. The row
    check is what keeps an extension or unknown-ask application's baseline out
    of the fan-out even before the scope reconcile latches ``predict_excluded``
    on its row. Deliberately the **row-only** reason evaluator, not the
    connection-holding ``out_of_scope_reason_full``: the one rule the full
    evaluator adds (the bare opinion-import profile) cannot match an
    application row, and the caller's ``predict_excluded`` check already
    carries any snapshot-aware latch.

    The docket form is load-bearing, not redundant with the stage: a cert
    docket carries interim-stage events too — an entry-pinned stay or
    injunction motion filed on the petition's own docket — and a cert docket is
    squarely in scope, so the scope rules alone would admit one. Its cell would
    then freeze the *petition's* salience band as its conditioning, scoring an
    interim forecast against a cert population. Forecasting those motions is a
    later scope decision with its own baseline; until then the interim fan-out
    is the application docket, whose baseline the discovery mint stamps.
    """
    return (
        _declares_forecastable(event, Stage.interim)
        and row is not None
        and row.court == "scotus"
        and corpus.is_scotus_application_form(row.docket_number)
        and corpus.out_of_scope_reason(row) is None
    )


def _merits_forecastable(
    event: corpus.CorpusEvent, row: corpus.CorpusRow | None, today: date
) -> bool:
    """Whether an event is the forecastable merits event of a granted case.

    The merits admission: an **order-kind** event carrying the **merits
    stage**, on a row whose cert grant actually opened a merits proceeding, whose
    judgment is not already latched and whose proceeding is not recorded
    terminated, whose grant is not stale
    (:func:`fedcourtsai.corpus.is_stale_unparsed_grant` — the merits analogue
    of the petition stage's stale-Term refusal: a grant two Terms past with
    neither column latched is a decided docket the record never resolved, and
    a forward cell on it is a mislabeled backtest with unrestricted
    retrieval; the first post-freeze fan-out spent ~25 events' cells on
    exactly this class), and which the row-only scope rules keep in
    scope. The stage carries the event test — an order event of any other sort
    carries no stage at all — with the kind checked defensively beside it, since
    only the merits mint produces an order-kind event today and a second one
    would have to declare its own stage to reach here.

    The latched-judgment check is not redundant with the event's open flag: a
    parsed judgment whose entry carries no usable date surfaces for triage
    rather than resolving the event, so the row knows the case is decided while
    the event stays open. Without the check that docket mints a cell per
    predictor, per day, that provisioning then refuses.

    The terminated check is the same guard for the case that ends with no
    disposition at all — a post-grant Rule 46 dismissal, a dismissal as moot,
    an abatement on the petitioner's death, a grant the Court vacated, a docket
    whose only terminal notation is the mandate. Nothing will ever latch a
    judgment there, so an unlatched column alone would keep the event
    forecastable for the stale-grant bound's two Terms, and
    on a long-decided docket that is a forward cell on a case whose answer is
    already public. The column
    (``merits_terminated``, :mod:`fedcourtsai.pipeline.judgment`) is what makes
    the record refuse it rather than the scope latch.

    The row predicate is :func:`fedcourtsai.corpus.opens_merits_proceeding` —
    the same rule that mints the event, that the judgment backfill parses, and
    that the statpack merits section measures its disturbed rate over. Checking
    it here rather than trusting the event's existence is what keeps the
    forecast population and the baseline population one population when the two
    could drift: a docket re-resolved to ``gvr`` after its merits event was
    minted leaves the cert order carrying the disposition, so its judgment is a
    cert-stage fact the merits baseline excludes, and a cell forecasting it
    would be scored against a rate its own case is not in. (The baseline side
    applies one further predicate this side cannot: its pool guard excludes
    parsed judgments dated on their own grant — unreachable here, since a
    forecastable merits event requires ``merits_judgment`` unlatched, so the
    gap does not exist yet at admission time. The seam that survives: a
    stale-labeled cert-order vacatur whose event mints and is forecast before
    the poll latches its judgment would score a near-certain disturbance
    against a pool its own class was removed from — bounded by the latch
    window, and named in ``metrics/README.md`` rather than hidden here.)

    The scope rules narrow the forecast population *inside* the baseline's
    rather than matching it exactly, and the gap is not small: predict scope
    excludes IFP petitions, consolidated-out-of-scope members, and
    date-inconsistent rows, while :func:`opens_merits_proceeding` — and so the
    statpack merits section the baseline is pooled from — admits all of them.
    The IFP slice alone is roughly an eighth of the committed pack's plain
    grants, and it is the criminal/habeas end of the docket, whose disturbance
    rate has no reason to match the paid cohort's. So the merits baseline is
    measured over a population wider than the one forecast, which is the same
    shape ``docs/decision-model.md`` invokes to exclude GVRs; the honest
    resolution is a fee-class cut on the merits section, and until one lands
    the residue is stated rather than bounded. Admitting the excluded dockets
    instead is not the alternative — a merits cell on a docket the documented
    predict-scope exclusion refuses is a scope decision, not a fix.
    """
    return (
        _declares_forecastable(event, Stage.merits)
        and row is not None
        and row.merits_judgment is None
        and row.merits_terminated is None
        and corpus.opens_merits_proceeding(row)
        and not corpus.is_stale_unparsed_grant(row, today=today)
        and corpus.out_of_scope_reason(row) is None
    )


def _case_baseline_forecastable(event: corpus.CorpusEvent, row: corpus.CorpusRow | None) -> bool:
    """Whether a case-baseline event is the forecastable baseline of its case.

    The kind is necessary but not sufficient: an **application** docket whose
    baseline still reads petition-kind carries a mislabel, not a cert petition.
    Discovery mints an application's baseline as the interim-stage motion, but a
    row minted before that rule — or one the relabel pass has not reached — keeps
    the cert-shaped id, and admitting it would forecast a stay application under
    the cert contract, against a cert population, on the strength of a name.

    Keyed on the docket form rather than on the event's stage, because the
    mislabel predates the stage stamp: the rows that need excluding are exactly
    the ones carrying no stage at all. That makes forecastability correct on its
    own terms rather than conditional on a data migration having run — the
    migration changes which event is forecast, never whether a mislabeled one is.

    A **declared later moment sharing the baseline's kind** (the cert arrival
    event is petition-kind — the petition is the filing that opens it) must
    not ride this arm: admission here would bypass the register, making the
    ``forecastable`` switch-off inert and skipping the stage arm's decided-row
    refusal. So a declared non-first moment defers entirely to its stage's own
    arm, whatever its kind.

    And the baseline carries the information-set precondition on a SCOTUS
    cert docket (:func:`_premature_distribution_cell`, shared with the
    cert-stage arm so the or-chain cannot route around it): the moment is the
    **first distribution**, so a petition the Court has not yet distributed
    has no distribution-moment cell to mint — its docketing-time forecast is
    the arrival moment's, on the arrival event. Without this an
    arrival-selected petition would sweep premature baseline cells whose
    snapshots carry no conference at all, filed under a moment that has not
    happened. Non-SCOTUS dockets have no distribution concept and admit as
    before.
    """
    if event.kind not in _FORECASTABLE_KINDS:
        return False
    spec = moments.spec_for(event.event_id)
    if spec is not None and spec.ordinal != 0:
        return False
    if (
        row is not None
        and row.court == "scotus"
        and corpus.is_scotus_application_form(row.docket_number)
    ):
        return False
    return not _premature_distribution_cell(event, row)


def forecastable_event_ids(
    conn: corpus.ReadConnection,
    court_id: str,
    docket_id: int,
    *,
    today: date | None = None,
) -> list[str]:
    """:func:`forecastable_events` over an already-open connection.

    ``today`` anchors the merits arm's stale-grant bound; callers holding an
    injected clock (the live cycle threads one through routing and stamping)
    pass it so one cycle's decisions cannot straddle midnight, and tests pass
    a fixed date. ``None`` — the default the predict matrix and pull take —
    reads the wall clock, which is what a live queue decision means by now.
    """
    resolved_today = today if today is not None else date.today()
    case_id = ids.case_id(court_id, docket_id)
    row = corpus.get_row(conn, case_id)
    if row is not None and row.predict_excluded:
        return []
    events = corpus.events_for_case(conn, case_id)
    return [
        event.event_id
        for event in events
        if not event.resolved
        and (
            _case_baseline_forecastable(event, row)
            or _cert_forecastable(event, row)
            or _interim_forecastable(event, row)
            or _merits_forecastable(event, row, resolved_today)
        )
    ]


def resolved_events(
    corpus_db_path: Path,
    court_id: str,
    docket_id: int,
    *,
    backend: corpus.CorpusBackend | None = None,
) -> list[str]:
    """Event ids the corpus tracks as resolved (``resolved = 1``).

    The mirror of :func:`open_events`: an event whose ``outcome.json`` has been
    recorded is flipped resolved in the corpus, making it ready for
    ``run-evaluate``. Empty (not created) if the local corpus does not exist
    yet; ``backend`` selects the read backend (see
    :func:`corpus.connect_readonly`).
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return []
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        events = corpus.events_for_case(conn, case_id)
    return [event.event_id for event in events if event.resolved]


def unforecastable_listed_events(
    corpus_db_path: Path,
    court_id: str,
    docket_id: int,
    *,
    today: date,
    backend: corpus.CorpusBackend | None = None,
) -> dict[str, str]:
    """Why the corpus refuses each of a case's events, keyed by event id.

    The re-check for events a caller *lists* rather than selects: queue
    selection (:func:`forecastable_events`) applies every forecastability rule,
    but a trigger issue names its event ids, and replaying an old one bypasses
    selection entirely. This is the same refusal read back from the corpus at
    fan-out time, in the two classes that turn a queued event unforecastable
    while the issue waits:

    * **Resolved since queueing** — the event carries ``resolved = 1``. A
      trigger issue is written when its events are open and fanned out whenever
      the workflow runs, and a pipeline pause can put an arbitrary gap between
      the two.
    * **Merits proceeding no longer forecastable** — the row fails one of the
      row-level arms of the selection predicate (:func:`_merits_forecastable`):
      the grant no longer opens a merits proceeding (a docket re-resolved to
      ``gvr`` leaves the cert order carrying the disposition), a judgment or
      termination is latched while the event stays open for triage, or the
      grant is :func:`fedcourtsai.corpus.is_stale_unparsed_grant`. Each is a
      decided or non-existent proceeding a forward cell must not forecast, and
      for all of them this seam is load-bearing: provisioning's forward gate
      re-refuses only the latched-judgment and terminated arms, so the gvr and
      stale classes have no later backstop. The refusal is a property of the
      *proceeding*, not of one moment, so every declared merits moment is
      refused together — keyed per event id without consulting the events
      table, since a merits moment absent from the corpus is still a moment of
      the proceeding the listing names. ``today`` anchors the stale bound,
      passed by the caller so one run's decisions cannot straddle midnight.

    Where both classes apply the resolved reason wins, because it is the one
    that says what to do next (grade it). The row-only scope refusals
    (``predict_excluded``, out-of-scope) are not re-stated here — the scope
    gate drops those whole cases before event resolution. Empty (not created)
    if the local corpus does not exist yet; ``backend`` selects the read
    backend (see :func:`corpus.connect_readonly`).
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return {}
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        events = corpus.events_for_case(conn, case_id)
        row = corpus.get_row(conn, case_id)
    reasons = {
        event.event_id: "the corpus records it resolved (it closed since the run was queued)"
        for event in events
        if event.resolved
    }
    if row is not None:
        refusal = _merits_listing_refusal(row, today=today)
        if refusal is not None:
            for spec in moments.moments_for(Stage.merits):
                reasons.setdefault(spec.event_id, refusal)
    return reasons


def _merits_listing_refusal(row: corpus.CorpusRow, *, today: date) -> str | None:
    """Why a listed merits moment on this row is unforecastable, or ``None``.

    The row-level arms of :func:`_merits_forecastable`, read back as reasons;
    the arms must not drift apart, so any arm added there is owed here. The
    scope arm is deliberately absent (the scope gate drops those cases whole).
    """
    if row.merits_judgment is not None or row.merits_terminated is not None:
        return (
            "the corpus row already carries its merits outcome (a parsed judgment or a "
            "recorded termination held for triage), so a forward cell would forecast a "
            "decided docket"
        )
    if not corpus.opens_merits_proceeding(row):
        return (
            "the corpus row's grant no longer opens a merits proceeding (re-resolved so the "
            "cert order carries the disposition), so there is nothing left to forecast"
        )
    if corpus.is_stale_unparsed_grant(row, today=today):
        return (
            f"its cert grant is more than {corpus.STALE_GRANT_DAYS} days old with neither a "
            "parsed judgment nor a recorded termination, so the merits proceeding reads as a "
            "decided docket the record never resolved rather than a pending one"
        )
    return None


def event_recorded_closed(
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    events: Sequence[corpus.CorpusEvent],
) -> str | None:
    """Why the record already treats ``event_id`` as closed, or ``None``.

    The record-side half of the forward gate, split out from
    :func:`forward_refusal_reason` because it needs no corpus row: the committed
    ``outcome.json`` and the event's own ``resolved`` flag are both readable
    under every backend, including the casestore source that exposes events but
    not rows. Empty ``event_id`` (a caller that scoped no event) checks nothing
    here — the row-level decided check in :func:`forward_refusal_reason` covers
    that shape.
    """
    if not event_id:
        return None
    outcome_path = CasePaths(data_root, court_id, docket_id).event(event_id).outcome
    if outcome_path.is_file():
        return f"the ledger already records an outcome for {event_id}"
    found = next((e for e in events if e.event_id == event_id), None)
    if found is not None and found.resolved:
        return f"the corpus records {event_id} resolved"
    return None


def forward_refusal_reason_from_parts(
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    events: Sequence[corpus.CorpusEvent],
    row: corpus.CorpusRow | None,
) -> str | None:
    """Why the **record** says no forward cell may be minted for this event.

    The mechanical companion to the snapshot-text guard in provisioning
    (``_forward_leakage``): that one asks whether the provisioned payload
    *discloses* the outcome, this one asks whether the outcome *exists* — and a
    stale snapshot from a paused pipeline answers the first question with
    silence while the second still says no. Three checks, most specific first:
    the committed ``outcome.json`` and the corpus event's ``resolved`` flag
    (both via :func:`event_recorded_closed`), then the row's own latched
    outcome for the event's stage — the merits judgment for a merits moment,
    the disposition / resolution date for everything else. For the cert and
    merits stages that mirrors the decided-row refusals their forecastable
    predicates apply at queue time; for the interim and case-baseline shapes,
    whose queue predicates carry no decided-row arm, this gate is deliberately
    stricter — a latched disposition or resolution date is the record of an
    outcome whatever the queue seam asks. Deliberately **not** full
    :func:`forecastable_event_ids` membership: scope and selection are the
    plan seams' questions (the predict matrix re-asks them), and the corpus
    row legitimately lags its own snapshot — a merits cell provisioned on the
    grant order that opened it must not be refused because the row has not
    latched the grant yet. This gate asks only the question provisioning owns:
    does the record already hold this event's outcome?

    Pure over its inputs so provisioning can feed it the events and row it
    already read on its own connection (one connection per cell, and the
    ranged egress counters stay complete); :func:`forward_refusal_reason` is
    the connection-opening wrapper for callers that hold none.
    """
    closed = event_recorded_closed(data_root, court_id, docket_id, event_id, events)
    if closed is not None or row is None:
        return closed
    spec = moments.spec_for(event_id) if event_id else None
    if spec is not None and spec.stage is Stage.merits:
        if row.merits_judgment is not None:
            return "the corpus already latched the merits judgment"
        if row.merits_terminated is not None:
            # No disposition was ever entered, so no judgment can latch — but
            # the proceeding is over, and a forward cell on it would be
            # forecasting a question the docket already closed.
            return (
                "the corpus records the merits proceeding terminated without a "
                f"disposition ({row.merits_terminated})"
            )
    elif row.disposition is not None or corpus.resolution_date(row) is not None:
        return "the corpus records the case decided"
    return None


def forward_refusal_reason(
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    *,
    backend: corpus.CorpusBackend | None = None,
) -> str | None:
    """:func:`forward_refusal_reason_from_parts` over its own corpus read.

    Returns ``None`` when the record raises no objection — including when the
    local corpus is absent, where there is no record to consult (the snapshot
    read that precedes this in provisioning fails loudly on that shape anyway).
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return None
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        events = corpus.events_for_case(conn, case_id)
        row = corpus.get_row(conn, case_id)
    return forward_refusal_reason_from_parts(data_root, court_id, docket_id, event_id, events, row)


def event_has_claimable_prediction(
    data_root: Path, court_id: str, docket_id: int, event_id: str
) -> bool:
    """Whether the event holds a prediction in the process scope a new cell would join.

    The **comparability** gate on the predict sweep's cohort-completion
    carve-out, and the reason that carve-out is not simply
    :func:`fedcourtsai.matrix.event_has_predictions`. Completing a cohort is
    only worth spending on when the completed cohort is one a claimable board
    actually counts, and the board's scope is the frozen partition: `stratify`
    keeps a cell only where the scored predictor's *latest* prediction
    :func:`fedcourtsai.process_version.is_frozen`. A cell minted now is stamped
    with a blessed digest at a post-freeze instant and so lands in that
    partition — so completing an event whose existing cohort is entirely
    **unfrozen** does not finish a cohort at all: it manufactures an event on
    which one engine is scored and its rivals are structurally excluded, which
    is the differential-coverage shape a cross-engine claim may not be read
    over. The predicate refuses exactly that, and admits the case the carve-out
    exists for — an event whose cohort a board already counts, missing an engine.

    Keyed per predictor on the latest prediction — the right key *here*, where
    no evaluation exists yet to name a graded run, and exactly the fallback
    rule :func:`scored_prediction` gives an unstamped record — so this answers
    the question the board will ask rather than a near-miss of it. While no
    freeze is in force there is a single process scope and any committed
    prediction qualifies.
    """
    predictions_root = CasePaths(data_root, court_id, docket_id).event(event_id).predictions_dir
    by_predictor: dict[str, list[Prediction]] = {}
    for path in predictions_root.glob("*/*/prediction.json"):
        prediction = read_model(path, Prediction)
        by_predictor.setdefault(prediction.predictor_id, []).append(prediction)
    if FROZEN_SINCE is None:
        return bool(by_predictor)
    return any(
        is_frozen(max(runs, key=cell_clock).process_version) for runs in by_predictor.values()
    )


def iter_evaluations(data_root: Path) -> list[Evaluation]:
    """Every ``evaluation.json`` in the derived ledger, in stable path order.

    Walks ``data/cases/<court>/<docket>/events/<event>/evaluations/<evaluator>/
    <predictor>/<run>/evaluation.json`` and validates each against the schema, so
    a reader sees only well-formed rows. Returns nothing if the ledger does not
    exist yet (reading must not create it).

    Deliberately **uncollapsed**, unlike :func:`stratify`: its caller is the ops
    report's leakage digest, an all-versions diagnostic whose subject is what
    each grading recorded, so a superseded run is evidence rather than a
    duplicate. Nothing that scores a predictor reads the ledger this way.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    pattern = "*/*/events/*/evaluations/*/*/*/evaluation.json"
    return [read_model(path, Evaluation) for path in sorted(cases_dir.glob(pattern))]


def _declares_forecastable(event: corpus.CorpusEvent, stage: Stage) -> bool:
    """Whether ``event`` is a declared, fan-out-eligible moment of ``stage``.

    The kind/stage pair an admission used to spell out, read off the register
    instead — so adding a moment is a table row rather than an edit to every
    predicate that has to admit it, and a declared-but-switched-off moment
    (``forecastable=False``) stays out of the fan-out without a second flag
    anywhere.
    """
    spec = moments.spec_for(event.event_id)
    return (
        spec is not None
        and spec.stage is stage
        and spec.forecastable
        and event.stage == stage
        and event.kind == spec.kind
    )


def normalized_stage(kind: EventKind, stage: Stage | None) -> Stage | None:
    """The decision standard a cell reads as, normalizing an unrecorded stage.

    A missing or null stage on a petition/appeal-kind event reads as **cert** —
    the case-baseline kinds resolve on the cert standard by construction — while
    a null stage on any other kind stays no-stage, since nothing says which rule
    would govern. The twin of :func:`normalized_moment` on the other axis, and
    one rule in one place: the stratified boards and every surface that captions
    a number by its stage have to agree about what a null means, or the same cell
    reads as two different populations.
    """
    if stage is None and kind in _FORECASTABLE_KINDS:
        return Stage.cert
    return stage


def normalized_moment(stage: Stage | None, moment: Moment | None) -> Moment | None:
    """The forecast moment a cell reads as, normalizing an unrecorded one.

    A record written before the moment axis existed carries none, and its event
    is by construction the stage's **first** moment — there was no second one to
    be. Normalizing here rather than back-filling the record follows the stage
    rule directly above: the join decides what a legacy artifact reads as, and
    the artifact keeps saying only what its writer knew.
    """
    return moment if moment is not None else (first_moment(stage) if stage is not None else None)


class ExcludedCell(NamedTuple):
    """A scored cell the forward-claim rule kept out of every stratum."""

    evaluation: Evaluation
    reason: str


def scored_prediction(
    event_dir: Path, predictor_id: str, prediction_run_id: str | None
) -> Prediction | None:
    """The prediction an evaluation graded, or ``None`` where the predictor wrote none.

    The one join rule every evaluation reader shares — the stratified boards,
    the leaderboard's agreement views, the stamp-time computations, and the
    ``validate`` gates all resolve through here, so no two enforcers of one
    rule can score different predictions. A harness-stamped
    ``prediction_run_id`` names the graded run outright; a record stamped
    before the field existed — or one naming a run whose artifact is gone, a
    state the append-only ledger does not produce and ``validate`` refuses —
    falls back to the predictor's **latest** prediction by
    :func:`fedcourtsai.integrity.cell_clock`, the historical rule the stamp
    exists to retire. The path is assembled inline because ``event_dir`` is a
    bare directory here, not a :class:`fedcourtsai.paths.EventPaths` — it
    mirrors the glob one line below.
    """
    if prediction_run_id is not None:
        named = event_dir / "predictions" / predictor_id / prediction_run_id / "prediction.json"
        if named.is_file():
            return read_model(named, Prediction)
    files = sorted(event_dir.glob(f"predictions/{predictor_id}/*/prediction.json"))
    predictions = [read_model(p, Prediction) for p in files]
    return max(predictions, key=cell_clock) if predictions else None


class _ScopedCell(NamedTuple):
    """One in-scope ``evaluation.json`` with the siblings its stratum needs.

    :func:`stratify`'s first pass: the record, the event directory its path
    identifies, and the scored prediction the frozen gate already resolved —
    carried so the run collapse can drop a superseded grading before the
    outcome join, and so the survivor's prediction is not read twice.
    """

    evaluation: Evaluation
    event_dir: Path
    scored_prediction: Prediction


class StratifiedRun(NamedTuple):
    """:func:`stratify`'s result: the scorable cells, and what was excluded.

    ``claimed_forward`` is the breach check's denominator: in-scope cells whose
    harness record carried a forward-claiming context at all — what tells "no
    claim breached" apart from "nothing recorded a claim to check".

    ``superseded`` is how many in-scope gradings the run collapse dropped —
    the only place a re-grade is still countable. Every cell in ``cells`` is a
    survivor, so without this the operation leaves no trace on anything built
    downstream; the leaderboard publishes it so a standing that moved because a
    cell was re-graded says so. Counted **after** the scope gate, exactly where the
    collapse runs, so it is always "superseded within this scope" and never
    mixes a re-grade the scope excludes into a scoped board's audit line.
    """

    cells: list[StratifiedCell]
    excluded: list[ExcludedCell]
    claimed_forward: int = 0
    superseded: int = 0


def stratify(
    data_root: Path,
    *,
    frozen_only: bool = True,
    policy: ForwardClaimPolicy = FORWARD_CLAIM_POLICY,
) -> StratifiedRun:
    """Every evaluation joined to its stratum, stage, and forecast moment, in path order.

    For each ``evaluation.json``, reads the scored predictor's prediction(s) for
    the same event and the event's ``outcome.json`` — all committed artifacts, so
    the split is deterministic and offline — and classifies the cell forward vs
    retrospective (:func:`fedcourtsai.integrity.classify_stratum`), on the
    prediction's **harness clock** (:func:`fedcourtsai.integrity.cell_clock` —
    the process stamp, with the agent-written ``created_at`` only as the
    unstamped fallback: the stratum boundary is a pre-registration boundary and
    must not rest on a clock the agent controls). The clock that decides is
    the **scored** prediction's — the run the evaluation's harness-stamped
    ``prediction_run_id`` names (:func:`scored_prediction`) — so a predictor's
    later replay of an already-graded event cannot move the graded cell's
    stratum in either direction. A record stamped before the field existed
    falls back to the predictor's **latest** prediction's clock: the
    conservative reading for an ambiguous join, since it never presents a
    possibly post-resolution prediction as a forward forecast. An
    evaluation can only exist for a resolved event with a real prediction (the
    referential checks enforce both), so a missing sibling artifact raises
    rather than guessing a stratum.

    **One grading per cell per judge.** A re-graded cell commits a second
    ``evaluation.json`` beside the first, and both describe one observation, so
    the scoped records are collapsed on ``(case, event, predictor, evaluator)``
    — newest by harness clock
    (:func:`fedcourtsai.integrity.latest_evaluation_runs`) — before anything is
    joined or counted. Every surface built on this stream inherits the collapse,
    so no board, claim aggregate, or exclusion count can double-count a
    re-grade. The collapse never reaches across evaluators: a panel of judges on
    one prediction is several observations, which is what the ``evaluators``
    counts and the agreement views measure. It runs **after** the scope gate
    below, so a re-grade outside the scope cannot displace the in-scope grading
    it superseded — and how many gradings it dropped comes back as
    ``superseded``, since a survivor carries no mark of having superseded
    anything and the boards have nothing else to audit a re-grade from.

    A cell whose harness record **contradicts its own forward claim**
    (:func:`fedcourtsai.integrity.forward_claim_breach` — ``context.mode``
    says forward, the outcome existed when the harness ran it) is not a valid
    observation of any stratum. Under ``policy="exclude"`` (the pre-registered
    default) it lands in ``excluded`` and never in ``cells``; under
    ``policy="retrospective"`` it is forced into the retrospective stratum
    *and* still listed in ``excluded``, so both variants publish the same
    count and the boards' ``forward_claim`` block states which rule built
    them.

    The third element is the event's decision **stage**, read off its committed
    ``event.yaml`` and normalized for stratification: a petition/appeal-kind
    event with no recorded stage reads as **cert** — the case-baseline kinds
    resolve on the cert standard by construction — while a null stage on any
    other kind stays ``None`` (no stage, never guessed into one). The
    leaderboard segments its stage axis on this value.

    ``frozen_only`` (the default) keeps only cells whose latest prediction was
    produced by a **frozen** process (:func:`process_version.is_frozen`), so every
    surface built on this stream — the leaderboard and the ops dashboard both — is
    the frozen headline by construction and the two cannot disagree. It filters on
    the *prediction's* stamp, not the evaluation's digest: the competitor being
    ranked is the predictor. The scored prediction is the one the evaluation's
    harness-stamped ``prediction_run_id`` names — so a grading of a de-counted
    prediction stays attributed to that prediction and cannot ride a frozen
    re-run of the same cell into the counted figures — falling back, for
    records stamped before the field existed, to the predictor's latest
    prediction for the event. The evaluation's own **harness stamp**
    must additionally be at or after the freeze instant
    (:func:`process_version.graded_post_freeze` — its digest is recorded but
    not enforced): under the latest-prediction fallback, without the time gate
    a shakedown evaluation would ride into the frozen headline the moment the
    same predictor re-ran its event under the frozen process. An unstamped
    shakedown prediction is never frozen, so the shakedown ledger drops out
    for free.
    ``frozen_only=False`` is the all-versions view, which reproduces every
    scored cell regardless of process.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return StratifiedRun([], [], 0, 0)
    cells: list[StratifiedCell] = []
    excluded: list[ExcludedCell] = []
    claimed_forward = 0
    scoped: list[_ScopedCell] = []
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        # event_dir/evaluations/<evaluator>/<predictor>/<run>/evaluation.json
        event_dir = path.parents[4]
        scored = scored_prediction(event_dir, evaluation.predictor_id, evaluation.prediction_run_id)
        if scored is None:
            raise FileNotFoundError(
                f"{path} grades a predictor with no committed prediction on this "
                f"event — the referential checks refuse this ledger"
            )
        if frozen_only and not (
            is_frozen(scored.process_version) and graded_post_freeze(evaluation.process_version)
        ):
            continue
        scoped.append(_ScopedCell(evaluation, event_dir, scored))

    # The run collapse runs *after* the scope gate, never before: a cell graded
    # under the frozen process and re-graded outside it must keep the frozen
    # grading on the frozen board rather than lose the cell to a newer run the
    # board does not admit. Every counter below therefore sees one grading per
    # (case, event, predictor, evaluator).
    survivors = latest_evaluation_runs(scoped, lambda cell: cell.evaluation)
    # The one place a re-grade is still countable: every survivor below is
    # indistinguishable from a cell that was graded once, so the boards take
    # their audit line from this difference rather than re-scanning the ledger.
    superseded = len(scoped) - len(survivors)
    for evaluation, event_dir, scored in survivors:
        outcome = read_model(event_dir / "outcome.json", Outcome)
        # A mootness-basis outcome never enters the forward/retrospective
        # skill aggregates — the label tracks vacatur practice, not
        # cert-worthiness. Under the retrospective policy a breaching mootness
        # cell therefore routes procedural, not retrospective; under exclude
        # it is dropped like any breaching cell.
        procedural = outcome.disposition_basis == "mootness"
        if scored.context is not None and scored.context.mode == "forward":
            claimed_forward += 1
        breach = forward_claim_breach(scored, outcome)
        if breach is not None:
            excluded.append(ExcludedCell(evaluation, breach))
            if policy == "exclude":
                continue
            stratum: Stratum = PROCEDURAL if procedural else RETROSPECTIVE
        else:
            stratum = (
                PROCEDURAL
                if procedural
                else classify_stratum(cell_clock(scored), outcome.resolved_at)
            )
        event = read_model(event_dir / "event.yaml", PredictableEvent)
        stage = normalized_stage(event.kind, event.stage)
        cells.append((evaluation, stratum, stage, normalized_moment(stage, event.moment)))
    return StratifiedRun(cells, excluded, claimed_forward, superseded)


def iter_stratified_evaluations(
    data_root: Path, *, frozen_only: bool = True
) -> list[StratifiedCell]:
    """:func:`stratify`'s scorable cells alone, for a caller that needs no ledger.

    The cells-only seam; the boards call :func:`stratify` directly so the
    exclusion record they publish and the cells they aggregate come from one
    pass.
    """
    return stratify(data_root, frozen_only=frozen_only).cells


def ledger_cell_counts(data_root: Path) -> tuple[int, int, int]:
    """``(prediction cells, events predicted, predicted events resolved)``.

    The pipeline-funnel counts the ops substance section leads with, read
    straight off the committed ledger tree: every ``prediction.json`` is one
    cell; the distinct event directories those cells live under are the
    predicted events; a predicted event counts resolved once its
    ``outcome.json`` has landed beside them. Returns zeros when the ledger does
    not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return (0, 0, 0)
    prediction_files = sorted(cases_dir.glob("*/*/events/*/predictions/*/*/prediction.json"))
    # prediction path: <event_dir>/predictions/<predictor>/<run>/prediction.json
    event_dirs = {path.parents[3] for path in prediction_files}
    resolved = sum(1 for event_dir in event_dirs if (event_dir / "outcome.json").exists())
    return (len(prediction_files), len(event_dirs), resolved)


class PredictedEventRef(NamedTuple):
    """One predicted event in the committed ledger, cheap enough to enumerate all of.

    The selection index behind the daily prediction-reading digest: identity and
    the newest run that wrote under the event, read from the *path* alone so
    choosing which event to feature never parses hundreds of documents. The
    chosen one is then loaded in full by :func:`load_predicted_event`.
    """

    case_id: str
    event_id: str
    latest_run_id: str


def iter_predicted_events(data_root: Path) -> list[PredictedEventRef]:
    """Every event with at least one committed prediction, newest run first.

    ``latest_run_id`` is the newest run id under the event across all
    predictors; run ids are UTC timestamps, so descending lexical order is
    newest-first, and the ordering is total (case, then event) so two callers
    reading the same tree agree on "the newest event". Returns nothing if the
    ledger does not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    # <cases>/<court>/<docket>/events/<event>/predictions/<predictor>/<run>/prediction.json
    by_event: dict[tuple[str, str], str] = {}
    for path in cases_dir.glob("*/*/events/*/predictions/*/*/prediction.json"):
        event_dir = path.parents[3]
        docket = event_dir.parents[1].name
        if not docket.isdigit():
            continue
        key = (ids.case_id(event_dir.parents[2].name, int(docket)), event_dir.name)
        run_id = path.parent.name
        by_event[key] = max(by_event.get(key, ""), run_id)
    refs = [
        PredictedEventRef(case_id=case, event_id=event, latest_run_id=run)
        for (case, event), run in by_event.items()
    ]
    refs.sort(key=lambda ref: (ref.latest_run_id, ref.case_id, ref.event_id), reverse=True)
    return refs


class PredictionCell(NamedTuple):
    """One predictor's committed output for an event, documents included.

    ``reasoning`` / ``predicted_reasoning`` are the *text* of the documents the
    prediction names (``None`` where it names none, or where the named file is
    missing — ``validate`` refuses that state, so a reader reports the absence
    rather than failing on it). ``cell_path`` is the run directory spelled as
    ``data_root`` spells it — repo-relative under the default root, the same
    convention ``Prediction.input_snapshot`` records — which is what a digest
    links to for the full artifacts.
    """

    prediction: Prediction
    reasoning: str | None
    predicted_reasoning: str | None
    flags: AgentFlags | None
    cell_path: str


class PredictedEvent(NamedTuple):
    """A predicted event with every predictor's cell — the digest's whole input.

    ``event`` is the committed ``event.yaml`` definition, ``None`` when the
    ledger carries predictions under an event whose definition is absent (a
    state ``validate`` refuses, reported rather than crashed on).
    """

    case_id: str
    event_id: str
    event: PredictableEvent | None
    event_path: str
    cells: list[PredictionCell]


def _named_document(cell_dir: Path, name: str | None) -> str | None:
    """The text of the document a prediction names, or ``None``.

    Resolves the pointer under the same rule
    :func:`fedcourtsai.validate.check_prediction_docs` enforces — a plain
    filename beside the record, never a path and never a symlink — rather than
    trusting the gate to have run: this reader's output is published verbatim to
    a public issue, which is the one place a malformed pointer would be worth
    writing. A pointer that fails the rule, or a file that is absent or
    unreadable, reports as a missing document rather than raising.
    """
    if not name or Path(name).name != name or name in (".", ".."):
        return None
    path = cell_dir / name
    if path.is_symlink():
        return None
    try:
        return path.read_text()
    except OSError:
        return None


def load_predicted_event(data_root: Path, case_id: str, event_id: str) -> PredictedEvent | None:
    """Load one event's predictions and their documents, or ``None`` if it has none.

    The expensive half of the digest read, run once for the event
    :func:`iter_predicted_events` selected. Cells are ordered by predictor, then
    run, so the rendered document is stable across regenerations; a predictor
    with several runs contributes each of them, newest last.
    """
    pair = _case_pair(case_id)
    if pair is None:
        return None
    event_paths = CasePaths(data_root, *pair).event(event_id)
    files = sorted(event_paths.predictions_dir.glob("*/*/prediction.json"))
    if not files:
        return None
    cells: list[PredictionCell] = []
    for path in files:
        prediction = read_model(path, Prediction)
        cells.append(
            PredictionCell(
                prediction=prediction,
                reasoning=_named_document(path.parent, prediction.reasoning_doc),
                predicted_reasoning=_named_document(
                    path.parent, prediction.predicted_reasoning_doc
                ),
                flags=(
                    read_model(flags_path, AgentFlags)
                    if (flags_path := path.parent / "flags.json").is_file()
                    else None
                ),
                cell_path=path.parent.as_posix(),
            )
        )
    event_file = event_paths.event_file
    return PredictedEvent(
        case_id=case_id,
        event_id=event_id,
        event=read_model(event_file, PredictableEvent) if event_file.is_file() else None,
        event_path=event_paths.base.as_posix(),
        cells=cells,
    )


def iter_usage(data_root: Path) -> list[ModelUsage]:
    """Every ``usage.json`` in the derived ledger, in stable path order.

    Predict usage lives at ``predictions/<predictor>/<run>/usage.json`` and
    evaluate usage at ``evaluations/<evaluator>/<run>/usage.json``; both are
    matched and validated so a cost roll-up sees only well-formed rows. Returns
    nothing if the ledger does not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    patterns = (
        "*/*/events/*/predictions/*/*/usage.json",
        "*/*/events/*/evaluations/*/*/usage.json",
    )
    paths = sorted(path for pattern in patterns for path in cases_dir.glob(pattern))
    return [read_model(path, ModelUsage) for path in paths]


# The committed agent-artifact layout each stage writes, relative to data/cases:
# predict lives under a per-event prediction dir, evaluate under a per-event
# evaluator x run dir.
_PREDICT_GLOB = "*/*/events/*/predictions/*/*/{name}"
_EVALUATE_GLOB = "*/*/events/*/evaluations/*/*/{name}"


def iter_flags(data_root: Path) -> list[AgentFlags]:
    """Every committed ``flags.json`` in the derived ledger, in stable path order.

    A cell writes one only when it surfaced something to triage; predict flags live
    at ``predictions/<predictor>/<run>/flags.json`` and evaluate at
    ``evaluations/<evaluator>/<run>/flags.json``. All are matched and validated so the
    run-ops dashboard rolls up only well-formed records. Returns nothing if the
    ledger does not exist yet (reading must not create it).
    """
    return _iter_agent_artifact(data_root, "flags.json", AgentFlags)


def iter_tooling(data_root: Path) -> list[AgentToolingFeedback]:
    """Every committed ``tooling.json`` self-report in the ledger, in stable path order.

    Mirrors :func:`iter_flags` across the stages' layouts; the run-ops dashboard
    rolls these into the agent tooling-feedback digest. Returns nothing if the ledger
    does not exist yet (reading must not create it).
    """
    return _iter_agent_artifact(data_root, "tooling.json", AgentToolingFeedback)


def _iter_agent_artifact[T: BaseModel](data_root: Path, name: str, model: type[T]) -> list[T]:
    """Read every committed ``name`` agent artifact across all stages, validated."""
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    patterns = (
        _PREDICT_GLOB.format(name=name),
        _EVALUATE_GLOB.format(name=name),
    )
    paths = sorted(path for pattern in patterns for path in cases_dir.glob(pattern))
    return [read_model(path, model) for path in paths]
