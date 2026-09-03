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
Resolution status therefore decides which reading a row carries, and any
retrospective interim population drawn from these events inherits that
conditioning — which is exactly the kind of rule a cohort must not be built on.
A forward cell is unaffected *once its row has been re-polled* — **not** by
construction: a queued row not polled since the arrival read shipped still
carries the docketing stamp and is moved by an apply, so the boundary runs
through the forward stratum too, and closing that gap is part of what this pass
is for.

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
- **What the ledger has to state, and in what terms.** How many rows changed
  stamp and by how much — a histogram of the day deltas — but that is the
  *window*, not what was in it. A one-day move on a docket disposed of that day
  admits the outcome; a month-long move over a quiet docket admits nothing. So
  the day histogram is reported as an upper bound and the **entries the
  pre-repair cut admitted** are reported beside it, with the two readings that
  decide the question named rather than counted: whether the row's own
  disposition fell inside that band, and whether the Court's response request
  did.
- **What it can and cannot claim to have removed.** It removes the correlation
  on the slice carrying a readable live-shaped snapshot with a parseable
  arrival. Every other arm — no snapshot, no proceedings, no dated submission
  entry, a refused later reading — keeps the pre-repair stamp, and that is a
  still-conditioned row rather than a safe fallback: late is the safe direction
  for *leakage*, but it is the defect itself for *conditioning*. Whether the
  residue is itself resolution-skewed is the question, and it has a structural
  reason to be — a stored live snapshot exists because a channel polled the
  case, and the poller serves the unresolved slice — so the ledger splits the
  class, the repairs and the residue by resolution and lets the reader see it.

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
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import EventKind
from .cert_signals import entry_date, proceedings_entries
from .interim_signals import application_arrival_date, response_requested_date
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

    over_admitted: int = Field(
        ge=0,
        default=0,
        description="Docket entries that a cell provisioned **today**, under the "
        "pre-repair stamp and over the corpus at `corpus_vintage`, would admit and "
        "the repaired stamp does not. A bound on the rule's forward exposure, not a "
        "measurement of what any committed cell saw: it is read off the newest "
        "stored snapshot with no date bound, so it *over*-counts against a cell "
        "provisioned when that docket was shorter, and *under*-counts wherever the "
        "stored snapshot itself predates filings the docket has since gained. It is "
        "the reading that bears on leakage where the day delta does not — a one-day "
        "move on a same-day disposition admits the outcome, a month-long move over a "
        "quiet docket admits nothing. On a row that carried no stamp the pre-repair "
        "cut was no cut at all, so this counts the whole tail rather than a window",
    )
    admitted_the_disposition: bool = Field(
        default=False,
        description="Whether this row's own disposition date is inside that band — "
        "i.e. whether a cell provisioned today under the pre-repair stamp would read "
        "the outcome it was forecasting. The sharpest reading in this ledger, and a "
        "counterfactual on the same terms as `over_admitted`: it says what the rule "
        "still exposes, not what a committed cell was shown",
    )
    admitted_the_response_request: bool = Field(
        default=False,
        description="The same counterfactual for the Court's request for a response "
        "— an escalation signal the arrival moment had not yet seen",
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
        description="Live-slice SCOTUS interim baseline events the walk read at "
        "all, entry-pinned rows included. The **wrong-blob** denominator and only "
        "that: zero means the population could not be read rather than that the "
        "class is empty, so the caller refuses on it. Deliberately looser than the "
        "class, so `candidates / events_seen` is not a prevalence — "
        "`baseline_candidates_seen` is the matched denominator",
    )
    baseline_candidates_seen: int = Field(
        ge=0,
        default=0,
        description="The **matched** denominator: live-slice SCOTUS interim "
        "baseline events with `docket_entry_id IS NULL`, which is every row the "
        "predicate could have selected. `candidates / baseline_candidates_seen` is "
        "the defect's prevalence in the reachable population; the ratio against "
        "`events_seen` is not, since that count includes entry-pinned rows this "
        "route never acts on",
    )
    events_all_slices: int = Field(
        ge=0,
        default=0,
        description="Baseline interim events with `docket_entry_id IS NULL` across "
        "the whole blob, live slice or not. The count that makes the **unreachable** "
        "arm visible: this pass needs a stored live-shaped snapshot, so a row "
        "outside the live slice is never even a candidate, and its defective stamp "
        "survives every dispatch. The gap between this and "
        "`baseline_candidates_seen` is the part of the population no run of this "
        "pass can reach",
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
    over_admitted_rows: int = Field(
        ge=0,
        default=0,
        description="Of `filled`, the rows where a cell provisioned today under the "
        "pre-repair stamp would admit at least one docket entry the repaired stamp "
        "does not. The day histogram bounds the *window*; this counts what is in it, "
        "which is the reading that bears on leakage — a day delta over a quiet "
        "docket admits nothing. A forward-exposure bound, not a cell measurement: "
        "see `over_admitted` on `ArrivalFill` for which way it errs",
    )
    over_admitted_entries: int = Field(
        ge=0,
        default=0,
        description="Those entries, summed across `filled`",
    )
    admitted_the_disposition: list[str] = Field(
        default_factory=list,
        description="The cases where a cell provisioned today under the pre-repair "
        "stamp would read the case's own disposition, in class order. The sharpest "
        "reading this ledger carries — but a **counterfactual over the corpus at "
        "`corpus_vintage`**, not a claim about any cell that ran: it says what the "
        "rule still exposes. Named rather than counted, because these are the cases "
        "a cohort has to be checked against; `admitted_the_disposition_committed` is "
        "the subset that actually carries committed predict output",
    )
    admitted_the_disposition_committed: list[str] = Field(
        default_factory=list,
        description="Of `admitted_the_disposition`, the cases carrying committed "
        "predict output on this event — the cut that turns a forward-exposure bound "
        "into a list of gradings a reader can go and check. Still not proof the "
        "cell saw the disposition (its own provisioning read a shorter docket), but "
        "it is the population where that question is worth asking one case at a "
        "time. Empty where no data root was supplied",
    )
    admitted_the_response_request: int = Field(
        ge=0,
        default=0,
        description="The same counterfactual for the response request — an "
        "escalation signal the arrival moment had not yet seen, and the other "
        "reading the registered boundary measurement took",
    )
    residue_admits_disposition: list[str] = Field(
        default_factory=list,
        description="The **unrepaired** cases whose *surviving* stamp still admits "
        "their own disposition, in class order. The measurement the repaired rows' "
        "readings above cannot give: conditioning persists exactly where the stamp "
        "did not move, so a boundary claim scoped to `filled` describes the half of "
        "the class that was fixed and says nothing about the half that was not. "
        "Answerable without an arrival — the stored stamp and `date_decided` decide "
        "it — so every residue arm is covered, `no_snapshot` included",
    )
    corpus_vintage: date | None = Field(
        default=None,
        description="The newest `last_pulled` stamp across the blob this ran "
        "against (what `fedcourts corpus-info` prints). Every exposure reading "
        "above is a counterfactual over the corpus as of this date, so a ledger "
        "quoted without it states a bound whose basis is unrecoverable",
    )
    candidates_resolved: int = Field(
        ge=0,
        default=0,
        description="Of `candidates`, the resolved (decided) rows. Resolution is "
        "the axis the defect runs along — the poller re-polls only unresolved rows "
        "— so the class is expected to be overwhelmingly resolved, and a split that "
        "is not says the defect has a second source",
    )
    filled_resolved: int = Field(
        ge=0,
        default=0,
        description="Of `filled`, the resolved rows",
    )
    unrepaired: int = Field(
        ge=0,
        default=0,
        description="Candidates this pass could not repair — every residue arm "
        "together, `unchanged` excluded, since that arm is already correct. These "
        "keep the pre-repair stamp, so they are the still-conditioned remainder "
        "rather than a safe fallback",
    )
    unrepaired_resolved: int = Field(
        ge=0,
        default=0,
        description="Of `unrepaired`, the resolved rows — the number that says "
        "whether this pass removed the outcome correlation or only shrank it. A "
        "residue that is entirely decided rows is a correlation the repair did not "
        "reach; one that splits like the class did is a residue the correlation "
        "does not run through",
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
        description="The blast-radius bound this run carried, counted against the "
        "rows actually written rather than the `candidates` denominator beside "
        "them. Reported in both modes and *checked* only on an apply, since a dry "
        "run writes nothing there is anything to refuse",
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
    #: Whether the event is closed. Carried because resolution is the axis the
    #: defect runs along, so the ledger has to be able to split on it: a residue
    #: that is all decided rows is a correlation shrunk, not one removed.
    resolved: bool
    #: The row's own disposition date, for the sharpest reading of what the old
    #: cut admitted — whether the outcome itself was inside the window.
    date_decided: date | None


@dataclass
class _Tally:
    """What the walk has recorded so far, accumulated across its candidates."""

    filled: list[ArrivalFill] = field(default_factory=list)
    later_refused: list[str] = field(default_factory=list)
    no_snapshot: int = 0
    no_proceedings: int = 0
    unparsed: int = 0
    unchanged: int = 0
    #: Of the candidates this pass could not repair, how many were resolved —
    #: accumulated as they are attributed, so no arm can be added to without the
    #: split following it.
    unrepaired: int = 0
    unrepaired_resolved: int = 0
    filled_resolved: int = 0
    residue_admits_disposition: list[str] = field(default_factory=list)

    def record_unrepairable(self, candidate: _Candidate) -> None:
        """Record a candidate that keeps its pre-repair stamp.

        Also asks the residue-side question the repaired rows' readings cannot:
        does the stamp this row *keeps* still admit its own disposition? It
        needs no arrival — the stored stamp and ``date_decided`` decide it — so
        every arm is covered, including the rows whose snapshot could not be
        read at all. This is where conditioning persists, so a boundary claim
        that omits it describes only the half of the class that was fixed.
        """
        self.unrepaired += 1
        self.unrepaired_resolved += int(candidate.resolved)
        if _admits(candidate.date_decided, stamp=candidate.opened_at):
            self.residue_admits_disposition.append(candidate.case_id)


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


@dataclass(frozen=True)
class ArrivalScan:
    """The class this route can act on, and the three denominators around it."""

    candidates: tuple[_Candidate, ...]
    #: Live-slice baseline interim events, entry-pinned rows included. The
    #: wrong-blob denominator the caller refuses on, and nothing else.
    events_seen: int
    #: Live-slice baseline interim events the predicate could have selected —
    #: the matched denominator, so a prevalence can be stated.
    baseline_candidates_seen: int
    #: The same, blind to the live slice: what the population would be if this
    #: route could reach every row. The gap is the arm no dispatch reaches.
    events_all_slices: int


def arrival_candidates(conn: sqlite3.Connection) -> ArrivalScan:
    """The interim baseline events showing the stamp defect, and its denominators.

    Two arms in one predicate, because the defect has two shapes and they are the
    same defect: a row that never got an arrival read carries the docketing date
    where one is stored and nothing where it is not. Joined to ``cases`` because
    the docketing date and the docket number both live there, and a row whose
    case is absent is out of scope rather than acted on — neither the fallback it
    is being compared against nor the number the parser anchors on can be read
    for it.

    **Three denominators, because one number cannot answer three questions.**
    ``events_seen`` is deliberately loose — every live-slice baseline interim
    event, entry-pinned rows included — and exists only to tell a converged
    corpus from one this process cannot read at all.
    ``baseline_candidates_seen`` is matched to the predicate, so
    ``candidates / baseline_candidates_seen`` is the defect's prevalence in the
    reachable population, which the loose count's ratio is not.
    ``events_all_slices`` drops the live-slice limb: this pass needs a stored
    live-shaped snapshot, so a row outside that slice is never a candidate and
    its defective stamp survives every dispatch — the gap between the two is the
    arm no run of this pass reaches, and it is invisible without the count.
    """

    def _count(where: str) -> int:
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM events e JOIN cases c ON c.case_id = e.case_id "
                f"WHERE e.event_id = ? AND e.court = 'scotus' AND {where}",
                (MOTION_BASELINE_EVENT_ID,),
            ).fetchone()[0]
        )

    live = corpus.live_slice_sql("c")
    # An entry-pinned motion event names one specific filing rather than the
    # docket's arrival, so the arrival derivation is the wrong reading for it.
    baseline = "e.docket_entry_id IS NULL"
    rows = conn.execute(
        "SELECT e.case_id AS case_id, e.event_id AS event_id, e.opened_at AS opened_at, "
        "e.resolved AS resolved, c.docket_number AS docket_number, "
        "c.date_decided AS date_decided "
        "FROM events e JOIN cases c ON c.case_id = e.case_id "
        f"WHERE e.event_id = ? AND e.court = 'scotus' AND {live} AND {baseline} "
        "AND (e.opened_at IS NULL OR e.opened_at = c.date_filed) "
        "ORDER BY e.case_id, e.event_id",
        (MOTION_BASELINE_EVENT_ID,),
    ).fetchall()
    return ArrivalScan(
        candidates=tuple(
            _Candidate(
                case_id=str(record["case_id"]),
                event_id=str(record["event_id"]),
                docket_number=str(record["docket_number"] or ""),
                opened_at=_stored_date(record, "opened_at"),
                resolved=bool(record["resolved"]),
                date_decided=_stored_date(record, "date_decided"),
            )
            for record in rows
        ),
        events_seen=_count(live),
        baseline_candidates_seen=_count(f"{live} AND {baseline}"),
        events_all_slices=_count(baseline),
    )


