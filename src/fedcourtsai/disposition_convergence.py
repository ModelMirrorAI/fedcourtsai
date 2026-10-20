"""Converge committed cert outcomes against the disposition their docket text carries.

A cert-stage label asserts what the order said — a ``granted``, or the
``denied`` / ``dismissed`` a docket's exit recorded — and the committed ledger
holds records the current parser reads differently. Nothing
else re-reads them: ``record_outcomes`` is idempotent-by-filter, so a resolution
pass never revisits a resolved event, and the Munsingwear migration's predicate
(``granted`` + a ``mootness`` basis) cannot reach a record carrying no basis at
all.

This sweep re-resolves them from the stored docket text and is
**self-confirming**: it relabels only where the parser, run over the snapshot's
own disposing entry, returns a label the arm below admits. No confirmation, no
write — the outcome is reported with the reason instead, so the dry run is the
triage ledger.

**Three arms, and the difference between them is what kind of mistake each
corrects** (:data:`RelabelArm`).

``gvr`` — *the same order, read more finely.* An order that grants, vacates and
remands in one breath — the prose GVR
(:func:`fedcourtsai.pipeline.cert_signals._gvr_tail_sentence`, reached through
:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`) — sits
recorded as a plain grant. The petition was granted either way, so the binary
does not move; only the label sharpens.

``disowned-grant`` — *no order at all.* The recorded grant was read off an
ancillary order about the petition rather than an order on it: an extension of
time to respond, a delayed distribution, an unsealing. The clerk's wording put
the cert noun beside a granting verb, the parser latched it, and the case's real
terminal — a denial, or a petition-stage Rule 46 dismissal — was recorded
nowhere. Here the binary *does* move, from 1 to 0, and so does the resolution
date. The guard that stops the parser reading those sentences at all lives in
:func:`fedcourtsai.pipeline.cert_signals._is_non_order_sentence`; this arm is
what withdraws the records it already wrote.

**The era boundary is a rule about provenance, and each arm meets it
differently.** A label is only a *parse gap* if the parser wrote it. From
:data:`PARSED_ORDER_TEXT_SINCE` forward, a cert disposition was recorded by
reading the docket's own order text, so a wrong label there is a gap in that
read and the ``gvr`` arm may correct it. Earlier resolutions were normalized
from upstream record fields and never passed through the disposition parser at
all — their ``granted`` is the older vocabulary's faithful record, which the
forward-convention rule in ``docs/salience.md`` protects, and relabeling one
would be the retroactive vocabulary flip that rule forbids.

The ``disowned-grant`` arm answers that provenance question from the docket
itself instead of from the calendar, which is why it reaches back through the
boundary. It fires only where an entry **dated the recorded resolution** carries
the sentence the ``granted`` was read out of — grant-shaped, and refused today
by the order guard — and **nothing anywhere on the docket** parses as a grant
any more (:func:`_recording_entry`). Then the label's provenance is not
inferred but held: this text, and today's parser will not stand behind it. That
is a parse gap with a date on it, whatever Term it happened in, and the sentence
is quoted in the report so the warrant is auditable rather than asserted. Where
the recorded day names no such sentence, or any entry still parses as a grant —
the real grant whose Rule 46 exit or mootness dismissal comes later — the arm
declines *on that warrant*, and the row is reported with which of the two it
failed rather than falling through to the date boundary. The warrant is the
whole of this arm's licence, so a widening snapshot store still cannot quietly
reach the protected residual: what a fuller store buys is text to judge, and a
row whose text does not carry the warrant is not judged.

**Scored cells are held back by default.** An ``evaluation.json`` is stamped with
a ``correct`` bit computed from the outcome, so relabeling under a committed
evaluation puts a published bit out of step with the record it was scored
against. A candidate whose event directory holds committed predict or evaluate
output is skipped and reported unless ``include_scored`` says otherwise; when it
does, each relabel reports how many stamped evaluations it puts in the re-grade
backlog, which ``stamp-cell --regrade`` is the follow-through for.

**Which fields move is a property of the arm**, set in one place
(:func:`_update_for`) so the report and the write cannot describe different
work. On ``gvr`` three fields move: ``actual_disposition``,
``disposition_basis`` (latching on, never off), and ``disposition_route`` where
one was already assessed; votes, the signal blocks and everything else stay.
On ``disowned-grant`` the record's whole warrant moves to a different entry, so
those three move plus ``actual_granted`` (1 → 0), ``resolved_at`` (to the
confirming entry's date), and — because moving the date is what strands them —
``signals`` / ``interim_signals``, which are frozen *as at resolution* and would
otherwise hide every docket step between the two dates from the increment
claims. Votes and every other recorded field stay under every arm.

``restored-grant`` — *the exit was no exit.* The mirror of ``disowned-grant``,
on a recorded ``denied`` or ``dismissed``: the label was read off text that
names the petition's fate without deciding it — the termination conditional a
stay order pending certiorari ends with ("Should the petition ... be denied,
this stay shall terminate automatically"), or a Rule 46 dismissal "only as to"
one petitioner — while the docket went on to its grant or GVR. The order guard
and the partial-scope veto in :mod:`fedcourtsai.pipeline.cert_signals` stop the
parser reading those sentences; this arm restores the grant they hid. It fires
only where the confirming entry is a grant, no entry dated the recorded
resolution still parses as an exit, and one carries the refused sentence
(:func:`_recorded_exit`), which is quoted as the warrant. The binary moves 0 →
1 and the resolution re-dates to the grant, with the same field set as a
withdrawal. Like that arm it reaches back through the era boundary on its
warrant. A refused exit whose docket ends in a different exit (a partial
dismissal followed by the real denial) moves no binary and is reported rather
than relabeled.

**Population.** Committed cert-stage outcomes labeled ``granted``, and those
labeled ``denied`` / ``dismissed`` whose case row in the corpus records a grant
(:func:`_corpus_records_grant` — the screen that keeps the exit majority of the
ledger from costing a snapshot read each; the docket text is still the
warrant). Stage comes
from the declared moments table
(:func:`fedcourtsai.pipeline.moments.declares`), not from ``event.yaml``: these
baselines carry no stage of their own, and the moments table is where the
pipeline reads a stage-level answer off an event id. A declared moment of
another stage is simply out of population — it resolves under its own standard,
which the cert vocabulary has no claim on — but an id the table declares
*nothing* for is reported rather than passed over in silence, since there the
sweep cannot tell what governs the event at all. Idempotent under every arm:
a ``gvr`` leaves the population, and a withdrawn or restored label is re-read
from the entry it was re-dated to, whose parse it now agrees with.

**Scope: the ledger, and only the ledger.** ``data/cases`` is the derived-judgment
store this sweep converges, and corpus writes belong to the writer jobs' upsert
path, so a sweep that reached across would be writing a store it does not own.

**The corpus does not converge on its own, and the gap matters to anyone reading
the two stores together.** Base rates and every published disposition figure are
built from the corpus (:func:`fedcourtsai.analytics.build_statpack`), not from
``data/cases``, so between this sweep and a corpus correction a withdrawn row
reads ``0`` in the ledger while still counting as a grant in the denominators
those cells are scored against. The live channel closes part of that:
:func:`fedcourtsai.pipeline.ingest._live_resolution` re-reads the proceedings
text through the same guard, and ``disposition`` / ``date_cert_granted`` take
the incoming value on upsert rather than latching. Only part, though —
:func:`fedcourtsai.corpus.live_rotation` polls a row only while its disposition
is null or its merits proceeding is open, and a fabricated grant whose docket
opened no merits event satisfies neither. Those rows are unreachable by any
channel and owe a curated corpus write.
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
    refused_exit_sentence,
    refused_grant_sentence,
)
from .pipeline.outcome import granted_flag
from .schemas import GRANTED_DISPOSITIONS, Disposition, Outcome, Stage
from .serialize import read_model, write_json

#: The era boundary the ``gvr`` arm may reach back to. Resolutions from this
#: date forward were recorded by reading the docket's own order text, so a wrong
#: label there is a gap in that read. Earlier ones were normalized from upstream
#: record fields and never passed through the disposition parser, which makes
#: their ``granted`` the older vocabulary's faithful record — the residual the
#: forward-convention rule protects — rather than anything that arm may correct.
#: The date is the start of the Term whose cert dispositions were the first the
#: parser recorded.
#:
#: A **date** is the right instrument only where the docket cannot answer the
#: provenance question itself. It can, for the two binary arms: a recorded
#: resolution date carrying an entry that no longer parses as a grant
#: (:func:`_recording_entry`, ``disowned-grant``) or as an exit
#: (:func:`_recorded_exit`, ``restored-grant``) names the parse gap directly,
#: so those arms are governed by their own warrants and this constant does not
#: bound them. Anything else stays behind this date.
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
_NO_RECORDING_ENTRY_REASON = (
    "no entry dated the recorded resolution carries text a grant could have been read out of, so "
    "the label's provenance cannot be established and the parse-gap warrant fails"
)
_NO_RECORDED_EXIT_REASON = (
    "no entry dated the recorded resolution carries text a denial or dismissal could have been "
    "read out of, so the label's provenance cannot be established and the restore warrant fails"
)
_LIVE_EXIT_REASON = (
    "an entry dated the recorded resolution still parses as an exit, so the label's own warrant "
    "stands and the grant is a separate order rather than a correction"
)
_LIVE_GRANT_RECITAL_REASON = (
    "an entry on this docket still parses as a grant, so the label's own warrant stands and a "
    "later non-grant entry is a subsequent order rather than a correction"
)


@dataclass(frozen=True)
class _Confirmation:
    """What the parser read off the snapshot's disposing entry."""

    disposition: Disposition
    basis: Literal["standard", "mootness"]
    evidence: str
    filed: date


