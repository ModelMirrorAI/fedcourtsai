"""Converge committed cert outcomes against the disposition their docket text carries.

A ``granted`` label on a cert-stage outcome asserts what the order said, and the
committed ledger holds records the current parser reads differently: an order
that grants, vacates and remands in one breath — the prose GVR
(:func:`fedcourtsai.pipeline.cert_signals._gvr_tail_sentence`, reached through
:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`) — recorded
as a plain grant. Nothing else re-reads them: ``record_outcomes`` is
idempotent-by-filter, so a resolution pass never revisits a resolved event, and
the Munsingwear migration's predicate (``granted`` + a ``mootness`` basis)
cannot reach a record carrying no basis at all.

This sweep re-resolves them from the stored docket text and is **self-confirming**:
it relabels only where the parser, run over the snapshot's own disposing entry,
returns ``gvr``. No confirmation, no write — the outcome is reported with the
reason instead, so the dry run is the triage ledger.

**The era boundary is the whole separation, and it is in the predicate, not
just the prose.** A label is only a *parse gap* if the parser wrote it. From
:data:`PARSED_ORDER_TEXT_SINCE` forward, a cert disposition was recorded by
reading the docket's own order text, so a wrong label there is a gap in that
read and this sweep may correct it. Earlier resolutions were normalized from
upstream record fields and never passed through the disposition parser at all —
their ``granted`` is the older vocabulary's faithful record, which the
forward-convention rule in ``docs/salience.md`` protects, and relabeling one
would be the retroactive vocabulary flip that rule forbids. Those are reported,
never rewritten, and the boundary is enforced in code so that widening snapshot
coverage can never quietly reach them.

**Scored cells are held back by default.** An ``evaluation.json`` is stamped with
a ``correct`` bit computed from the outcome, so relabeling under a committed
evaluation puts a published bit out of step with the record it was scored
against. A candidate whose event directory holds committed predict or evaluate
output is skipped and reported unless ``include_scored`` says otherwise; when it
does, each relabel reports how many stamped evaluations it puts in the re-grade
backlog, which ``stamp-cell --regrade`` is the follow-through for.

Three fields move, and no others. ``actual_disposition`` takes the confirmed
label. ``disposition_basis`` takes the basis of the same matched entry, but only
ever **latches on**: ``gvr`` + ``mootness`` is the Munsingwear vacatur and
``gvr`` + ``standard`` the merits GVR, so a record already carrying ``mootness``
describes an order this sweep's single-entry read is not entitled to
re-characterize — keeping it is what stops a Munsingwear sitting committed as a
merits GVR. ``disposition_route`` advances to ``gvr`` **where a route was
already assessed**, because the marker is derived from the label —
:func:`fedcourtsai.pipeline.outcome.disposition_route` returns ``gvr`` for any
``gvr`` — so leaving it would commit a record the derivation could not produce,
and the summary-route claim (:mod:`fedcourtsai.pipeline.claims`) resolves off
that marker alone and would read a GVR as plenary. A null route stays null: it
is a coverage sentinel, and filling one in would widen the assessed set rather
than correct it.

``actual_granted`` is untouched by construction — a GVR is in
:data:`~fedcourtsai.schemas.GRANTED_DISPOSITIONS`, so the binary is 1 before and
after — and so are the votes, the signal blocks, and every other recorded field.

**Population.** Committed cert-stage outcomes labeled ``granted`` resolved on or
after the era boundary. Stage comes from the declared moments table
(:func:`fedcourtsai.pipeline.moments.declares`), not from ``event.yaml``: these
baselines carry no stage of their own, and the moments table is where the
pipeline reads a stage-level answer off an event id. A declared moment of
another stage is simply out of population — it resolves under its own standard,
which the cert vocabulary has no claim on — but an id the table declares
*nothing* for is reported rather than passed over in silence, since there the
sweep cannot tell what governs the event at all. Idempotent, because the relabel
leaves the population: a ``gvr`` outcome no longer reads ``granted``.

**Scope: the ledger, and only the ledger.** ``data/cases`` is the derived-judgment
store this sweep converges. The corpus's own disposition column converges through
the pull path — a later pull re-reads the docket and re-normalizes the row — and
corpus writes belong to the writer jobs' upsert path, so a sweep that reached
across would be writing a store it does not own.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from . import corpus
from .paths import EventPaths
from .pipeline import moments
from .pipeline.cert_signals import (
    entry_date,
    match_disposition_signal,
    mootness_disposition,
    proceedings_entries,
)
from .schemas import Disposition, Outcome, Stage
from .serialize import read_model, write_json

#: The era boundary this sweep may reach back to. Resolutions from this date
#: forward were recorded by reading the docket's own order text, so a wrong
#: label there is a gap in that read. Earlier ones were normalized from upstream
#: record fields and never passed through the disposition parser, which makes
#: their ``granted`` the older vocabulary's faithful record — the residual the
#: forward-convention rule protects — rather than anything this sweep may
#: correct. The date is the start of the Term whose cert dispositions were the
#: first the parser recorded.
PARSED_ORDER_TEXT_SINCE = date(2025, 10, 6)

#: How much of a matched order's own words the report quotes. Wide enough to
#: carry both halves of a prose GVR — the grant and the vacatur — and the "in
#: light of X" citation that identifies which decision it issued under, since
#: that is what a reviewer reads to judge whether the matched entry really is
#: the resolving order.
_EVIDENCE_LIMIT = 260

_NO_SNAPSHOT_REASON = (
    "no stored snapshot for the case, so there is no docket text to re-resolve against"
)
_NO_DISPOSING_ENTRY_REASON = (
    "the snapshot discloses entries at or after the resolution date but none of them parses as "
    "a disposition, so nothing confirms a different label"
)
_UNDECLARED_EVENT_REASON = (
    "the moments table declares no stage for this event id, so which decision standard governs "
    "it cannot be read and the cert vocabulary cannot be applied"
)
_SCORED_REASON = (
    "the event carries committed predict/evaluate output, whose stamped `correct` bits were "
    "computed from this label (re-run with --include-scored to relabel and take on the re-grade)"
)


@dataclass(frozen=True)
class _Confirmation:
    """What the parser read off the snapshot's disposing entry."""

    disposition: Disposition
    basis: Literal["standard", "mootness"]
    evidence: str
    filed: date


