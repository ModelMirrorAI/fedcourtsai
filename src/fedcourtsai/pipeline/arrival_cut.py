"""Where an interim arrival cell's snapshot stops: at the opening entry, not at the day.

The interim arrival moment is the instant an application reaches a Justice, and
a date-valued cutoff cannot express it. ``opened_at`` names a *day*, the cut
keeps everything filed strictly before the day after it, and a capital stay
application can be submitted, referred, responded to, drawn amici and denied
inside that one day. Every such entry postdates the moment the cell forecasts
and lands in its information set anyway — on the highest-salience interim shape,
where it matters most.

So the arrival cut is **positional as well as dated**: the snapshot is the docket
as of the opening entry itself. Entries filed before the opening day are kept
whatever their position; entries filed after it are dropped whatever their
position; and the opening day's own entries are kept only up to the opening
entry, so the same-day tail — a referral, a response request, an amicus, the
disposition — is outside the set by construction rather than by a per-kind
blocklist that the next docket shape defeats.

**Position is not channel-invariant, so it is never taken naively.** The two
upstream payload shapes pin no entry order between them: a naive ``entries[:i]``
on a newest-first list keeps precisely the half the cut exists to remove, and
does it silently. The kept set is therefore the intersection of two bounds —
the date bound above, and an anchor bound resolved against the list's *own*
observed chronology (:func:`docket_order`), which fails closed to the anchor
entry alone where the chronology cannot be read.

**Unanchorable rows refuse; they never fall back to the date cut.** The anchor is
the docket's own submission entry, dated at the event's stamped ``opened_at``
(:func:`~fedcourtsai.pipeline.interim_signals.application_arrival_date` reads the
same clause). Where the payload names none — a degraded payload, a consolidated
caption, or a stamp that no longer matches what the docket says — the moment's
information set cannot be located, and a cell provisioned on the date cut
instead would carry the defect this module exists to remove while recording that
it had been fixed. :func:`cut_at_arrival` returns ``None`` there and the caller
refuses the cell. Refusal could be outcome-correlated in a way that has to be
measured rather than assumed away — unanchorable, terse and summarily-disposed-of
are a plausible single shape — so :class:`ArrivalCutLedger` counts the refusals,
split by resolution status, by whether the docket was disposed of on its own
arrival day, and by cause. The cause split is what makes the count readable: a
stamp that disagrees with the docket is corpus convergence state the
arrival-backfill sweep converges, while a docket naming no submission entry is a
property of the case, and pooling the two reports a stale-stamp backlog as a
membership rule. Every figure is read over the **in-scope** rows as well as the
whole population, because the predict matrix mints cells only for substantive
applications and the population is dominated by time-extension dockets that are
themselves the terse same-day-disposed shape.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from itertools import pairwise
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..schemas import EventKind
from .cert_signals import PROCEEDINGS_KEYS, entry_date, proceedings_entries
from .interim_signals import (
    application_arrival_date,
    escalation_signals,
    match_interim_disposition,
)
from .prefetch import prefetch_by_case

#: The interim baseline's identity — the arrival moment every application docket
#: mints, and the one moment this cut governs. An entry-pinned motion event names
#: a specific filing rather than the docket's arrival, so it is out of scope.
MOTION_BASELINE_EVENT_ID = ids.event_id(EventKind.motion.value, "disposition")

#: How a provisioned snapshot's entries were bounded, as recorded on the cell's
#: context. ``date`` is the plain moment cut — every entry filed strictly before
#: the cutoff. ``arrival-position`` is that cut *and* the anchor bound this
#: module applies. Named here because the schema field, the provisioner and the
#: ledger must all mean the same thing by them.
CutKind = Literal["date", "arrival-position"]

#: The renewal form carries the submission verb without being the arrival — an
#: application refiled to a second Justice. Read the same way the arrival parser
#: reads it, so the anchor entry and the arrival date cannot disagree about
#: which entry opened the event.
_RENEWAL_RE = re.compile(r"\brefiled\b", re.I)


def payload_docket_number(payload: Mapping[str, Any]) -> str:
    """The application number the anchor clause recites, over either payload shape.

    Read from the payload rather than the corpus row for the same reason the
    cell's context is: the cut is a statement about what *this* document says, and
    an auditor re-reading the provisioned snapshot must be able to re-derive the
    anchor from it alone.

    **Annotation-stripped, which is load-bearing rather than tidy.** The live
    channel appends a marking to the number on some dockets — the capital-case
    flag among them — while ingest stores the number stripped
    (:func:`fedcourtsai.corpus.strip_docket_annotation`) and derives ``opened_at``
    from the stripped form. Reading the raw payload value here would build an
    anchor pattern no entry matches, and the cell would refuse. That would fall
    hardest on exactly the shape this module exists for: a capital stay
    application is the one most likely to be submitted and disposed of in a day
    and the one most likely to carry the marking.
    """
    raw = str(payload.get("docket_number") or payload.get("CaseNumber") or "").strip()
    return corpus.strip_docket_annotation(raw)


def _submission_re(docket_number: str) -> re.Pattern[str] | None:
    """The submission clause of *this* docket's own application number.

    The same anchor
    :func:`~fedcourtsai.pipeline.interim_signals.application_arrival_date` reads,
    and deliberately not a re-derivation of it: the number in its parentheses,
    then the filing verb within a bounded span. The number alone matches every
    later entry reciting it — most often the disposition — so the verb is what
    keeps the anchor on the head entry.
    """
    number = docket_number.strip()
    if not number:
        return None
    return re.compile(
        r"application\s*\(\s*" + re.escape(number) + r"\s*\).{0,200}?\bsubmitted\b", re.I
    )


def docket_order(
    entries: Sequence[tuple[str, str | None]],
) -> Literal["ascending", "descending"] | None:
    """Which way ``entries`` runs in time, or ``None`` where it cannot be read.

    The anchor bound is a statement about the docket's own sequence, and the
    payload shapes pin none: the live supremecourt.gov list is append-only and
    runs oldest-first, while the REST record's order is whatever the upstream
    query produced. Reading the direction off the parsed dates rather than
    assuming it is what stops a newest-first list from keeping the wrong half.

    ``ascending`` where the parsed dates never decrease *and* rise at least once;
    ``descending`` for the mirror. ``None`` — the chronology says nothing — in
    the two cases that matter and for the same reason: a list whose dates are all
    equal (the whole docket filed in one day, which is exactly the shape this
    module was built for) is consistent with either direction, and a
    non-monotone list is consistent with neither. The caller fails closed on it.

    Undated entries are skipped rather than treated as breaks: an entry the
    date parser cannot read is dropped by the date bound anyway, and letting one
    make the whole docket unreadable would refuse cells the anchor could place.
    """
    dates = [parsed for _, raw in entries if (parsed := entry_date(raw)) is not None]
    rises = any(before < after for before, after in pairwise(dates))
    falls = any(before > after for before, after in pairwise(dates))
    if rises and not falls:
        return "ascending"
    if falls and not rises:
        return "descending"
    return None


def anchor_index(
    entries: Sequence[tuple[str, str | None]], *, docket_number: str, opened_at: date
) -> int | None:
    """Position of the entry that opened the event, or ``None`` where none does.

    The anchor is a submission entry of this docket's own application number
    whose date is the event's **stamped** ``opened_at``. Requiring the stamp to
    match is what makes the cut and the event agree about which entry the moment
    is: a row whose stamp has gone stale against its docket names an anchor the
    payload does not carry, and refusing it is preferable to cutting at an entry
    the event was never opened at.

    Where several submission entries share that date — a head entry re-docketed
    the same day — the **docket-order-earliest** wins, mirroring the arrival
    parser's ``min``. That is the conservative choice in the only direction that
    matters: it admits the smaller same-day prefix.
    """
    pattern = _submission_re(docket_number)
    if pattern is None:
        return None
    matches = [
        index
        for index, (text, raw) in enumerate(entries)
        if not _RENEWAL_RE.search(text) and pattern.search(text) and entry_date(raw) == opened_at
    ]
    if not matches:
        return None
    return matches[0] if docket_order(entries) != "descending" else matches[-1]


def same_day_tail(
    entries: Sequence[tuple[str, str | None]], *, anchor: int, opened_at: date
) -> frozenset[int]:
    """Indices of the opening day's entries that fall *after* the opening entry.

    The positional half of the cut, and the only half that needs the list's
    direction: entries dated before the opening day are kept wherever they sit,
    entries dated after it are dropped wherever they sit, and only the opening
    day's own run has to be split around the anchor.

    Fails closed where :func:`docket_order` reads nothing — every same-day entry
    but the anchor goes. That is the right default for the shape that produces
    it: a docket whose entries are all one date is an application submitted,
    referred and disposed of in a day, where the opening entry is the whole of
    what the arrival moment saw.
    """
    order = docket_order(entries)
    tail: set[int] = set()
    for index, (_, raw) in enumerate(entries):
        if index == anchor or entry_date(raw) != opened_at:
            continue
        if order == "ascending" and index < anchor:
            continue
        if order == "descending" and index > anchor:
            continue
        tail.add(index)
    return frozenset(tail)


@dataclass(frozen=True)
class CutBoundary:
    """What bounded a provisioned snapshot, as the cell's context records it.

    The two halves travel together by construction — an ``arrival-position`` kind
    is meaningless without the anchor it stopped at, and an anchor index is
    meaningless under any other kind — so the builder takes one object rather
    than two parameters a caller could set inconsistently.
    """

    kind: CutKind
    anchor_index: int | None = None


@dataclass(frozen=True)
class ArrivalCut:
    """A payload cut at its opening entry, and what the anchor bound removed.

    ``payload`` still carries every entry the *date* bound admits: this is the
    anchor bound alone, so a caller on the reconstruction branch composes it with
    the ordinary truncation and a caller on the ``dated`` branch — whose payload
    the docket really served before the cutoff, and whose entries are therefore
    already inside the date bound — applies nothing else.

    ``dropped_same_day`` is the size of the tail, and ``dropped_a_disposition``
    whether the tail carried this application's own disposition. The second is
    the leak the positional cut exists to close, counted rather than asserted.
    """

    payload: dict[str, Any]
    anchor_index: int
    dropped_same_day: int
    dropped_a_disposition: bool


def cut_at_arrival(
    payload: Mapping[str, Any], *, docket_number: str, opened_at: date
) -> ArrivalCut | None:
    """``payload`` as the docket stood at its opening entry, or ``None`` to refuse.

    ``None`` where the opening entry cannot be anchored — no proceedings list, no
    usable application number, or no submission entry stamped at ``opened_at``.
    The caller refuses the cell and counts it; there is deliberately no date-cut
    fallback, because that is the conditioning this cut replaces.

    **Positions are translated, never assumed to line up.**
    :func:`~fedcourtsai.pipeline.cert_signals.proceedings_entries` skips a
    non-mapping element, so the read view and the stored list can differ in
    length and an index from one means a different entry in the other. Applying a
    read-view index to the stored list would drop the wrong entries — and it
    fails *open*: on a list whose first element is not a mapping it removes the
    submission entry and keeps the same-day disposition, while the context records
    that the tighter bound ran. ``kept_positions`` maps every read-view index back
    to the element it was read from, so the two can never disagree.
    """
    key = next((k for k in PROCEEDINGS_KEYS if isinstance(payload.get(k), list)), None)
    if key is None:
        return None
    raw_entries = list(payload[key])
    positions = [index for index, entry in enumerate(raw_entries) if isinstance(entry, Mapping)]
    entries = proceedings_entries(payload)
    if len(positions) != len(entries):
        # The two readings disagree about what an entry is, so no index is
        # trustworthy. Fail closed rather than cut at a position that may name a
        # different filing than the one it was chosen for.
        return None
    anchor = anchor_index(entries, docket_number=docket_number, opened_at=opened_at)
    if anchor is None:
        return None
    tail = same_day_tail(entries, anchor=anchor, opened_at=opened_at)
    dropped_a_disposition = any(
        match_interim_disposition(entries[index][0]) is not None for index in tail
    )
    dropped_positions = {positions[index] for index in tail}
    out = dict(payload)
    out[key] = [entry for index, entry in enumerate(raw_entries) if index not in dropped_positions]
    return ArrivalCut(
        payload=out,
        # Reported as a position in the payload's own list, not in the read view,
        # so an auditor counting entries in the stored snapshot lands on the entry
        # the cut was taken at.
        anchor_index=positions[anchor],
        dropped_same_day=len(tail),
        dropped_a_disposition=dropped_a_disposition,
    )


class ArrivalCutRow(BaseModel):
    """One interim arrival row's reading under the positional cut."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    resolved: bool = Field(description="Whether the application has been disposed of.")
    application_kind: str = Field(
        default="",
        description="The application's form — `substantive`, `extension`, or unknown. The "
        "scope key, and no aggregate here is readable without it: the predict matrix drops "
        "every non-substantive application (`corpus.out_of_scope_reason_full` via "
        "`is_non_cert_scotus_form`), and extensions dominate the population while being "
        "structurally the terse, same-day-disposed shape. A figure pooled over kinds "
        "describes a set most of which can never be provisioned a cell.",
    )
    in_predict_scope: bool = Field(
        default=False,
        description="Whether a predict cell can be minted for this row at all — the "
        "denominator every operational rate is read over.",
    )
    anchored: bool = Field(
        description="Whether the opening entry could be located in the row's stored "
        "snapshot. False refuses the cell."
    )
    refusal: Literal["", "no-submission-entry", "stale-stamp"] = Field(
        default="",
        description="Why an unanchored row refuses, empty on an anchored one. The two "
        "causes are not the same finding and must not be pooled: 'no-submission-entry' "
        "is a docket whose payload names no dated submission clause at all — the "
        "outcome-correlated class, since terse dockets are disproportionately "
        "summarily disposed of — while 'stale-stamp' is a docket that names one whose "
        "date is not what `events.opened_at` holds, which is a corpus convergence "
        "state the arrival-backfill sweep repairs rather than a property of the case.",
    )
    same_day_tail: int = Field(
        default=0,
        ge=0,
        description="Entries the anchor bound removes that the date cut admits — the "
        "same-day-after-opening-entry tail. Zero on a refused row, where the cut "
        "took nothing because the cell does not run.",
    )
    tail_carries_disposition: bool = Field(
        default=False, description="Whether that tail carried the application's own disposition."
    )
    same_day_disposition: bool = Field(
        default=False,
        description="Whether the docket records a disposition dated on the day the "
        "application was SUBMITTED — read from the payload's own submission entry "
        "(`application_arrival_date`), never from `events.opened_at`. The distinction is "
        "the whole value of the field on a refused row: a `stale-stamp` refusal IS the "
        "finding that the stamp names no submission entry, so a same-day read taken "
        "against the stamp would answer a question about the wrong day. False where the "
        "payload names no datable submission entry, since there is then no arrival day to "
        "read against.",
    )
    amicus_tail: int = Field(
        default=0, ge=0, description="Amicus entries inside that tail (the interim-v1 claim)."
    )
    response_requested_in_tail: bool = Field(
        default=False,
        description="Whether the tail carried the Court's response request, which the "
        "date cut let the cell read as already granted.",
    )
    referred_in_tail: bool = Field(
        default=False, description="Whether the tail carried the referral to the full Court."
    )