#: Which remit authorized a relabel. ``gvr`` re-reads a grant the parser now
#: reads as a prose GVR — same order, finer label, the binary unmoved.
#: ``disowned-grant`` withdraws a grant the parser no longer reads at all;
#: ``restored-grant`` is its mirror, restoring the grant a refused exit hid.
#: Those two move the binary and the resolution date, in opposite directions,
#: so all three are named apart everywhere they are reported.
RelabelArm = Literal["gvr", "disowned-grant", "restored-grant"]


@dataclass(frozen=True, kw_only=True)
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
    #: Which remit authorized this relabel (see :data:`RelabelArm`). Required
    #: rather than defaulted: the withdrawal disclosure and the report's arm
    #: split both key on it, so a construction that forgot it would report a
    #: grant withdrawal as a label sharpening.
    arm: RelabelArm
    #: On ``disowned-grant``, the refused sentence the withdrawn ``granted`` was
    #: read out of; on ``restored-grant``, the refused sentence the replaced
    #: ``denied`` / ``dismissed`` was read out of — each arm's own warrant,
    #: quoted so the dry run shows the evidence for the relabel and not only
    #: for the order replacing it.
    recital: str | None = None
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
    #: ``denied`` / ``dismissed`` outcomes the corpus screen passed over: their
    #: case row records no grant, so the docket text is never read. Counted
    #: rather than listed — it is most of the ledger.
    screened: int = 0


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