@dataclass(frozen=True)
class DispositionRelabel:
    """One outcome the sweep re-resolves, carrying the text that confirms the new label."""

    ref: str  # "<case_id>/<event_id>"
    was: Disposition
    now: Disposition
    basis: Literal["standard", "mootness"]
    evidence: str
    #: The three dates a reviewer needs to judge whether the matched entry is
    #: the order that resolved this event.
    entry_filed: date
    resolved_at: date
    snapshot_date: date
    #: Committed evaluation directories under the event — the re-grade backlog
    #: this relabel creates. Non-zero only under ``include_scored``.
    stamped_evaluations: int = 0


@dataclass
class DispositionConvergenceResult:
    """What the convergence sweep changed (or would change on a dry run)."""

    applied: bool = False
    relabeled: list[DispositionRelabel] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id/event_id, reason)
    #: True when ``apply`` was asked for but the blast-radius bound refused it.
    #: Nothing is written in that case — the plan is reported and abandoned.
    refused: bool = False
    #: Candidates whose docket text was actually read and judged this run —
    #: the denominator the relabel count is a fraction *of*.
    checkable: int = 0
    #: Candidates in scope but with no readable text (no snapshot, or a snapshot
    #: predating the resolution). Not evidence of a clean ledger, just of a
    #: partial one, which is why it is reported beside the relabel count.
    uncheckable: int = 0
    #: Candidates the sweep declines to judge at all: resolved before the era
    #: boundary, carrying an undeclared event id, or held back as scored.
    out_of_scope: int = 0