class ArrivalCutLedger(BaseModel):
    """What the positional cut does over the interim arrival provisioning population.

    A dry-run reading, not a record of provisioned cells: it is computed over each
    row's newest stored snapshot, so it states what a cell provisioned against the
    corpus at ``corpus_vintage`` would carry. Two things it is deliberately not.
    It is **not** the arrival-backfill pass's ``over_admitted`` band, which is open
    on the arrival day by construction and is therefore identically zero on this
    delta — the quantity here is the same-day tail that band excludes. And its
    denominator is the **provisioning population**, every interim arrival row a
    cell can be minted for, not the repair pass's defective-stamp candidates.

    The refusal arm is split by resolution status and by same-day disposition
    because unanchorable, terse and summarily-disposed-of are a plausible single
    shape: a membership rule that drops rows correlated with the outcome has to be
    measured to be readable, and the split is what makes it so.
    """

    model_config = ConfigDict(extra="forbid")

    corpus_vintage: date | None = Field(
        default=None,
        description="Newest pull stamp in the blob the reading was taken from. Every "
        "figure below is as at this vintage and states it, because the population "
        "and the tails both move with the corpus.",
    )
    rows_seen: int = Field(
        ge=0,
        description="Interim arrival rows carrying a stamp at all. NOT the population any "
        "operational rate is read over — see `scope_rows`, which is the subset a predict "
        "cell can be minted for.",
    )
    scope_rows: int = Field(
        default=0,
        ge=0,
        description="Rows a predict cell can actually be minted for: substantive "
        "applications, the only interim form the matrix does not drop "
        "(`corpus.out_of_scope_reason_full` via `is_non_cert_scotus_form`). Every rate below "
        "that describes the pipeline is read over THIS, because the remainder — dominated by "
        "time-extension applications, which are structurally the terse same-day-disposed "
        "shape — can never produce a cell and would bias every figure toward it.",
    )
    kind_counts: dict[str, int] = Field(
        default_factory=dict,
        description="The population split by application form, so the composition behind any "
        "pooled figure is visible rather than implied.",
    )
    scope_anchored: int = Field(default=0, ge=0, description="In-scope rows that anchored.")
    scope_refused: int = Field(default=0, ge=0, description="In-scope rows refused.")
    scope_tail_rows: int = Field(
        default=0, ge=0, description="In-scope rows carrying a same-day tail."
    )
    scope_tail_entries: int = Field(
        default=0, ge=0, description="Entries in those in-scope tails — the delta that governs."
    )
    scope_tail_carries_disposition: int = Field(
        default=0, ge=0, description="In-scope tails carrying the application's own disposition."
    )
    scope_pending_rows: int = Field(
        default=0,
        ge=0,
        description="Undisposed-of IN-SCOPE rows — the forward lane's true denominator, and "
        "the only one an operational refusal rate may be quoted against.",
    )
    scope_pending_anchored: int = Field(default=0, ge=0, description="Of those, anchored.")
    scope_pending_refused: int = Field(default=0, ge=0, description="Of those, refused.")
    no_snapshot: int = Field(
        default=0, ge=0, description="Rows holding no stored snapshot to read at all."
    )
    anchored: int = Field(default=0, ge=0, description="Rows whose opening entry was located.")
    refused: int = Field(
        default=0, ge=0, description="Rows refused because it was not — the membership rule."
    )
    refused_resolved: int = Field(default=0, ge=0, description="Refusals on a disposed-of row.")
    refused_same_day_disposition: int = Field(
        default=0, ge=0, description="Refusals on a row disposed of on its arrival day."
    )
    refused_no_submission_entry: int = Field(
        default=0,
        ge=0,
        description="Refusals whose payload names no dated submission clause at all — the "
        "class an outcome correlation would run through, if it runs anywhere. Read it as "
        "the hypothesis this split exists to test rather than as an established property "
        "of the class: the arm is small, and a rate over a handful of rows supports "
        "nothing.",
    )
    refused_no_submission_entry_resolved: int = Field(
        default=0, ge=0, description="Of those, disposed-of rows."
    )
    refused_stale_stamp: int = Field(
        default=0,
        ge=0,
        description="Refusals whose payload names a submission entry on a date "
        "`events.opened_at` does not hold. A corpus convergence state, not a property of "
        "the case: `opened_at` takes no fill-in latch on the upsert path and the arrival "
        "read is live-branch-only, so a non-live re-extraction writes the docketing date "
        "back over a repaired stamp, and the arrival-backfill sweep moves it again. Read "
        "this count as a freshness reading of the stamps, and re-dispatch that sweep "
        "rather than concluding anything about the dockets.",
    )
    refused_stale_stamp_resolved: int = Field(
        default=0, ge=0, description="Of those, disposed-of rows."
    )
    pending_rows: int = Field(
        default=0,
        ge=0,
        description="Undisposed-of rows across the whole stamped population, in scope or not. "
        "Reported for completeness only: `scope_pending_rows` is the forward lane's "
        "denominator, since a non-substantive application never reaches the matrix however "
        "open it is.",
    )
    pending_anchored: int = Field(default=0, ge=0, description="Of those, anchored.")
    pending_refused: int = Field(default=0, ge=0, description="Of those, refused.")
    anchored_resolved: int = Field(
        default=0,
        ge=0,
        description="Anchored rows that are disposed of — the refusal split's base.",
    )
    tail_rows: int = Field(
        default=0, ge=0, description="Anchored rows carrying a same-day-after-opening-entry tail."
    )
    tail_rows_resolved: int = Field(default=0, ge=0, description="Of those, disposed-of rows.")
    tail_entries: int = Field(
        default=0, ge=0, description="Entries in those tails — the separately named quantity."
    )
    tail_carries_disposition: int = Field(
        default=0,
        ge=0,
        description="Rows whose tail carried the application's own disposition: the leak the "
        "date cut admits and this cut removes.",
    )
    amicus_shift_rows: int = Field(
        default=0,
        ge=0,
        description="Rows whose frozen amicus count falls under the cut. An UPPER BOUND on "
        "the interim-v1 amicus-increment claim's new positives, not a count of them: the "
        "claim is `outcome.amicus > context.amicus`, so lowering the frozen count flips a "
        "row only where the claim was not already positive, and a docket that gained a later "
        "amicus resolved positive under both readings.",
    )
    amicus_shift_entries: int = Field(
        default=0, ge=0, description="Amicus entries removed across those rows."
    )
    response_requested_unmasked: int = Field(
        default=0,
        ge=0,
        description="Rows whose frozen response-requested flag falls from true to false, moving "
        "the increment claim from vacuously masked to resolvable.",
    )
    response_requested_unmasked_resolved: int = Field(
        default=0, ge=0, description="Of those, disposed-of rows."
    )
    referral_unmasked: int = Field(
        default=0, ge=0, description="The same move on the referral increment claim."
    )
    referral_unmasked_resolved: int = Field(
        default=0, ge=0, description="Of those, disposed-of rows."
    )
    rows: list[ArrivalCutRow] = Field(
        default_factory=list, description="Per-row readings, case_id-ordered."
    )