@dataclass(frozen=True)
class _Disowned:
    """The refused sentence a committed ``granted`` label was read out of."""

    recital: str


def _recording_entry(
    payload: dict[str, Any], resolved_at: date
) -> _Disowned | Literal["grant", "unidentified"]:
    """What the docket says today about the grant the label records. Three answers.

    - ``"grant"`` — **some entry anywhere on this docket still parses as a
      grant.** The petition was granted, whatever else the docket goes on to
      say, so a later denial or dismissal is a *subsequent* order — the
      post-grant Rule 46 exit, a dismissal as moot — and never a correction of
      the grant. Docket-wide rather than scoped to the recorded day on purpose:
      a real grant recorded a day out would otherwise be withdrawn on the
      strength of its own later dismissal, and that is the one mistake this arm
      must never make.
    - :class:`_Disowned` — an entry **dated the recorded resolution** carries a
      grant-shaped match that :func:`fedcourtsai.pipeline.cert_signals.refused_grant_sentence`
      refuses, and nothing on the docket parses as a grant any more. That
      sentence *is* the label's provenance: a grant was read out of it once, and
      today's parser will not stand behind it. It comes back rather than a bare
      flag so the dry run can quote the warrant, not only the order that
      replaces it.
    - ``"unidentified"`` — everything else: no entry on the recorded date, or
      entries with nothing a grant could have been read from. The label's
      provenance cannot be established from this docket, which is exactly the
      state the older vocabulary's normalized records are in. Reported, never
      rewritten.

    Requiring the refused sentence, rather than merely an entry on the day, is
    what keeps the warrant honest. A real grant whose order text the payload
    does not carry would otherwise be withdrawn on the strength of any unrelated
    entry sharing its date and any later dismissal — the exact shape of the
    consolidated dockets whose terminal is nowhere on them.

    Undated entries cannot anchor the date test, on the same rule as
    :func:`_confirming_signal` — :func:`entry_date` refuses a partial date so a
    scan cannot drift with the day it runs — but they are still read for the
    grant test, where the question is what the docket says rather than when.
    """
    recital: str | None = None
    for text, raw in proceedings_entries(payload):
        matched = match_disposition_signal(text)
        if matched is not None and matched[0] in GRANTED_DISPOSITIONS:
            return "grant"
        if recital is None and entry_date(raw) == resolved_at:
            recital = refused_grant_sentence(text)
    return _Disowned(recital) if recital is not None else "unidentified"