def _truncate(text: str) -> str:
    """One entry's words, whitespace-collapsed and bounded for a report line."""
    collapsed = " ".join(text.split())
    return (
        collapsed if len(collapsed) <= _EVIDENCE_LIMIT else collapsed[: _EVIDENCE_LIMIT - 1] + "…"
    )


def _confirming_signal(payload: dict[str, Any], resolved_at: date) -> _Confirmation | None:
    """The disposition the payload's own disposing entry carries, or ``None``.

    Scoped to entries filed **at or after** the recorded resolution date: an
    earlier grant of some other relief on the same docket is not the order that
    resolved this event, and reading one would relabel off unrelated text. An
    undated entry is skipped rather than guessed at — :func:`entry_date` refuses
    a partial date precisely so a scan cannot drift with the day it runs.

    The **earliest dated** qualifying entry wins, chosen by date rather than by
    position, because this reader is the one that *writes*. The REST shape's
    entry order is whatever upstream returned (the client pages
    ``docket-entries/`` with no ``order_by``), so a position-keyed pick would
    make the relabel a function of upstream's ordering; ties keep payload order,
    which leaves the choice deterministic either way.

    Narrower than :func:`fedcourtsai.pipeline.outcome.disposition_basis`, which
    reads the first disposition-bearing entry *anywhere* in the payload,
    deliberately: that function describes the docket, while this one must name
    the order that resolved **this** event. The basis is then read off the same
    entry's own text, so the label and the basis can never describe two
    different orders, and the whole entry is quoted as the evidence rather than
    the parser's own narrow snippet — a reviewer judging the match needs the
    grant half and the "in light of" citation, not just the words around it.
    """
    qualifying: list[tuple[date, int, str, Disposition]] = []
    for position, (text, raw) in enumerate(proceedings_entries(payload)):
        filed = entry_date(raw)
        if filed is None or filed < resolved_at:
            continue
        matched = match_disposition_signal(text)
        if matched is None:
            continue
        disposition, _label, _snippet = matched
        qualifying.append((filed, position, text, disposition))
    if not qualifying:
        return None
    filed, _position, text, disposition = min(qualifying, key=lambda e: (e[0], e[1]))
    basis: Literal["standard", "mootness"] = (
        "mootness" if mootness_disposition(text) else "standard"
    )
    return _Confirmation(
        disposition=disposition, basis=basis, evidence=_truncate(text), filed=filed
    )


def _stamped_evaluations(paths: EventPaths) -> int:
    """How many committed evaluation directories sit under one event.

    Directory presence, not an ``evaluation.json`` read: an empty leftover still
    means a cell was provisioned here, and counting it errs toward reporting a
    re-grade that is not owed rather than missing one that is.
    """
    root = paths.evaluations_dir
    if not root.is_dir():
        return 0
    return sum(1 for path in root.glob("*/*") if path.is_dir())


def _carries_agent_output(paths: EventPaths) -> bool:
    """Whether any predict or evaluate cell has committed output under this event."""
    return paths.predictions_dir.exists() or paths.evaluations_dir.exists()


@dataclass(frozen=True)
class _Skip:
    """One candidate the sweep will not rewrite, and which denominator it counts in."""

    reason: str
    bucket: Literal["checkable", "uncheckable", "out_of_scope"]


@dataclass(frozen=True)
class _Plan:
    """One confirmed relabel: what to report and what to write."""

    relabel: DispositionRelabel
    update: dict[str, Any]


