"""Back-fill of the interim baseline's arrival stamp, which no channel revisits.

An interim event's ``opened_at`` is the moment it declares — the day the
application was submitted to a Justice — and it is where provisioning cuts, so
what is stamped there decides what a cell for that moment is allowed to see. The
arrival is read from the docket's own submission entry
(:func:`~fedcourtsai.pipeline.interim_signals.application_arrival_date`) on the
live ingest branch, with the docketing date as the fallback where no entry
carries a readable one.

**The defect is a stamp rule correlated with the outcome.** The live poller
serves the *unresolved* slice, so a decided application has left the rotation
and is never re-polled: an event minted or last polled before the arrival read
existed keeps whatever it had, which is the docketing date or nothing at all.
Resolution status therefore decides which reading a row carries. Forward cells
are unresolved by construction and unaffected, but any retrospective interim
population drawn from these events inherits that conditioning — which is exactly
the kind of rule a cohort must not be built on.

- **Population.** SCOTUS interim baseline events (``evt-motion-disposition``,
  ``docket_entry_id`` null, so an entry-pinned event naming a specific filing is
  never touched — the arrival derivation is the wrong reading for one) whose
  stamp shows the defect: **no stamp at all**, or **the docketing date**, which
  is the fallback shape a row that never got the arrival read carries. Both
  arms, because the split the defect creates has both halves. Live-slice, since
  the repair reads the stored live-shaped snapshot.

  Deliberately **not** predicated on resolution, even though the class is
  overwhelmingly decided rows: repairing only the decided half would leave the
  population conditioned on resolution status all over again, and re-deriving an
  unresolved row costs one stored-snapshot read and converges to what its next
  poll would write anyway.
- **Route.** The response back-fill's exactly: re-parse each row's newest stored
  live-shaped snapshot with the same pure parsers ingest uses, rather than
  re-fetching a fact already stored. The renewal exclusion comes along with the
  parser — an application refiled to a second Justice carries the filing verb
  and is never the arrival.
- **Direction is a safety property, not a detail.** The cut keeps everything
  filed strictly before the day after ``opened_at``, so a **later** stamp admits
  more and an **earlier** one admits less. Docketing is systematically the later
  of the two readings, which is why the repair moves stamps *earlier* and why a
  parse that would move one **later** is refused rather than written: that is
  the enlarging direction, and this pass exists to remove enlargement rather
  than to introduce it. Refused rows are named.
- **What the ledger has to state.** How many rows changed stamp and by how much.
  A retrospective interim cohort's conditioning depends on that number: it is
  the size of the window each repaired row had been over-admitting by, so a
  histogram of the day deltas is what says whether the pre-repair population was
  merely late or was seeing its own disposition.

One limitation this pass cannot fix and must not hide: ``events.opened_at``
carries no fill-in latch on the upsert path (every event column but ``resolved``
takes the incoming value), and the arrival read is live-branch-only. A **non-live**
re-extraction of an application docket therefore writes the docketing date back
over a repaired stamp, in the enlarging direction. The predicate above re-selects
such a row — the docketing arm is exactly that shape — so successive dispatches
converge it again, but the pass is a sweep against a live regression rather than
a one-time repair.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..schemas import EventKind
from .cert_signals import proceedings_entries
from .interim_signals import application_arrival_date
from .prefetch import prefetch_by_case

#: The interim baseline's identity — the event every application docket mints,
#: as opposed to an entry-pinned motion event naming one specific filing.
MOTION_BASELINE_EVENT_ID = ids.event_id(EventKind.motion.value, "disposition")

#: The day-delta buckets the ledger reports a moved stamp in, in order. Each is
#: an inclusive upper bound on the days a stamp moved *earlier*; the last bucket
#: is open. Buckets rather than a mean because the distribution is what matters:
#: a class that moved a median 5 days with a tail past a month is a different
#: reading from one that moved 5 days uniformly, and only the second is safely
#: describable as "merely late".
MOVE_BUCKETS: tuple[tuple[str, int | None], ...] = (
    ("1", 1),
    ("2-3", 3),
    ("4-7", 7),
    ("8-14", 14),
    ("15-30", 30),
    ("31+", None),
)


class ArrivalFill(BaseModel):
    """One event row's repaired arrival stamp, with what it replaces."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    event_id: str
    opened_at: date = Field(description="The arrival the stored snapshot's submission entry names")
    previous: date | None = Field(
        default=None,
        description="The stamp being replaced — the docketing date, or null where "
        "the row carried none. What separates a fill from a move, which the "
        "histogram counts apart",
    )

    @property
    def moved_days(self) -> int | None:
        """How many days earlier this stamp moves, or ``None`` where there was none."""
        return None if self.previous is None else (self.previous - self.opened_at).days