def _recorded_exit(
    payload: dict[str, Any], resolved_at: date
) -> _Disowned | Literal["exit", "unidentified"]:
    """What the entries dated a recorded denial or dismissal say about it today.

    :func:`_recording_entry`'s mirror for the ``restored-grant`` arm, and
    scoped to the recorded day rather than the docket, because the two binary arms
    guard opposite mistakes. A withdrawal must never take a real grant away, so
    any grant anywhere vetoes it; a restoration must never overturn a real
    exit, and the exit that matters is the one the label was read from. A
    later denial on the same docket (the real terminal after a partial
    dismissal) is no veto here — the confirming entry already decides what the
    label becomes, and a grant arm acts only where that entry is a grant.

    - ``"exit"`` — an entry dated the recorded resolution still parses as a
      denial or dismissal. The label's warrant stands. (The ordinary shape — a
      real denial later vacated on rehearing — never reaches here, because that
      denial is itself the confirming entry and agrees with the label; this is
      the backstop for a same-day grant entry read ahead of the exit.)
    - :class:`_Disowned` — no entry on that day parses as an exit, and one
      carries an exit-shaped sentence today's parser refuses
      (:func:`fedcourtsai.pipeline.cert_signals.refused_exit_sentence`: a stay
      order's termination conditional, a dismissal scoped "only as to" one
      party). That sentence is the label's provenance.
    - ``"unidentified"`` — nothing on that day an exit could have been read
      from. Reported, never rewritten.
    """
    recital: str | None = None
    for text, raw in proceedings_entries(payload):
        if entry_date(raw) != resolved_at:
            continue
        matched = match_disposition_signal(text)
        if matched is not None and matched[0] in _WITHDRAWN_GRANT_LABELS:
            return "exit"
        if recital is None:
            recital = refused_exit_sentence(text)
    return _Disowned(recital) if recital is not None else "unidentified"


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
    bucket: Literal["checkable", "uncheckable", "out_of_scope", "screened"]


@dataclass(frozen=True)
class _Plan:
    """One confirmed relabel: what to report and what to write."""

    relabel: DispositionRelabel
    update: dict[str, Any]


def _out_of_scope(
    event_paths: EventPaths, outcome: Outcome, *, include_scored: bool
) -> _Skip | None:
    """The gate that refuses a candidate before any docket text is read.

    Categorical rather than evidential — it says the sweep *may not* look, not
    that looking found nothing — which is why it runs before the snapshot read
    and costs nothing. The era boundary is **not** here: it is a rule about what
    kind of record a label is, and the ``disowned-grant`` arm answers that
    question from the docket text itself, so it is applied per arm in
    :func:`_arm` once the text has been read.
    """
    if not include_scored and _carries_agent_output(event_paths):
        return _Skip(_SCORED_REASON, "out_of_scope")
    return None


def _era_skip(outcome: Outcome) -> _Skip:
    """The protected residual: a label the disposition parser never wrote."""
    return _Skip(
        f"resolved {outcome.resolved_at.isoformat()}, before the disposition parser "
        f"recorded this court's labels: the older vocabulary's record, not a parse gap",
        "out_of_scope",
    )


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


