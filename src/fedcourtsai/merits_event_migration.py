"""Converge already-granted dockets onto the open merits forecast events.

The live mint (:func:`fedcourtsai.pipeline.outcome.mint_moment_events`) opens a
case's merits events at cert-grant *detection*: the grant that closes the
petition event is also the birth of the judgment forecast. A docket whose grant
is already latched in the corpus without having passed through a live
resolution therefore carries no merits event, and the merits forecast stream
has no cell to mint for it. This sweep converges those dockets onto exactly the
events the live path mints, through the same construction and write seams
(:func:`~fedcourtsai.pipeline.outcome.merits_grant_event`,
:func:`~fedcourtsai.pipeline.outcome.briefed_merits_event_for`,
:func:`~fedcourtsai.pipeline.outcome.persist_moment_events`), so there is one
event shape and one idempotency story however a grant reached the corpus.

The population is **forward-only**: rows whose grant opens a merits proceeding
(:func:`fedcourtsai.corpus.opens_merits_proceeding` — a GVR or summary reversal
decides in the cert order and mints nothing, a granted application never enters
the merits docket) whose ``merits_judgment`` is not latched and whose
``merits_terminated`` is unset — the sweep's record that the proceeding ended
with no disposition, which closes the question just as a judgment does. A decided
grant leaves nothing to forecast, so it gets no event — minting one would open
a row the next detection pass immediately resolves, manufacturing a resolved
event no forecast ever attached to. The grant-moment event opens at the row's
``date_cert_granted``; where the respondent's merits brief is latched
(``merits_brief_filed``), the briefed moment is minted beside it, opened at the
brief date. A case already carrying an **open** grant event is topped up with
just the owed briefed moment (the brief can latch after the grant event was
minted, by this sweep or the live path); one whose grant event is *resolved*
is converged — the merits question is closed, whatever else the row reads.

``merits_judgment is None`` means *unlatched*, not *pending* — the judgment
sweep (``backfill-merits-judgments``) leaves the columns null on
really-decided dockets whose snapshot it could not parse or never saw — so a
mint additionally requires the docket to be shown still pending
(:func:`_pendency_conflict`): a stored snapshot must exist and its high-recall
judgment scan (:func:`~fedcourtsai.pipeline.outcome.snapshot_shows_judgment`,
the same guard forward provisioning applies) must be clean. That check is only
as good as the latch it complements, so run ``backfill-merits-judgments
--apply`` immediately before this sweep in the same corpus session — the
judgment columns must be as latched as the stored snapshots allow before
pendency is judged.

The mint deliberately applies **no predict-scope filter** — live-path
congruence, not oversight: an IFP grant mints its merits event exactly as the
live path would, and the fan-out's scope rules
(:func:`fedcourtsai.store.forecastable_event_ids`) refuse the cell, never the
event.

Four shapes are skipped and reported rather than minted, because folding them
would falsify the record: a case whose target event id already exists pinned to
a docket entry (that row is some *filing's* event, not the forecast moment —
the upsert would latch another filing's ``resolved`` state onto it), a case
with committed ledger artifacts under the target id that no corpus event row
backs (minting would adopt whatever the orphaned directory holds as the fresh
event's history), a case with no stored snapshot (pendency unverifiable), and
a case whose snapshot shows an unparsed judgment signal (possibly decided).
All land on the dry-run report for maintainer triage.

Deterministic (``case_id`` order), offline, idempotent — a second run finds
every in-population docket already carrying every event it is owed and mints
nothing.

:func:`backfill_event_moments` is the sibling sweep for the ``moment`` column
itself: a stage-carrying event row written without a moment reads downstream as
the stage's first moment, and the sweep materializes that reading into the
column (:func:`fedcourtsai.corpus.stamp_first_moments`).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from . import corpus
from .paths import CasePaths
from .pipeline import moments
from .pipeline.outcome import (
    MERITS_EVENT_ID,
    briefed_merits_event_for,
    merits_grant_event,
    persist_moment_events,
    snapshot_shows_judgment,
)
from .pipeline.prefetch import prefetch_by_case
from .schemas import Moment, Stage

#: The merits stage's briefed-moment event id, selected off the declared table
#: by moment name so an inserted moment can never silently re-point it.
BRIEFED_MERITS_EVENT_ID = next(
    spec.event_id for spec in moments.moments_for(Stage.merits) if spec.moment is Moment.briefed
)


@dataclass
class MeritsEventBackfillResult:
    """What the merits-event backfill minted (or would mint on a dry run)."""

    applied: bool = False
    minted: list[tuple[str, str]] = field(default_factory=list)  # (case_id, event_id) minted
    already_present: int = 0  # in-population cases already converged (nothing owed)
    decided: int = 0  # grants with a latched judgment or a recorded termination
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id, reason) for triage


@dataclass(frozen=True)
class _Owed:
    """The mint one in-population case is owed, pending its snapshot check.

    What the planning pass carries forward for a case it has not skipped: the
    pendency check is the only step needing the case's snapshot, so planning
    stops here and the snapshots for exactly these cases are prefetched
    together.
    """

    court_id: str
    docket_id: int
    to_mint: list[corpus.CorpusEvent]


def _ledger_orphan(data_root: Path, court_id: str, docket_id: int, event_id: str) -> bool:
    """Whether the git ledger holds artifacts under ``event_id`` for this case.

    Consulted only where the corpus carries no row for the id: a corpus-backed
    event's ledger directory is the normal committed shape, while an unbacked
    one holds artifacts under an identity this mint would silently adopt.
    """
    return CasePaths(data_root, court_id, docket_id).event(event_id).base.exists()


def backfill_merits_events(
    conn: sqlite3.Connection, data_root: Path, *, apply: bool
) -> MeritsEventBackfillResult:
    """Mint the open merits events onto each granted, still-undecided docket.

    Dry run by default (finds the rows, writes nothing); ``apply`` writes each
    case's events through
    :func:`fedcourtsai.pipeline.outcome.persist_moment_events` — corpus upsert
    first, ledger ``event.yaml`` second, the live mint's own order, so an
    interruption leaves the corpus authoritative and the next run converges
    the ledger. ``data_root`` is the git ledger root, consulted read-only for
    the orphaned-artifact skip (see the module docstring for both skip shapes).

    Runs in two passes because the pendency check's snapshot read is the pass's
    only expensive one and only a minority of the population reaches it: the
    planning pass walks every candidate serially over SQLite and the ledger,
    and only the cases it leaves owing a mint have their snapshots read —
    through :func:`~fedcourtsai.pipeline.prefetch.prefetch_by_case`, so where
    payload reads are offloaded that read is a bounded fan-out rather than a
    serial walk of GET latency. Fetching per candidate inside the planning walk
    would instead read the store for every SCOTUS grant, most of which are
    already decided or converged. Planning is complete before the first write,
    which is invisible to a pass that finishes — the plans are per-case and no
    case's plan reads another's events or ledger path — and decides what a pass
    that does not finish leaves behind: a snapshot read that raises (the content
    store refusing, rather than a case simply having none) aborts the sweep with
    no mint written at all, never a partial one. The sweep converges, so the
    next run re-derives the whole plan.
    """
    result = MeritsEventBackfillResult(applied=apply)
    records = conn.execute(
        "SELECT case_id FROM cases WHERE court = 'scotus' ORDER BY case_id"
    ).fetchall()
    # Every case that produces ordered output, in `case_id` order, as
    # `(case_id, reason-to-skip | mint-owed)`. The decided and already-
    # converged cases are counters, not output, so they end here.
    planned: list[tuple[str, str | _Owed]] = []
    for record in records:
        row = corpus.get_row(conn, str(record["case_id"]))
        if row is None or not corpus.opens_merits_proceeding(row):
            continue
        if row.merits_judgment is not None or row.merits_terminated is not None:
            result.decided += 1
            continue
        case_id = row.case_id
        court_id, _, docket = case_id.partition("/")
        if not docket.isdigit():
            planned.append(
                (case_id, "case id carries no numeric docket id, so it has no ledger path")
            )
            continue
        docket_id = int(docket)
        to_mint, skip_reason = _plan_case(conn, data_root, row, court_id, docket_id)
        if skip_reason is not None:
            planned.append((case_id, skip_reason))
            continue
        if not to_mint:
            result.already_present += 1
            continue
        planned.append((case_id, _Owed(court_id, docket_id, to_mint)))
    owed = [(case_id, plan) for case_id, plan in planned if isinstance(plan, _Owed)]
    # `latest_snapshot` never touches `conn` where payload reads are offloaded
    # (the registered source serves it, and its Protocol requires tolerance of
    # concurrent reads), which is what makes handing the call to the prefetch
    # pool's worker threads sound; the mode cannot flip mid-pass because
    # nothing here re-registers the source. Consumed inside the block and
    # reduced to each case's verdict rather than kept as payloads, so peak
    # retention stays the prefetch's own in-flight window; keyed by the
    # case id the prefetch yields with each payload, so the verdict cannot
    # drift onto another case — which would be a mint on a docket the pendency
    # check had refused.
    with prefetch_by_case(
        [case_id for case_id, _ in owed],
        lambda case_id: corpus.latest_snapshot(conn, case_id),
        thread_name_prefix="merits-events",
    ) as fetched:
        pendency = {case_id: _pendency_conflict(found) for case_id, found in fetched}
    for case_id, plan in planned:
        if isinstance(plan, str):
            result.skipped.append((case_id, plan))
            continue
        if (conflict := pendency[case_id]) is not None:
            result.skipped.append((case_id, conflict))
            continue
        result.minted.extend((case_id, event.event_id) for event in plan.to_mint)
        if apply:
            persist_moment_events(conn, data_root, plan.court_id, plan.docket_id, plan.to_mint)
    return result


def _plan_case(
    conn: sqlite3.Connection,
    data_root: Path,
    row: corpus.CorpusRow,
    court_id: str,
    docket_id: int,
) -> tuple[list[corpus.CorpusEvent], str | None]:
    """The events to mint for one in-population case, or the reason to skip it.

    ``([], None)`` means the case is already converged: its grant event exists
    and either is resolved or leaves no briefed moment owed. A non-``None``
    reason covers the whole case even where only the briefed target conflicts:
    minting the grant event beside a conflicting briefed row would hand triage
    a half-minted stage.

    Reads only SQLite and the ledger, never the case's snapshot: a non-empty
    mint is still conditional on :func:`_pendency_conflict`, which the caller
    applies once it has prefetched the snapshots of exactly the cases that got
    this far.
    """
    opened_at = row.date_cert_granted
    if opened_at is None:
        # Unreachable while `opens_merits_proceeding` requires the date; a skip
        # keeps a loosened guard loud on the triage report, never miscounted.
        return [], "merits-proceeding row carries no date_cert_granted to date the grant moment"
    events = {e.event_id: e for e in corpus.events_for_case(conn, row.case_id)}
    conflict = _target_conflict(events, data_root, court_id, docket_id, MERITS_EVENT_ID, "grant")
    if conflict is not None:
        return [], conflict
    existing_grant = events.get(MERITS_EVENT_ID)
    if existing_grant is not None and existing_grant.resolved:
        # A resolved grant event means the merits question is already closed,
        # so nothing is owed — whatever the row's judgment columns read.
        return [], None
    to_mint = [] if existing_grant is not None else [merits_grant_event(row, opened_at)]
    # The briefed moment's own guards (brief latched, judgment not latched,
    # merits-proceeding row) live in the shared seam; the open grant event it
    # requires is either the one this sweep is about to mint or the stored,
    # still-open row — so a case already carrying its grant event is topped up
    # with just the owed briefed moment.
    briefed = briefed_merits_event_for(row, [MERITS_EVENT_ID])
    if briefed is not None:
        conflict = _target_conflict(
            events, data_root, court_id, docket_id, BRIEFED_MERITS_EVENT_ID, "briefed"
        )
        if conflict is not None:
            return [], conflict
        if BRIEFED_MERITS_EVENT_ID not in events:
            to_mint.append(briefed)
    return to_mint, None


def _pendency_conflict(found: tuple[date, dict[str, Any]] | None) -> str | None:
    """The reason the docket cannot be shown still pending, or ``None``.

    The forward-only population keys on unlatched merits columns, which mean
    *unlatched*, not *pending*: the judgment sweep leaves them
    null on really-decided dockets whose snapshot it could not parse
    (``no_match``) or never saw (``no_snapshot``). Minting on that residue
    would open an event the predict cell refuses daily on a docket that is
    already decided — the ``no_match`` shape because the snapshot reads
    terminal, the ``no_snapshot`` shape because there is nothing to provision —
    with ``forecastable_event_ids`` re-admitting it every fan-out inside the
    stale-grant bound's two Terms, burning the cell's attempt cap each time. So a mint
    requires a stored snapshot whose high-recall judgment scan
    (:func:`~fedcourtsai.pipeline.outcome.snapshot_shows_judgment`, the same
    guard provisioning applies) is clean.

    ``found`` is that snapshot as :func:`fedcourtsai.corpus.latest_snapshot`
    (the judgment sweep's own read) returns it — supplied by the caller, which
    prefetches the population's snapshots together, so ``None`` here means the
    case has none stored.
    """
    if found is None:
        return (
            "no stored snapshot to verify pendency — run a pull and "
            + "backfill-merits-judgments first"
        )
    signal = snapshot_shows_judgment(found[1])
    if signal is not None:
        return (
            f"judgment columns unlatched but the {signal}; possibly decided "
            + "(the judgment sweep's no_match residue)"
        )
    return None


def _target_conflict(
    events: Mapping[str, corpus.CorpusEvent],
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    moment_name: str,
) -> str | None:
    """The reason ``event_id`` cannot be minted onto this case, or ``None``.

    The two conflicting shapes the module docstring names: an existing corpus
    row pinned to a docket entry (some filing's event, not the forecast
    moment), and committed ledger artifacts under the id that no corpus row
    backs. An existing un-pinned row is not a conflict — it is the already-
    minted event the population condition excludes.
    """
    existing = events.get(event_id)
    if existing is not None and existing.docket_entry_id is not None:
        return f"existing {event_id} row is entry-pinned, not the {moment_name} moment"
    if existing is None and _ledger_orphan(data_root, court_id, docket_id, event_id):
        return (
            f"committed ledger artifacts under {event_id} with no "
            + "corpus event row; minting would adopt them"
        )
    return None


@dataclass
class MomentBackfillResult:
    """What the moment stamp changed (or would change on a dry run), per stage."""

    applied: bool = False
    stamped: dict[str, int] = field(default_factory=dict)  # stage value -> rows stamped


def backfill_event_moments(conn: sqlite3.Connection, *, apply: bool) -> MomentBackfillResult:
    """Stamp each stage-carrying event row's null ``moment`` as the stage's first.

    A null ``moment`` already reads downstream as the stage's first moment, so
    the stamp changes no behavior — it materializes the reading into the column
    so moment-keyed grouping can read it directly. Stage-keyed off the declared
    table (:func:`fedcourtsai.pipeline.moments.first_moment`), written through
    the corpus's own writer (:func:`fedcourtsai.corpus.stamp_first_moments`).
    Idempotent; dry run by default (counts the rows, writes nothing).
    """
    result = MomentBackfillResult(applied=apply)
    for stage in Stage:
        moment = moments.first_moment(stage)
        if moment is None:
            continue
        if apply:
            count = corpus.stamp_first_moments(conn, stage, moment)
        else:
            count = int(
                conn.execute(
                    "SELECT COUNT(*) AS n FROM events WHERE stage = ? AND moment IS NULL",
                    (stage.value,),
                ).fetchone()["n"]
            )
        if count:
            result.stamped[stage.value] = count
    return result