def _out_of_scope(
    event_paths: EventPaths, outcome: Outcome, *, include_scored: bool
) -> _Skip | None:
    """The two gates that refuse a candidate before any docket text is read.

    Both are categorical rather than evidential — they say the sweep *may not*
    look, not that looking found nothing — which is why they run before the
    snapshot read and cost nothing.
    """
    if outcome.resolved_at < PARSED_ORDER_TEXT_SINCE:
        return _Skip(
            f"resolved {outcome.resolved_at.isoformat()}, before the disposition parser "
            f"recorded this court's labels: the older vocabulary's record, not a parse gap",
            "out_of_scope",
        )
    if not include_scored and _carries_agent_output(event_paths):
        return _Skip(_SCORED_REASON, "out_of_scope")
    return None


def _readable_snapshot(
    conn: sqlite3.Connection, outcome: Outcome
) -> tuple[date, dict[str, Any]] | _Skip:
    """The stored payload that could contain the resolving order, or why it cannot.

    A snapshot older than the resolution is *structurally* uncheckable — the
    order had not been entered when it was taken — which is a different fact
    from a snapshot that simply carries no disposing entry, and the two are
    counted apart so the report's denominators stay honest.
    """
    found = corpus.latest_snapshot(conn, outcome.case_id)
    if found is None:
        return _Skip(_NO_SNAPSHOT_REASON, "uncheckable")
    snapshot_date, payload = found
    if snapshot_date < outcome.resolved_at:
        return _Skip(
            f"the stored snapshot predates the resolution ({snapshot_date.isoformat()} < "
            f"{outcome.resolved_at.isoformat()}), so the resolving order cannot be in it",
            "uncheckable",
        )
    return snapshot_date, payload


def _declined(confirmed: _Confirmation | None, recorded: Disposition) -> _Skip | None:
    """Why a read of the docket text does not authorize a relabel, or ``None``.

    ``None`` is the single path to a write, so every way of failing to confirm a
    ``gvr`` — no disposing entry, a text that agrees with the label already, and
    a text that disagrees but reads as something else — comes back as a reported
    skip rather than as silence.
    """
    if confirmed is None:
        return _Skip(_NO_DISPOSING_ENTRY_REASON, "checkable")
    if confirmed.disposition == recorded:
        return _Skip(
            f"docket text parses {confirmed.disposition.value!r}; the label agrees", "checkable"
        )
    if confirmed.disposition != Disposition.gvr:
        return _Skip(
            f"docket text parses {confirmed.disposition.value!r}, which is outside this "
            f"sweep's remit: {confirmed.evidence!r}",
            "checkable",
        )
    return None


def _assess(
    conn: sqlite3.Connection,
    path: Path,
    outcome: Outcome,
    ref: str,
    *,
    include_scored: bool,
) -> _Plan | _Skip | None:
    """Judge one ``granted`` outcome. ``None`` means it is not this sweep's business.

    The gates run cheapest-and-most-categorical first — stage, era, scored — so
    a candidate the sweep may not touch never costs a snapshot read, and the
    protected residual is refused before any docket text is consulted.
    """
    # A declared moment of another stage resolves under its own standard, so the
    # cert vocabulary has no claim on it and it is simply out of population. An
    # id the table declares nothing for is a different answer — the sweep cannot
    # tell what standard governs it — and the dry run is only a complete triage
    # ledger if it says so.
    if not moments.declares(outcome.event_id, Stage.cert):
        undeclared = moments.spec_for(outcome.event_id) is None
        return _Skip(_UNDECLARED_EVENT_REASON, "out_of_scope") if undeclared else None
    event_paths = EventPaths(path.parent)
    if (barred := _out_of_scope(event_paths, outcome, include_scored=include_scored)) is not None:
        return barred
    readable = _readable_snapshot(conn, outcome)
    if isinstance(readable, _Skip):
        return readable
    snapshot_date, payload = readable
    confirmed = _confirming_signal(payload, outcome.resolved_at)
    recorded = Disposition(outcome.actual_disposition)
    if (declined := _declined(confirmed, recorded)) is not None:
        return declined
    assert confirmed is not None  # `_declined` returns a skip for every other case
    basis = "mootness" if outcome.disposition_basis == "mootness" else confirmed.basis
    update: dict[str, Any] = {
        "actual_disposition": confirmed.disposition,
        "disposition_basis": basis,
    }
    if outcome.disposition_route is not None:
        update["disposition_route"] = "gvr"
    return _Plan(
        relabel=DispositionRelabel(
            ref=ref,
            was=recorded,
            now=confirmed.disposition,
            basis=basis,
            evidence=confirmed.evidence,
            entry_filed=confirmed.filed,
            resolved_at=outcome.resolved_at,
            snapshot_date=snapshot_date,
            stamped_evaluations=_stamped_evaluations(event_paths) if include_scored else 0,
        ),
        update=update,
    )