class ArrivalBackfillResult(BaseModel):
    """What the arrival back-fill wrote, or would write on a dry run."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the stamps or only counted them")
    events_seen: int = Field(
        ge=0,
        description="SCOTUS interim baseline events the walk read at all — the "
        "denominator under `candidates`. Zero means the population could not be "
        "read rather than that the class is empty, so the caller refuses on it: a "
        "blob carrying no interim events would otherwise report a clean pass over nothing",
    )
    candidates: int = Field(
        ge=0,
        description="Events showing the defect — no stamp, or the docketing date — "
        "in `case_id` order. The whole population this route can act on",
    )
    filled: list[ArrivalFill] = Field(
        default_factory=list,
        description="The rows whose stamp this run wrote (or would), each naming "
        "the arrival it takes and the stamp it replaces",
    )
    stamped: int = Field(
        ge=0,
        default=0,
        description="Of `filled`, the rows that carried no stamp at all. Counted "
        "apart because no day delta is measurable for them: an unstamped interim "
        "event takes no cut whatsoever, so what it gains is not a tightening of a "
        "window but the window itself",
    )
    moved: int = Field(
        ge=0,
        default=0,
        description="Of `filled`, the rows whose stored docketing stamp moves "
        "earlier. `move_histogram` says by how much",
    )
    move_histogram: dict[str, int] = Field(
        default_factory=dict,
        description="The moved rows' day deltas, bucketed (`MOVE_BUCKETS`) and "
        "zero-filled in order. The reading a retrospective interim cohort's "
        "conditioning depends on: each bucket counts rows whose pre-repair cut "
        "admitted that many extra days of docket beyond the declared moment",
    )
    move_days_max: int = Field(
        ge=0,
        default=0,
        description="The largest single move, in days — the worst case the "
        "histogram's open bucket hides",
    )
    unchanged: int = Field(
        ge=0,
        default=0,
        description="Candidates whose stored stamp already equals the arrival the "
        "snapshot names. Not a failure and not the converged class: an application "
        "docketed the day it was submitted reads this way and is correct already",
    )
    later_refused: list[str] = Field(
        default_factory=list,
        description="Candidates whose parsed arrival **postdates** the stored "
        "stamp, in class order. Refused rather than written: the cut keeps "
        "everything filed before the day after `opened_at`, so a later stamp "
        "admits more docket, which is the enlargement this pass exists to remove. "
        "A non-empty list is a reading to chase — the parser anchors on the "
        "submission entry, which precedes docketing on every docket sampled for "
        "the rule",
    )
    no_snapshot: int = Field(
        ge=0,
        default=0,
        description="Candidates with no stored live-shaped snapshot to parse. Not "
        "evidence of a clean corpus, just of an unreadable one — under the corpus "
        "split the payloads live in the content store, and a poll that 404-stamped "
        "without storing one leaves nothing to re-read",
    )
    no_proceedings: int = Field(
        ge=0,
        default=0,
        description="Candidates whose newest live-shaped snapshot carries an empty "
        "proceedings list, so the arrival is unobservable from it rather than "
        "absent from the docket. Separated from `no_snapshot` by the *key*, not "
        "the entries: a payload carrying no proceedings key at all is the other "
        "channel's shape and is never selected as the live snapshot, so it lands "
        "there instead",
    )
    unparsed: int = Field(
        ge=0,
        default=0,
        description="Candidates read and parsed whose proceedings name no dated "
        "submission entry for their own number — a docket whose head entry is "
        "missing from the stored payload, or one carrying only the renewal form "
        "the parser excludes. These keep the docketing fallback, which is late in "
        "the safe direction",
    )
    bound: int | None = Field(
        default=None,
        description="The blast-radius bound this run was checked against — the "
        "rows actually written, not the `candidates` denominator beside them",
    )
    refused: bool = Field(
        default=False,
        description="True when an apply was asked for and the bound refused it. "
        "Nothing is written in that case — reported as a field and not only as an "
        "exit code, so a witness reading the ledger sees the refusal",
    )


@dataclass(frozen=True)
class _Candidate:
    """One event row in the class, with what the re-derivation needs."""

    case_id: str
    event_id: str
    docket_number: str
    opened_at: date | None


@dataclass
class _Tally:
    """What the walk has recorded so far, accumulated across its candidates."""

    filled: list[ArrivalFill] = field(default_factory=list)
    later_refused: list[str] = field(default_factory=list)
    no_snapshot: int = 0
    no_proceedings: int = 0
    unparsed: int = 0
    unchanged: int = 0


def _stored_date(record: sqlite3.Row, column: str) -> date | None:
    raw = record[column]
    return date.fromisoformat(str(raw)) if raw else None


def _move_bucket(days: int) -> str:
    """The histogram bucket a move of ``days`` falls in."""
    for label, upper in MOVE_BUCKETS:
        if upper is None or days <= upper:
            return label
    raise AssertionError("MOVE_BUCKETS must end in an open bucket")


def _histogram(fills: list[ArrivalFill]) -> tuple[dict[str, int], int]:
    """The moved rows' day deltas, bucketed and zero-filled, and the largest.

    Zero-filled and in bucket order by construction, so an absent bucket in the
    ledger is never an omitted one — a reader comparing two dispatches' ledgers
    reads the same keys in the same order either way.
    """
    counts = {label: 0 for label, _ in MOVE_BUCKETS}
    largest = 0
    for fill in fills:
        days = fill.moved_days
        if days is None:
            continue
        counts[_move_bucket(days)] += 1
        largest = max(largest, days)
    return counts, largest


def arrival_candidates(conn: sqlite3.Connection) -> tuple[list[_Candidate], int]:
    """The interim baseline events showing the stamp defect, and the denominator.

    Two arms in one predicate, because the defect has two shapes and they are the
    same defect: a row that never got an arrival read carries the docketing date
    where one is stored and nothing where it is not. Joined to ``cases`` because
    the docketing date and the docket number both live there, and a row whose
    case is absent is out of scope rather than acted on — neither the fallback it
    is being compared against nor the number the parser anchors on can be read
    for it.

    The denominator returned beside the class is every baseline interim event in
    the live slice, which is what tells a converged corpus apart from one this
    process cannot read.
    """
    seen = conn.execute(
        "SELECT COUNT(*) FROM events e JOIN cases c ON c.case_id = e.case_id "
        f"WHERE e.event_id = ? AND e.court = 'scotus' AND {corpus.LIVE_SLICE_SQL}",
        (MOTION_BASELINE_EVENT_ID,),
    ).fetchone()[0]
    rows = conn.execute(
        "SELECT e.case_id AS case_id, e.event_id AS event_id, e.opened_at AS opened_at, "
        "c.docket_number AS docket_number FROM events e JOIN cases c ON c.case_id = e.case_id "
        f"WHERE e.event_id = ? AND e.court = 'scotus' AND {corpus.LIVE_SLICE_SQL} "
        # An entry-pinned motion event names one specific filing rather than the
        # docket's arrival, so the arrival derivation is the wrong reading for it.
        "AND e.docket_entry_id IS NULL "
        "AND (e.opened_at IS NULL OR e.opened_at = c.date_filed) "
        "ORDER BY e.case_id, e.event_id",
        (MOTION_BASELINE_EVENT_ID,),
    ).fetchall()
    return [
        _Candidate(
            case_id=str(record["case_id"]),
            event_id=str(record["event_id"]),
            docket_number=str(record["docket_number"] or ""),
            opened_at=_stored_date(record, "opened_at"),
        )
        for record in rows
    ], int(seen)


def backfill_arrival_stamps(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_fills: int | None = None,
) -> ArrivalBackfillResult:
    """Re-derive the interim baseline's arrival stamp from each row's newest snapshot.

    ``max_fills`` is the blast-radius bound and lives here rather than in the
    caller, so a code caller is bounded on the same terms as the command. It
    counts the rows actually **written**, not the ``candidates`` denominator
    beside them, and over it nothing is written and ``refused`` is set — a
    refusal threshold rather than a slice, because this pass reaches no network
    and its whole cost is the population read it has already paid before the
    bound is checked.

    The write moves a stamp **earlier** or supplies a missing one, never later:
    the cut keeps everything filed strictly before the day after ``opened_at``,
    so a later stamp would admit more docket than the declared moment saw. A
    parse that would move one later is named in ``later_refused`` and not
    written.

    Convergent but not terminal: a repaired row leaves the class, and a stored
    stamp equal to the arrival keeps it out — but ``events.opened_at`` carries no
    fill-in latch, so a non-live re-extraction can write the docketing date back
    and put the row in the docketing arm again. Successive dispatches converge it
    each time.
    """
    candidates, events_seen = arrival_candidates(conn)
    result = ArrivalBackfillResult(
        applied=apply, events_seen=events_seen, candidates=len(candidates), bound=max_fills
    )
    if not candidates:
        result.move_histogram = {label: 0 for label, _ in MOVE_BUCKETS}
        return result
    tally = _Tally()
    with prefetch_by_case(
        [candidate.case_id for candidate in candidates],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="arrival-backfill",
    ) as fetched:
        for candidate, (_, snapshot) in zip(candidates, fetched, strict=True):
            _read_candidate(candidate, snapshot, tally)

    counts, largest = _histogram(tally.filled)
    result.filled = tally.filled
    result.stamped = sum(1 for fill in tally.filled if fill.previous is None)
    result.moved = len(tally.filled) - result.stamped
    result.move_histogram = counts
    result.move_days_max = largest
    result.unchanged = tally.unchanged
    result.later_refused = tally.later_refused
    result.no_snapshot = tally.no_snapshot
    result.no_proceedings = tally.no_proceedings
    result.unparsed = tally.unparsed
    if apply and max_fills is not None and len(result.filled) > max_fills:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result
    corpus.stamp_event_opened_at(
        conn, [(fill.case_id, fill.event_id, fill.opened_at) for fill in result.filled]
    )
    return result


def _read_candidate(
    candidate: _Candidate,
    snapshot: tuple[date, dict[str, object]] | None,
    tally: _Tally,
) -> None:
    """Attribute one candidate to a fill, a refusal, or the reason there is neither.

    Every way the re-derivation can decline is a *reported reason* rather than a
    silent skip, because the reasons are not interchangeable: a row with no
    stored snapshot is an unreadable corpus, one whose proceedings are absent is
    an unobservable payload, and one the parser finds no submission entry in
    keeps the docketing fallback — which is late, the safe way to be wrong.
    """
    if snapshot is None:
        tally.no_snapshot += 1
        return
    _, payload = snapshot
    entries = proceedings_entries(payload)
    if not entries:
        # An absent or empty proceedings list makes the arrival unobservable from
        # this payload, not absent from the docket.
        tally.no_proceedings += 1
        return
    arrival = application_arrival_date(candidate.docket_number, entries)
    if arrival is None:
        tally.unparsed += 1
        return
    if arrival == candidate.opened_at:
        tally.unchanged += 1
        return
    if candidate.opened_at is not None and arrival > candidate.opened_at:
        tally.later_refused.append(candidate.case_id)
        return
    tally.filled.append(
        ArrivalFill(
            case_id=candidate.case_id,
            event_id=candidate.event_id,
            opened_at=arrival,
            previous=candidate.opened_at,
        )
    )
