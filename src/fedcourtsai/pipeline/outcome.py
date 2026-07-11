"""Outcome detection: turn a resolved docket into ``outcome.json`` (or a reconcile ask).

This is ``pull``'s third job (see ``docs/data-pipeline.md``): once a refresh
re-ingests a docket through the shared core, decide whether any of the case's
**open** predictable events have now been decided, and record the ground truth
that ``run-evaluate`` scores against.

The corpus row carries only **case-level** facts — the docket's resolution
date (:func:`fedcourtsai.corpus.resolution_date`: the petition-stage cert date
on a SCOTUS docket, ``date_decided`` elsewhere) and a normalized
``disposition`` — so detection reasons at the case level and is deliberately
conservative:

- **Deterministic write.** When the docket appears decided, the disposition is
  *machine-readable* (a concrete :class:`Disposition`, not the ``other`` catch-all
  or ``None``), there is a decision date to stamp as ``resolved_at``, and the case
  has exactly **one** open event, the event's outcome is unambiguous: write
  ``outcome.json`` and mark the event resolved.
- **Reconcile otherwise.** Anything ambiguous — an unreadable/absent disposition,
  no decision date, or more than one open event the case-level disposition cannot
  be attributed to — produces a :class:`ReconcileRequest` so an agent (via a
  ``run:reconcile`` issue that ``run-pull`` files) confirms and records it by
  hand. Nothing is written on a guess.

The pure decision (:func:`detect_resolution`) is separated from the ledger write
(:func:`record_outcomes`) so the logic is testable without a filesystem.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import Disposition, Outcome, PredictableEvent
from ..serialize import write_json, write_yaml
from ..store import open_events
from .ingest import CorpusRow

# Dispositions that count as a granted (1) binary outcome; a partial grant still
# granted relief, so it lands on the granted side of the binary target.
_GRANTED: frozenset[Disposition] = frozenset({Disposition.granted, Disposition.granted_in_part})


def granted_flag(disposition: Disposition) -> int:
    """Project a disposition onto the binary ``actual_granted`` target (1=granted)."""
    return int(disposition in _GRANTED)


def is_machine_readable(disposition: Disposition | None) -> bool:
    """Whether a disposition is a concrete label we can record without a human.

    ``None`` (no disposition) and :attr:`Disposition.other` (the normalizer's
    catch-all for text it could not classify) are *not* machine-readable — they
    mean "decided, but we do not know how", which is the reconcile path.
    """
    return disposition is not None and disposition != Disposition.other


def appears_decided(row: CorpusRow) -> bool:
    """Whether the refreshed docket now looks resolved.

    A resolution date — the petition-stage cert grant/denial date on a SCOTUS
    docket, or the docket-level decision date (``date_terminated``/``date_decided``
    upstream) — or any disposition at all is the signal that the matter is no
    longer pending.
    """
    return corpus.resolution_date(row) is not None or row.disposition is not None


# Docket-entry descriptions that state the matter is over even when the docket
# row carries no decision date or disposition — common on appellate dockets
# CourtListener stopped indexing years ago (``date_terminated`` stays null):
# the clerk's termination entry and the published-opinion entry.
_TERMINAL_ENTRY_RE = re.compile(r"^opinion issued\b|\bcase termination\b", re.IGNORECASE)


def termination_signal(docket: Mapping[str, Any]) -> str | None:
    """A human-readable reason the fresh docket looks already decided, or ``None``.

    Complements :func:`appears_decided`, which keys on the normalized row's
    resolution date / disposition: a stale appellate docket often carries
    neither, yet its **latest** entry ("Case termination for order and
    judgment", "Opinion Issued") shows the matter is over. Only the last
    described entry counts — pendency is event-level, and a filing *after* a
    terminal entry (a stay-the-mandate motion, a rehearing petition) means the
    docket is active again, so an earlier terminal entry must not starve the
    later event. (A linked opinion cluster alone is deliberately not a signal
    here, matching :func:`fedcourtsai.corpus.snapshot_links_opinion_cluster`'s
    callers: a motions-panel opinion can publish on a still-pending appeal.)
    Pure, over the fresh full-docket payload. Used to keep decided-looking
    cases out of the forward-prediction queue — a forward cell on a decided
    case is a mislabeled back-test with unrestricted retrieval, so any
    predictor could trivially read the outcome.
    """
    last_description = ""
    for entry in docket.get("docket_entries") or []:
        for key in ("description", "short_description"):
            description = str(entry.get(key) or "").strip()
            if description:
                last_description = description
                break
    if last_description and _TERMINAL_ENTRY_RE.search(last_description):
        return f"latest docket entry reads as terminal: {last_description!r}"
    return None


@dataclass(frozen=True)
class ReconcileRequest:
    """An open event that appears decided but cannot be recorded deterministically.

    Carried out of the library so the workflow can open a ``run:pull`` reconcile
    issue; ``reason`` explains to the agent why automatic recording was declined.
    """

    case_id: str
    court_id: str
    docket_id: int
    event_id: str
    disposition: Disposition | None
    date_decided: date | None
    reason: str


@dataclass(frozen=True)
class Resolution:
    """The outcome of detection for one case in one refresh.

    ``outcomes`` maps each deterministically-resolved event id to the
    :class:`Outcome` to write; ``reconciles`` lists the events left for an agent.
    """

    outcomes: dict[str, Outcome] = field(default_factory=dict)
    reconciles: tuple[ReconcileRequest, ...] = ()


def _build_outcome(row: CorpusRow, event_id: str) -> Outcome:
    """Construct the ground-truth ``Outcome`` from a decided, machine-readable row.

    ``resolved_at`` is the :func:`corpus.resolution_date` — for a SCOTUS petition
    the cert-stage decision date, so a granted petition's outcome is stamped when
    cert was granted, not at the merits termination.
    """
    resolved_at = corpus.resolution_date(row)
    assert row.disposition is not None and resolved_at is not None
    return Outcome(
        case_id=row.case_id,
        event_id=event_id,
        resolved_at=resolved_at,
        actual_disposition=row.disposition,
        actual_granted=granted_flag(row.disposition),
        source=row.citations[0] if row.citations else None,
    )


def detect_resolution(
    row: CorpusRow,
    court_id: str,
    docket_id: int,
    open_event_ids: list[str],
) -> Resolution:
    """Decide how each open event resolves, given the refreshed corpus row.

    Pure: no I/O. Returns deterministic outcomes to write and reconcile requests
    for the rest. An undecided docket, or one with no open events, resolves to an
    empty :class:`Resolution` (nothing to do).
    """
    if not open_event_ids or not appears_decided(row):
        return Resolution()

    readable = is_machine_readable(row.disposition) and corpus.resolution_date(row) is not None
    if readable and len(open_event_ids) == 1:
        event_id = open_event_ids[0]
        return Resolution(outcomes={event_id: _build_outcome(row, event_id)})

    if not is_machine_readable(row.disposition):
        reason = "docket appears decided but its disposition is not machine-readable"
    elif corpus.resolution_date(row) is None:
        reason = "disposition is machine-readable but the docket carries no decision date"
    else:
        reason = (
            f"docket decided ({row.disposition}) but {len(open_event_ids)} events are open; "
            "the case-level disposition cannot be attributed to one event"
        )
    reconciles = tuple(
        ReconcileRequest(
            case_id=row.case_id,
            court_id=court_id,
            docket_id=docket_id,
            event_id=event_id,
            disposition=row.disposition,
            date_decided=row.date_decided,
            reason=reason,
        )
        for event_id in open_event_ids
    )
    return Resolution(reconciles=reconciles)


def record_outcomes(
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
    resolution: Resolution,
) -> list[str]:
    """Write each deterministic ``outcome.json`` and close its event in the corpus.

    The derived judgment (``outcome.json``) lands in the git ledger; the event's
    open/resolved state is a raw fact, so the matching ``CorpusEvent`` is flipped
    ``resolved`` in the packed corpus. The event's ``event.yaml`` is materialized
    beside the outcome from the same corpus row: an outcome committed without its
    event definition is a referential orphan the offline ``validate`` gate
    rejects, and unlike the agent cells (whose workflows run ``materialize-event``
    first) the deterministic writers commit straight from this working tree, so
    this is the only place that can guarantee the pair. Returns the event ids
    written, sorted. Idempotent: a resolved event is filtered out upstream by
    :func:`open_events` (which reads the same corpus flag), so a re-run never
    duplicates or overwrites a recorded outcome.
    """
    case = CasePaths(data_root, court_id, docket_id)
    case_id = ids.case_id(court_id, docket_id)
    written: list[str] = []
    with corpus.connect(corpus_db_path) as conn:
        events_by_id = {e.event_id: e for e in corpus.events_for_case(conn, case_id)}
        for event_id, outcome in sorted(resolution.outcomes.items()):
            event = events_by_id.get(event_id)
            if event is None:
                # Fail loud, before the outcome is written: an outcome without
                # its event definition is exactly the orphan the gate rejects,
                # and a resolution for an event the corpus does not hold is an
                # internal inconsistency (the open-events read and this write
                # use the same table), not upstream degradation.
                raise RuntimeError(
                    f"corpus holds no event {event_id!r} for {case_id}; "
                    "refusing to write an orphaned outcome"
                )
            write_json(case.event(event_id).outcome, outcome)
            write_yaml(
                case.event(event_id).event_file,
                PredictableEvent(
                    event_id=event.event_id,
                    case_id=event.case_id,
                    kind=event.kind,
                    title=event.title,
                    description=event.description,
                    docket_entry_id=event.docket_entry_id,
                    opened_at=event.opened_at,
                    decision_target=event.decision_target,
                    resolved=True,  # the outcome beside it is the resolution
                ),
            )
            # An event with a realized outcome is, by definition, resolved: close
            # it in the corpus so the next open_events read stops queuing it.
            corpus.set_event_resolved(conn, case_id, event_id)
            written.append(event_id)
    return written


def resolve_case(
    corpus_db_path: Path,
    data_root: Path,
    row: CorpusRow,
    court_id: str,
    docket_id: int,
) -> Resolution:
    """Detect and record resolution for one freshly-refreshed case.

    Reads the case's open events from the corpus (:func:`open_events`), decides
    each (:func:`detect_resolution`), writes the deterministic outcomes and closes
    their corpus events (:func:`record_outcomes`), and returns the full
    :class:`Resolution` so the caller can queue reconcile issues for the rest.
    """
    open_event_ids = open_events(corpus_db_path, court_id, docket_id)
    resolution = detect_resolution(row, court_id, docket_id, open_event_ids)
    record_outcomes(corpus_db_path, data_root, court_id, docket_id, resolution)
    return resolution