@dataclass(frozen=True)
class _Row:
    """One interim arrival row of the provisioning population."""

    case_id: str
    docket_number: str
    opened_at: date
    resolved: bool
    application_kind: str

    @property
    def in_predict_scope(self) -> bool:
        """Whether the matrix can mint a cell for this row.

        Substantive applications only: every other interim form is dropped by
        :func:`fedcourtsai.corpus.is_non_cert_scotus_form`, so a figure pooled over
        forms describes a population most of which can never be provisioned.
        """
        return self.application_kind == "substantive"


def provisioning_population(conn: corpus.ReadConnection) -> tuple[_Row, ...]:
    """Every interim arrival row a cell can be provisioned for, case_id-ordered.

    The **provisioning** population, which is not the arrival-backfill pass's:
    that pass selects the rows whose stamp shows the defect, while a cut is taken
    on every row whose stamp exists at all. ``opened_at IS NOT NULL`` is the whole
    of the predicate's substance —
    :func:`~fedcourtsai.provision.moment_cutoff` returns ``None`` without one, so
    an unstamped row takes no cut and this cut cannot reach it. Live-slice,
    because the reading is taken from a stored live-shaped snapshot; the rows
    outside it hold none and are unmeasured here rather than counted as clean.
    """
    live = corpus.live_slice_sql("c")
    rows = conn.execute(
        "SELECT e.case_id AS case_id, e.opened_at AS opened_at, e.resolved AS resolved, "
        "c.docket_number AS docket_number, c.application_kind AS application_kind "
        "FROM events e JOIN cases c ON c.case_id = e.case_id "
        f"WHERE e.event_id = ? AND e.court = 'scotus' AND {live} "
        "AND e.docket_entry_id IS NULL AND e.opened_at IS NOT NULL "
        "ORDER BY e.case_id",
        (MOTION_BASELINE_EVENT_ID,),
    ).fetchall()
    return tuple(
        _Row(
            case_id=str(record["case_id"]),
            docket_number=str(record["docket_number"] or ""),
            opened_at=date.fromisoformat(str(record["opened_at"])),
            resolved=bool(record["resolved"]),
            application_kind=str(record["application_kind"] or ""),
        )
        for record in rows
    )