#: The exits: the labels the ``disowned-grant`` arm may put in a withdrawn
#: grant's place, and the recorded labels the ``restored-grant`` arm may
#: replace. Both leave :data:`~fedcourtsai.schemas.GRANTED_DISPOSITIONS`, which
#: is what makes those two the arms that move the binary.
_WITHDRAWN_GRANT_LABELS: frozenset[Disposition] = frozenset(
    {Disposition.denied, Disposition.dismissed}
)


@dataclass(frozen=True)
class _Arm:
    """The remit a read of the docket authorizes, with the evidence it rests on."""

    kind: RelabelArm
    #: The refused sentence the replaced label was read out of: the withdrawn
    #: ``granted`` on ``disowned-grant``, the replaced ``denied`` / ``dismissed``
    #: on ``restored-grant``. Absent on ``gvr``, the one arm whose relabel is not
    #: warranted by text the parser declines to read.
    recital: str | None = None


def _withdrawal(payload: dict[str, Any], resolved_at: date) -> _Arm | _Skip:
    """Whether the docket warrants withdrawing the grant, or why it does not.

    The whole of the ``disowned-grant`` arm's licence to reach back through the
    era boundary, kept in one function so the two ways of failing it are read
    together with the one way of passing. Called only on the withdrawn-label
    branch, so a candidate the sweep would decline anyway never pays for the
    docket-wide scan.
    """
    recording = _recording_entry(payload, resolved_at)
    if recording == "grant":
        return _Skip(_LIVE_GRANT_RECITAL_REASON, "checkable")
    if recording == "unidentified":
        return _Skip(_NO_RECORDING_ENTRY_REASON, "checkable")
    return _Arm("disowned-grant", recital=recording.recital)


def _restoration(payload: dict[str, Any], resolved_at: date) -> _Arm | _Skip:
    """Whether the docket warrants restoring a grant over a recorded exit, or why not.

    The ``restored-grant`` arm's whole licence, read the way :func:`_withdrawal`
    reads its own: positive evidence on the recorded day, not the calendar, so
    it reaches back through the era boundary on the same terms.
    """
    recording = _recorded_exit(payload, resolved_at)
    if recording == "exit":
        return _Skip(_LIVE_EXIT_REASON, "checkable")
    if recording == "unidentified":
        return _Skip(_NO_RECORDED_EXIT_REASON, "checkable")
    return _Arm("restored-grant", recital=recording.recital)


def _agrees(confirmed: _Confirmation, outcome: Outcome) -> _Skip:
    """The label agrees with the text; say so, and name a date the agreement hides.

    No arm moves a date on its own, so a label the confirming entry agrees with
    keeps its ``resolved_at`` even where that entry is dated later — a grant
    recorded on a stay order's day and confirmed by the real grant months on.
    The reason names the gap so the dry run surfaces it rather than reading as
    a clean record.
    """
    reason = f"docket text parses {confirmed.disposition.value!r}; the label agrees"
    if confirmed.filed != outcome.resolved_at:
        reason += (
            f", but its confirming entry is dated {confirmed.filed.isoformat()}, not the "
            f"recorded {outcome.resolved_at.isoformat()}; no arm moves a date alone"
        )
    return _Skip(reason, "checkable")


def _binary_arm(
    confirmed: _Confirmation, recorded: Disposition, outcome: Outcome, payload: dict[str, Any]
) -> _Arm | _Skip:
    """The remit where an exit is on one side of the disagreement: the binary arms.

    A recorded grant the text now reads as an exit is the withdrawal
    (:func:`_withdrawal`). A recorded exit the text now reads as a grant is the
    restoration (:func:`_restoration`); one it reads as a different exit (a
    partial dismissal whose docket ends in a denial) moves no binary and is
    reported, not relabeled.
    """
    if recorded not in _WITHDRAWN_GRANT_LABELS:
        return _withdrawal(payload, outcome.resolved_at)
    if confirmed.disposition not in GRANTED_DISPOSITIONS:
        return _Skip(
            f"docket text parses {confirmed.disposition.value!r}, which is outside this "
            f"sweep's remit for a recorded exit: {confirmed.evidence!r}",
            "checkable",
        )
    return _restoration(payload, outcome.resolved_at)