def backfill_arrival_stamps(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_fills: int | None = None,
    data_root: Path | None = None,
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

    ``data_root`` enables the committed-cell cut: the exposure readings below are
    counterfactuals over the corpus as it stands, and intersecting them with the
    events that actually carry committed predict output is what turns a bound
    into a list of gradings a reader can check. Omitted, that field stays empty
    and the rest of the ledger is unchanged.
    """
    scan = arrival_candidates(conn)
    candidates = scan.candidates
    result = ArrivalBackfillResult(
        applied=apply,
        events_seen=scan.events_seen,
        baseline_candidates_seen=scan.baseline_candidates_seen,
        events_all_slices=scan.events_all_slices,
        candidates=len(candidates),
        bound=max_fills,
        # Every exposure reading below is a counterfactual over the corpus as of
        # this date, so the date travels with them rather than being recoverable
        # only from whatever the operator happened to note.
        corpus_vintage=corpus.latest_pull_date(conn),
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
    # What the pre-repair cut actually admitted, beside the window it spanned.
    result.over_admitted_rows = sum(1 for fill in tally.filled if fill.over_admitted)
    result.over_admitted_entries = sum(fill.over_admitted for fill in tally.filled)
    result.admitted_the_disposition = [
        fill.case_id for fill in tally.filled if fill.admitted_the_disposition
    ]
    result.admitted_the_disposition_committed = _with_committed_predictions(
        data_root, result.admitted_the_disposition
    )
    result.admitted_the_response_request = sum(
        1 for fill in tally.filled if fill.admitted_the_response_request
    )
    # The resolution split, which is what says whether the correlation was
    # removed or only shrunk.
    result.candidates_resolved = sum(1 for candidate in candidates if candidate.resolved)
    result.filled_resolved = tally.filled_resolved
    result.unrepaired = tally.unrepaired
    result.unrepaired_resolved = tally.unrepaired_resolved
    result.residue_admits_disposition = tally.residue_admits_disposition
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


def _with_committed_predictions(data_root: Path | None, case_ids: list[str]) -> list[str]:
    """Of ``case_ids``, those whose interim baseline event carries committed predict output.

    Read off the committed tree rather than the corpus, because that is where the
    question lives: a case in this list has a grading someone can open and check
    against the exposure the ledger reports. A malformed ``case_id`` is skipped
    rather than raised on — this is a reporting cut, and it must not be able to
    fail a pass whose write already landed.
    """
    if data_root is None:
        return []
    found: list[str] = []
    for case in case_ids:
        court, _, docket = case.partition("/")
        if not docket.isdigit():
            continue
        predictions = (
            CasePaths(data_root, court, int(docket)).event(MOTION_BASELINE_EVENT_ID).predictions_dir
        )
        if predictions.is_dir() and any(predictions.iterdir()):
            found.append(case)
    return found


def _admits(when: date | None, *, stamp: date | None) -> bool:
    """Whether a cut taken at ``stamp`` would show a docket entry dated ``when``.

    The cut keeps everything dated on or before the stamp, and a ``None`` stamp
    is no cut at all — `moment_cutoff` returns nothing for it, so the cell reads
    the latest snapshot and every date is admitted.
    """
    return when is not None and (stamp is None or when <= stamp)


def _inside(when: date | None, *, arrival: date, previous: date | None) -> bool:
    """Whether ``when`` is a day the pre-repair cut admitted and the repair does not.

    The cut keeps everything dated on or before the stamp, so the band the repair
    closes is ``(arrival, previous]``. ``previous`` of ``None`` is the unstamped
    arm, where the pre-repair cut was **no cut at all** — so the band is open to
    the right and every day after the arrival was admitted.
    """
    if when is None or when <= arrival:
        return False
    return previous is None or when <= previous


def _over_admitted(
    entries: list[tuple[str, str | None]], *, arrival: date, previous: date | None
) -> list[date]:
    """The dated docket entries the pre-repair cut admitted and the repair does not.

    The reading that bears on leakage, which the day delta only bounds: a
    one-day move on a docket disposed of that day admits the outcome, and a
    month-long move over a quiet docket admits nothing. Undated entries are not
    counted — the same strictness the cut itself applies, since a partial date
    cannot decide which side of a boundary an entry is on.
    """
    return [
        when
        for _, raw in entries
        if (when := entry_date(raw)) is not None
        and _inside(when, arrival=arrival, previous=previous)
    ]


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
        tally.record_unrepairable(candidate)
        return
    _, payload = snapshot
    entries = proceedings_entries(payload)
    if not entries:
        # An absent or empty proceedings list makes the arrival unobservable from
        # this payload, not absent from the docket.
        tally.no_proceedings += 1
        tally.record_unrepairable(candidate)
        return
    arrival = application_arrival_date(candidate.docket_number, entries)
    if arrival is None:
        tally.unparsed += 1
        tally.record_unrepairable(candidate)
        return
    if arrival == candidate.opened_at:
        tally.unchanged += 1
        return
    if candidate.opened_at is not None and arrival > candidate.opened_at:
        tally.later_refused.append(candidate.case_id)
        tally.record_unrepairable(candidate)
        return
    # The direction guard is skipped on the null arm above, and the asymmetry is
    # safe rather than an oversight: a row carrying no stamp takes *no cut at
    # all*, so any date is a tightening and there is no enlarging direction to
    # refuse. What it gains is a window, not a shorter one.
    admitted = _over_admitted(entries, arrival=arrival, previous=candidate.opened_at)
    tally.filled.append(
        ArrivalFill(
            case_id=candidate.case_id,
            event_id=candidate.event_id,
            opened_at=arrival,
            previous=candidate.opened_at,
            over_admitted=len(admitted),
            admitted_the_disposition=_inside(
                candidate.date_decided, arrival=arrival, previous=candidate.opened_at
            ),
            admitted_the_response_request=_inside(
                response_requested_date(entries), arrival=arrival, previous=candidate.opened_at
            ),
        )
    )
    tally.filled_resolved += int(candidate.resolved)