def _read_row(row: _Row, snapshot: tuple[date, dict[str, Any]] | None) -> ArrivalCutRow | None:
    """One row's reading, or ``None`` where no snapshot could be read for it."""
    if snapshot is None:
        return None
    _, payload = snapshot
    entries = proceedings_entries(payload)
    # Read against the DOCKET's own arrival, never against `events.opened_at`.
    # The distinction is the whole value of this field on a refused row: a
    # `stale-stamp` refusal *is* the finding that the stamp names no submission
    # entry, so a same-day read taken against the stamp would answer a question
    # about a day the application did not arrive on — and the refusal split exists
    # precisely to be read against the same-day-disposed shape.
    arrival = application_arrival_date(row.docket_number, entries) if row.docket_number else None
    same_day_disposition = arrival is not None and any(
        entry_date(raw) == arrival and match_interim_disposition(text) is not None
        for text, raw in entries
    )
    cut = cut_at_arrival(payload, docket_number=row.docket_number, opened_at=row.opened_at)
    if cut is None:
        # Which refusal this is decides what may be read off it, so the two are
        # separated at the point the cause is still visible. A docket naming a
        # submission entry the stamp disagrees with is a stamp that has drifted;
        # one naming none at all is the terse shape the outcome correlation runs
        # through.
        return ArrivalCutRow(
            case_id=row.case_id,
            resolved=row.resolved,
            application_kind=row.application_kind,
            in_predict_scope=row.in_predict_scope,
            anchored=False,
            refusal="stale-stamp" if arrival is not None else "no-submission-entry",
            same_day_disposition=same_day_disposition,
        )
    # The two readings of the same docket that the claim-side deltas are the
    # difference between: the escalation trio as the date cut froze it, and as
    # the anchor bound freezes it. Both over the cell's own payload, so a shift
    # here is exactly the shift the cell's `context.json` will carry.
    before_response, before_referral, before_amici = escalation_signals([t for t, _ in entries])
    kept_texts = [t for t, _ in proceedings_entries(cut.payload)]
    after_response, after_referral, after_amici = escalation_signals(kept_texts)
    return ArrivalCutRow(
        case_id=row.case_id,
        resolved=row.resolved,
        application_kind=row.application_kind,
        in_predict_scope=row.in_predict_scope,
        anchored=True,
        same_day_tail=cut.dropped_same_day,
        tail_carries_disposition=cut.dropped_a_disposition,
        same_day_disposition=same_day_disposition,
        amicus_tail=max(0, before_amici - after_amici),
        response_requested_in_tail=before_response and not after_response,
        referred_in_tail=before_referral and not after_referral,
    )


