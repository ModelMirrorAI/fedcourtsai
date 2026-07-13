"""Outcome detection: turn a resolved docket into ``outcome.json`` (or surface it).

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
- **Surface otherwise.** Anything ambiguous — an unreadable/absent disposition,
  no decision date, or more than one open event the case-level disposition cannot
  be attributed to — produces an :class:`UnrecordedOutcome`, surfaced on the
  run's daily log for maintainer triage. Nothing is written on a guess.

The pure decision (:func:`detect_resolution`) is separated from the ledger write
(:func:`record_outcomes`) so the logic is testable without a filesystem.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import Disposition, Outcome, PredictableEvent
from ..serialize import write_json, write_yaml
from ..store import open_events
from .cert_signals import match_disposition_signal, mootness_disposition
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
    mean "decided, but we do not know how", which is the unrecorded path.
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
# row carries no decision date or disposition. Three families:
#   - appellate dockets CourtListener stopped indexing years ago
#     (``date_terminated`` stays null): the clerk's termination entry and the
#     published-opinion entry;
#   - SCOTUS terminal orders the cert-disposition resolver deliberately does not
#     match — an IFP denial that dismisses under Rule 39.8, an original/habeas
#     petition dismissal (many words separate "petition" from "dismissed"), and a
#     fee-default closure;
#   - SCOTUS decided-merits orders the resolver's grant-anchored patterns miss:
#     a vacate-and-remand disposition with no "grant" word ("Judgment VACATED
#     and case REMANDED for further consideration in light of ..."), and the
#     "Judgment Issued" entry that follows it (the mandate analog — on a SCOTUS
#     docket the matter is over once judgment issues).
# The two new shapes are anchored against pending-shaped near-misses: "judgment
# issued" is start-anchored (like "opinion issued") so a docketing recital
# ("NOTICE OF APPEAL filed from the judgment issued on ...") stays pending, and
# the vacate pair requires the disposition order's noun-verb shape — "judgment
# ... vacated ... remand" — so the SG's confession-of-error *motion* ("Motion of
# respondent to vacate the judgment and remand ... filed", verb before noun) and
# an en banc panel-opinion vacatur ("panel opinion is VACATED and the case is
# REMANDED to the panel", no judgment) stay pending too.
# This is a high-recall *routing* backstop that also feeds the forward-cell
# provisioning refusal (``provision-snapshot --refuse-terminal``): a match
# diverts a decided-looking case out of the forward-predict queue for triage
# (``predict_skipped_decided``), or leaves a fanned-out cell snapshot-less. It
# never records an ``outcome.json``, so — unlike broadening the resolving
# instrument (:func:`fedcourtsai.pipeline.cert_signals.match_disposition_signal`) —
# a false positive is cheap (a case parked for triage or one degraded cell, its
# events left open), not a fabricated ground truth. The initial IFP denial that
# only sets a fee deadline ("...is denied. Petitioner allowed until ... to pay")
# is deliberately *not* matched: that petition may still proceed on payment, so
# the later closure / dismissal entry — not the denial — is the terminal signal.
_TERMINAL_ENTRY_RE = re.compile(
    r"^opinion issued\b"
    r"|\bcase termination\b"
    r"|\bconsidered closed\b"
    r"|\brule\s*39\.8\b"
    r"|\bpetition\b.{0,80}?\bdismissed\b"
    r"|^judgment issued\b"
    r"|\bjudgment\b.{0,40}?\bvacated\b.{0,80}?\bremand\w*"
    # The cert-before-judgment denial/dismissal: a deliberate resolver miss
    # (its multi-word noun-verb gap would also admit the expedite-motion
    # recital), so routing is its only net. Start-anchored — the disposition
    # entry opens with the noun, while the expedite order opens with
    # "Motion ..." and must stay pending.
    r"|^petitions? for (?:a )?writs? of certiorari before judgment (?:are |is )?(?:denied|dismiss)",
    re.IGNORECASE,
)


def entry_descriptions(docket: Mapping[str, Any]) -> list[str]:
    """Every non-empty entry description in a docket payload, in docket order.

    Reads both payload shapes a stored snapshot can carry: the REST/mapped
    ``docket_entries`` list (``description`` / ``short_description``) and the
    raw supremecourt.gov ``ProceedingsandOrder`` list (``Text``) that the live
    channel stores verbatim as the point-in-time raw fact. The shapes are
    mutually exclusive per stored payload (each channel stores its own payload
    whole), so the concatenation order is immaterial in practice. Tolerates
    malformed entries (skipped, never raised) — the raw payload is unvalidated.
    """
    descriptions: list[str] = []
    for entry in docket.get("docket_entries") or []:
        if not isinstance(entry, Mapping):
            continue
        for key in ("description", "short_description"):
            description = str(entry.get(key) or "").strip()
            if description:
                descriptions.append(description)
                break
    for entry in docket.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        description = str(entry.get("Text") or "").strip()
        if description:
            descriptions.append(description)
    return descriptions


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
    Pure, over the fresh full-docket payload in either shape
    (:func:`entry_descriptions`). Used to keep decided-looking cases out of
    the forward-prediction queue — a forward cell on a decided case is a
    mislabeled back-test with unrestricted retrieval, so any predictor could
    trivially read the outcome.
    """
    descriptions = entry_descriptions(docket)
    last_description = descriptions[-1] if descriptions else ""
    if last_description and _TERMINAL_ENTRY_RE.search(last_description):
        return f"latest docket entry reads as terminal: {last_description!r}"
    return None