def _arm(
    confirmed: _Confirmation | None,
    recorded: Disposition,
    outcome: Outcome,
    payload: dict[str, Any],
) -> _Arm | _Skip:
    """Which remit a read of the docket text authorizes, or why none does.

    A :class:`_Skip` is the only alternative to an arm, so every way of failing
    to confirm a relabel — no disposing entry, a text that agrees with the label
    already, a text that disagrees but reads as something else, and the era
    boundary — comes back reported rather than as silence.

    The order matters. The ``restored-grant`` and ``disowned-grant`` tests run
    **before** the era boundary because each *answers* the question the
    boundary asks (shown here for the withdrawal; the restoration's refused exit
    sentence is the same kind of evidence). The boundary
    protects labels the disposition parser never wrote — normalized from the
    upstream record's own fields, the older vocabulary's faithful record — and a
    ``disowned`` recording entry is positive evidence to the contrary: an order
    sat on that day, the parser read a grant out of it once, and today's parser
    reads no grant on the docket at all. That is a parse gap with a date on it,
    not a vocabulary flip, so it is correctable however old it is. Every other
    disagreement stays behind the boundary, where a widening snapshot store
    cannot quietly reach it.

    The final skip is a **total-function default, not a live case**: every label
    :data:`~fedcourtsai.pipeline.cert_signals._ENTRY_SIGNALS` can return is named
    by an arm above or agrees with the recorded label. It is what a label
    the parser gains later meets — reported, never acted on — so the sweep's
    remit only ever widens deliberately.
    """
    if confirmed is None:
        return _Skip(_NO_DISPOSING_ENTRY_REASON, "checkable")
    if confirmed.disposition == recorded:
        return _agrees(confirmed, outcome)
    if recorded in _WITHDRAWN_GRANT_LABELS or confirmed.disposition in _WITHDRAWN_GRANT_LABELS:
        return _binary_arm(confirmed, recorded, outcome, payload)
    if outcome.resolved_at < PARSED_ORDER_TEXT_SINCE:
        return _era_skip(outcome)
    if confirmed.disposition is not Disposition.gvr:
        return _Skip(
            f"docket text parses {confirmed.disposition.value!r}, which is outside this "
            f"sweep's remit: {confirmed.evidence!r}",
            "checkable",
        )
    return _Arm("gvr")