def converge_disposition_labels(
    conn: sqlite3.Connection,
    data_root: Path,
    *,
    apply: bool,
    max_relabels: int | None = None,
    include_scored: bool = False,
) -> DispositionConvergenceResult:
    """Re-resolve every in-era ``granted`` cert outcome against its stored snapshot.

    Dry run by default (reads the ledger and the snapshots, writes nothing);
    ``apply`` rewrites each confirmed ``outcome.json`` through
    :mod:`fedcourtsai.serialize`. One pass: the plan the report describes is
    exactly the write set, so the dry run a maintainer reads and the apply that
    follows cannot describe different work.

    ``max_relabels`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. When
    the confirmed count exceeds it nothing is written and
    :attr:`DispositionConvergenceResult.refused` comes back true — the
    population this sweep converges is finite and non-growing, so a count past
    the bound means the predicate widened, not that the ledger did. ``None``
    means unbounded, which is the dry run's default and never the apply path's.

    ``include_scored`` opts in to relabeling candidates that carry committed
    predict/evaluate output; each such relabel reports the stamped evaluations
    it puts in the re-grade backlog.

    The snapshot read is :func:`fedcourtsai.corpus.latest_snapshot`, which is
    split-aware on its own — under the corpus-split mode it serves from the
    per-case content store and ``conn`` goes unused — so the sweep reads the same
    payload provisioning would, whichever store holds it.

    Every member of the population that is not relabeled is reported with its
    reason: a resolution predating the era boundary, an event id the moments
    table declares no stage for, no snapshot, a snapshot predating the
    resolution, a snapshot disclosing entries but none disposing, the recorded
    label already agreeing with the text, committed scored output, or a parse
    that disagrees but is not ``gvr`` — the last of which this sweep deliberately
    declines to act on. Its remit is the one shape the parser gained the ability
    to read, not a licence to rewrite any label it now disagrees with.
    """
    result = DispositionConvergenceResult(applied=apply)
    planned: list[tuple[Path, Outcome, dict[str, Any]]] = []
    for path in sorted((data_root / "cases").glob("*/*/events/*/outcome.json")):
        outcome = read_model(path, Outcome)
        # Equality, never identity: a validated artifact carries the plain string
        # (``use_enum_values``), so the recorded label is normalized back to a member
        # before it is reported or compared against the parser's own.
        if outcome.actual_disposition != Disposition.granted:
            continue
        ref = f"{outcome.case_id}/{outcome.event_id}"
        verdict = _assess(conn, path, outcome, ref, include_scored=include_scored)
        if verdict is None:
            continue
        if isinstance(verdict, _Skip):
            if verdict.bucket == "checkable":
                result.checkable += 1
            elif verdict.bucket == "uncheckable":
                result.uncheckable += 1
            else:
                result.out_of_scope += 1
            result.skipped.append((ref, verdict.reason))
            continue
        result.checkable += 1
        result.relabeled.append(verdict.relabel)
        planned.append((path, outcome, verdict.update))
    if not apply:
        return result
    if max_relabels is not None and len(result.relabeled) > max_relabels:
        result.refused = True
        return result
    for path, outcome, update in planned:
        write_json(path, outcome.model_copy(update=update))
    return result