def _tally(ledger: ArrivalCutLedger, reading: ArrivalCutRow) -> None:
    """Fold one row's reading into the aggregates.

    Three denominators accumulate side by side and are never merged: the whole
    stamped population, the in-scope subset a predict cell can be minted for, and
    the pending arm of each. The refusal arm splits by cause on top of that,
    because a stamp that has drifted and a docket that names no submission entry
    are different findings.
    """
    ledger.kind_counts[reading.application_kind or "unknown"] = (
        ledger.kind_counts.get(reading.application_kind or "unknown", 0) + 1
    )
    if reading.in_predict_scope:
        ledger.scope_rows += 1
        ledger.scope_anchored += int(reading.anchored)
        ledger.scope_refused += int(not reading.anchored)
        ledger.scope_tail_carries_disposition += int(reading.tail_carries_disposition)
        if reading.same_day_tail:
            ledger.scope_tail_rows += 1
            ledger.scope_tail_entries += reading.same_day_tail
        if not reading.resolved:
            ledger.scope_pending_rows += 1
            ledger.scope_pending_anchored += int(reading.anchored)
            ledger.scope_pending_refused += int(not reading.anchored)
    if not reading.resolved:
        ledger.pending_rows += 1
        ledger.pending_anchored += int(reading.anchored)
        ledger.pending_refused += int(not reading.anchored)
    if not reading.anchored:
        ledger.refused += 1
        ledger.refused_resolved += int(reading.resolved)
        ledger.refused_same_day_disposition += int(reading.same_day_disposition)
        if reading.refusal == "no-submission-entry":
            ledger.refused_no_submission_entry += 1
            ledger.refused_no_submission_entry_resolved += int(reading.resolved)
        else:
            ledger.refused_stale_stamp += 1
            ledger.refused_stale_stamp_resolved += int(reading.resolved)
        return
    ledger.anchored += 1
    ledger.anchored_resolved += int(reading.resolved)
    if reading.same_day_tail:
        ledger.tail_rows += 1
        ledger.tail_rows_resolved += int(reading.resolved)
        ledger.tail_entries += reading.same_day_tail
    ledger.tail_carries_disposition += int(reading.tail_carries_disposition)
    if reading.amicus_tail:
        ledger.amicus_shift_rows += 1
        ledger.amicus_shift_entries += reading.amicus_tail
    if reading.response_requested_in_tail:
        ledger.response_requested_unmasked += 1
        ledger.response_requested_unmasked_resolved += int(reading.resolved)
    if reading.referred_in_tail:
        ledger.referral_unmasked += 1
        ledger.referral_unmasked_resolved += int(reading.resolved)


def arrival_cut_ledger(
    conn: corpus.ReadConnection, *, corpus_vintage: date | None
) -> ArrivalCutLedger:
    """What the positional cut does over the whole interim arrival population.

    A dry run over stored state, and the executed check behind every figure the
    freeze-record entry registers for this conditioning change. It provisions
    nothing and writes nothing: each row's newest live-shaped snapshot is read,
    cut, and the two readings compared, so the answer is what a cell provisioned
    against this blob would carry rather than what any committed cell was shown.
    """
    rows = provisioning_population(conn)
    ledger = ArrivalCutLedger(corpus_vintage=corpus_vintage, rows_seen=len(rows))
    if not rows:
        return ledger
    readings: list[ArrivalCutRow] = []
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="arrival-cut",
    ) as fetched:
        for row, (_, snapshot) in zip(rows, fetched, strict=True):
            reading = _read_row(row, snapshot)
            if reading is None:
                ledger.no_snapshot += 1
                continue
            readings.append(reading)
    for reading in readings:
        _tally(ledger, reading)
    ledger.rows = readings
    return ledger