def _update_for(arm: RelabelArm, outcome: Outcome, confirmed: _Confirmation) -> dict[str, Any]:
    """The fields one arm moves, and no others.

    ``gvr`` — same order, finer label. ``actual_disposition`` takes the confirmed
    label; ``disposition_basis`` takes the matched entry's basis but only ever
    **latches on**, since a record already carrying ``mootness`` describes an
    order this single-entry read is not entitled to re-characterize;
    ``disposition_route`` advances to ``gvr`` where a route was already assessed,
    because the marker is derived from the label and leaving it would commit a
    record the derivation could not produce. A null route stays null: it is a
    coverage sentinel, and filling one in would widen the assessed set rather
    than correct it. ``actual_granted`` is untouched by construction — a GVR is
    in :data:`~fedcourtsai.schemas.GRANTED_DISPOSITIONS`.

    ``disowned-grant`` and ``restored-grant`` move the same fields, in opposite
    directions on the binary; the account below is written for the withdrawal
    and holds for the restoration with the grant gained rather than lost.

    ``disowned-grant`` — a different order, and no grant at all. The record's
    whole warrant moves to the confirming entry, so every field derived from the
    old one moves with it: ``resolved_at`` to that entry's date (leaving it would
    date a denial to a motion order), ``actual_granted`` to the binary the new
    label projects to, and ``disposition_basis`` to that entry's own basis rather
    than latching — the stored basis described an order the parser has now
    disowned, so keeping it would carry a characterization of vacated text. An
    assessed ``disposition_route`` is **cleared**, because
    :func:`fedcourtsai.pipeline.outcome.disposition_route` returns ``None`` for
    every non-grant: the row leaves the grant family entirely, so the route is
    not a narrowed observation but an inapplicable one.

    **The date only ever moves later, and the direction is not neutral.**
    :func:`_confirming_signal` takes the earliest disposing entry *at or after*
    the recorded resolution, so ``resolved_at`` is monotone forward — which
    means a withdrawal can only push an already-scored cell from the
    retrospective stratum toward ``forward``
    (:func:`fedcourtsai.integrity.classify_stratum`, the leaderboard's rank key)
    and can only clear a recorded forward-claim breach
    (:func:`fedcourtsai.integrity.forward_claim_breach`), never the reverse. Both
    movements are correct where the withdrawal is correct — a cell that
    forecast an outcome the docket had not yet reached really is forward — but a
    correction whose error direction is one-sided and flattering has to be read
    as such, which is what the dry run is for, and neither movement is covered
    by ``stamp-cell --regrade``: they land on the next board build.

    The signal blocks are cleared for a different reason, and it is a
    consequence of moving the date rather than of the label. ``signals`` and
    ``interim_signals`` are *docket progress frozen as at resolution*, and the
    increment claims score them against the prediction-time value
    (:mod:`fedcourtsai.pipeline.claims`) — so a block frozen at the ancillary
    order, left beside a ``resolved_at`` that has advanced past it, would hide
    every distribution and CVSG in between and resolve those claims 0 where the
    truth is 1. Re-freezing them is the resolution pass's work, not a
    single-entry read's; ``None`` is the field's own documented "nobody looked"
    sentinel, and every claim masks on it. Votes and every other recorded field
    stay as they are under every arm.
    """
    if arm == "gvr":
        basis = "mootness" if outcome.disposition_basis == "mootness" else confirmed.basis
        update: dict[str, Any] = {
            "actual_disposition": confirmed.disposition,
            "disposition_basis": basis,
        }
        if outcome.disposition_route is not None:
            update["disposition_route"] = "gvr"
        return update
    update = {
        "actual_disposition": confirmed.disposition,
        "actual_granted": granted_flag(confirmed.disposition),
        "resolved_at": confirmed.filed,
        "disposition_basis": confirmed.basis,
    }
    if outcome.disposition_route is not None:
        update["disposition_route"] = None
    for block in ("signals", "interim_signals"):
        if getattr(outcome, block) is not None:
            update[block] = None
    return update


def _assess(
    conn: sqlite3.Connection,
    path: Path,
    outcome: Outcome,
    ref: str,
    *,
    include_scored: bool,
) -> _Plan | _Skip | None:
    """Judge one ``granted``, ``denied`` or ``dismissed`` outcome. ``None`` means
    it is not this sweep's business.

    The gates run cheapest-and-most-categorical first — stage, then the exit
    screen (a recorded ``denied`` / ``dismissed`` whose corpus row records no
    grant, :func:`_corpus_records_grant`), then the scored holdback — so a
    candidate the sweep may not touch never costs a snapshot read. The era
    boundary runs *after* the text read rather than beside them,
    because it is not categorical: whether a label is the older vocabulary's
    record or a parse gap is a question the docket text answers (see
    :func:`_arm`). The cost of moving it is one snapshot read per pre-era
    candidate, and the gain is that the ledger line each one gets says what the
    docket actually shows rather than only how old it is.
    """
    # A declared moment of another stage resolves under its own standard, so the
    # cert vocabulary has no claim on it and it is simply out of population. An
    # id the table declares nothing for is a different answer — the sweep cannot
    # tell what standard governs it — and the dry run is only a complete triage
    # ledger if it says so.
    if not moments.declares(outcome.event_id, Stage.cert):
        undeclared = moments.spec_for(outcome.event_id) is None
        return _Skip(_UNDECLARED_EVENT_REASON, "out_of_scope") if undeclared else None
    # The exit screen runs once the stage is known, so its count is cert-stage
    # outcomes only, and before the scored holdback, so an exit the corpus gives
    # no reason to read is never reported as held back either.
    recorded = Disposition(outcome.actual_disposition)
    if recorded in _WITHDRAWN_GRANT_LABELS and not _corpus_records_grant(conn, outcome):
        return _Skip("the corpus row records no grant", "screened")
    event_paths = EventPaths(path.parent)
    if (barred := _out_of_scope(event_paths, outcome, include_scored=include_scored)) is not None:
        return barred
    readable = _readable_snapshot(conn, outcome)
    if isinstance(readable, _Skip):
        return readable
    snapshot_date, payload = readable
    confirmed = _confirming_signal(payload, outcome.resolved_at)
    chosen = _arm(confirmed, recorded, outcome, payload)
    if isinstance(chosen, _Skip):
        return chosen
    assert confirmed is not None  # `_arm` returns a skip for every other case
    update = _update_for(chosen.kind, outcome, confirmed)
    # The reported basis is read back out of the write set rather than
    # recomputed, so the ledger line and the record can never disagree; the
    # narrowing is what keeps that read typed.
    basis: Literal["standard", "mootness"] = (
        "mootness" if update["disposition_basis"] == "mootness" else "standard"
    )
    return _Plan(
        relabel=DispositionRelabel(
            ref=ref,
            was=recorded,
            now=confirmed.disposition,
            basis=basis,
            evidence=confirmed.evidence,
            entry_filed=confirmed.filed,
            resolved_at=outcome.resolved_at,
            arm=chosen.kind,
            recital=chosen.recital,
            snapshot_date=snapshot_date,
            stamped_evaluations=_stamped_evaluations(event_paths) if include_scored else 0,
        ),
        update=update,
    )