@dataclass(frozen=True)
class UnrecordedOutcome:
    """An open event that appears decided but cannot be recorded deterministically.

    Carried out of the library so the workflow can surface it on the run's
    daily log; ``reason`` explains why automatic recording was declined.
    ``reason`` must stay a fixed-vocabulary string (the literals in
    :func:`detect_resolution`, interpolating only closed-enum values): it is
    rendered into a GitHub issue comment, so raw docket text — e.g.
    :func:`termination_signal` output — must never route here.
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
    :class:`Outcome` to write; ``unrecorded`` lists the events left for triage.
    """

    outcomes: dict[str, Outcome] = field(default_factory=dict)
    unrecorded: tuple[UnrecordedOutcome, ...] = ()


def disposition_basis(docket: Mapping[str, Any]) -> Literal["standard", "mootness"]:
    """What drove the payload's disposition wording — the ``Outcome`` basis marker.

    Pure over the fresh full-docket payload (either shape, via
    :func:`entry_descriptions`), so the refresh channels compute it from the
    payload they already hold and pass it into :func:`resolve_case`. "mootness"
    when the first disposition-bearing entry is mootness practice
    (:func:`fedcourtsai.pipeline.cert_signals.mootness_disposition` — a
    Munsingwear vacatur or a dismissal as moot): the label then tracks vacatur
    practice rather than cert-worthiness, and scoring segments the cell into
    the leaderboard's procedural stratum. On the REST shape the recorded
    disposition can come from upstream fields or cert dates rather than entry
    text, so the basis attaches to the first disposition-bearing *entry* — the
    same first-entry rule the live resolver applies.
    """
    for text in entry_descriptions(docket):
        if match_disposition_signal(text) is not None:
            return "mootness" if mootness_disposition(text) else "standard"
    return "standard"


def _build_outcome(
    row: CorpusRow, event_id: str, basis: Literal["standard", "mootness"]
) -> Outcome:
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
        disposition_basis=basis,
    )


def detect_resolution(
    row: CorpusRow,
    court_id: str,
    docket_id: int,
    open_event_ids: list[str],
    disposition_basis: Literal["standard", "mootness"] = "standard",
) -> Resolution:
    """Decide how each open event resolves, given the refreshed corpus row.

    Pure: no I/O. Returns deterministic outcomes to write and unrecorded
    outcomes for the rest. An undecided docket, or one with no open events, resolves to an
    empty :class:`Resolution` (nothing to do).
    """
    if not open_event_ids or not appears_decided(row):
        return Resolution()

    readable = is_machine_readable(row.disposition) and corpus.resolution_date(row) is not None
    if readable and len(open_event_ids) == 1:
        event_id = open_event_ids[0]
        return Resolution(outcomes={event_id: _build_outcome(row, event_id, disposition_basis)})

    if not is_machine_readable(row.disposition):
        reason = "docket appears decided but its disposition is not machine-readable"
    elif corpus.resolution_date(row) is None:
        reason = "disposition is machine-readable but the docket carries no decision date"
    else:
        reason = (
            f"docket decided ({row.disposition}) but {len(open_event_ids)} events are open; "
            "the case-level disposition cannot be attributed to one event"
        )
    unrecorded = tuple(
        UnrecordedOutcome(
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
    return Resolution(unrecorded=unrecorded)


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
    disposition_basis: Literal["standard", "mootness"] = "standard",
) -> Resolution:
    """Detect and record resolution for one freshly-refreshed case.

    Reads the case's open events from the corpus (:func:`open_events`), decides
    each (:func:`detect_resolution`), writes the deterministic outcomes and closes
    their corpus events (:func:`record_outcomes`), and returns the full
    :class:`Resolution` so the caller can surface the unrecorded rest.
    """
    open_event_ids = open_events(corpus_db_path, court_id, docket_id)
    resolution = detect_resolution(row, court_id, docket_id, open_event_ids, disposition_basis)
    record_outcomes(corpus_db_path, data_root, court_id, docket_id, resolution)
    return resolution