def _corpus_records_grant(conn: sqlite3.Connection, outcome: Outcome) -> bool:
    """The cheap screen for the ``restored-grant`` arm: does the case row hold a grant?

    The exit population is most of the ledger, and reading every denial's
    docket text to find the handful a refused exit hid would cost a snapshot
    read per outcome. The corpus row answers first, because the live channel
    and ``refresh-dockets`` re-derive ``disposition`` from the same parser on
    every read and the column takes the incoming value: a row whose docket the
    parser now reads as granted already says so. The screen only admits; the
    docket text is still the warrant. A row not yet re-read is screened out and
    waits for its refresh, which is why that re-read comes first.
    """
    row = corpus.get_row(conn, outcome.case_id)
    return row is not None and row.disposition in GRANTED_DISPOSITIONS


def converge_disposition_labels(
    conn: sqlite3.Connection,
    data_root: Path,
    *,
    apply: bool,
    max_relabels: int | None = None,
    include_scored: bool = False,
) -> DispositionConvergenceResult:
    """Re-resolve committed cert outcomes against their stored snapshots.

    Every ``granted`` outcome, and every ``denied`` / ``dismissed`` one whose
    corpus row records a grant (the ``restored-grant`` population).

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
    reason: an event id the moments table declares no stage for, no snapshot, a
    snapshot predating the resolution, a snapshot disclosing entries but none
    disposing, the recorded label already agreeing with the text, committed
    scored output, a resolution predating the era boundary that the
    ``disowned-grant`` warrant does not reach, a recorded resolution date the
    snapshot carries no entry for, a grant still standing on that date, an exit
    still standing on its recorded day, or a parse that disagrees but no arm
    names — the last of which this sweep deliberately declines to act on. Its
    remit is the three shapes named in the module docstring, not a licence to
    rewrite any label it now disagrees with. ``denied`` / ``dismissed`` outcomes
    the corpus screen passes over are counted in
    :attr:`DispositionConvergenceResult.screened`, not listed.
    """
    result = DispositionConvergenceResult(applied=apply)
    planned: list[tuple[Path, Outcome, dict[str, Any]]] = []
    for path in sorted((data_root / "cases").glob("*/*/events/*/outcome.json")):
        outcome = read_model(path, Outcome)
        # Equality, never identity: a validated artifact carries the plain string
        # (``use_enum_values``), so the recorded label is normalized back to a member
        # before it is reported or compared against the parser's own.
        recorded = Disposition(outcome.actual_disposition)
        if recorded is not Disposition.granted and recorded not in _WITHDRAWN_GRANT_LABELS:
            continue
        ref = f"{outcome.case_id}/{outcome.event_id}"
        verdict = _assess(conn, path, outcome, ref, include_scored=include_scored)
        if verdict is None:
            continue
        if isinstance(verdict, _Skip):
            if verdict.bucket == "screened":
                # Counted, never listed: it is most of the ledger.
                result.screened += 1
                continue
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
