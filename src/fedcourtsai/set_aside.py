"""The scored-figure set-aside: cells the record cannot show to be forward, by reason.

A membership rule beside the forward-claim rule, the leakage bit and the event
void (:mod:`fedcourtsai.integrity`, :mod:`fedcourtsai.voids`), and different
from all three in what it owes. Those drop a cell from every figure because the
cell is an observation of nothing; a set-aside cell may well be a genuine
forecast, but the record cannot show that it was made before its outcome was
public. So it leaves the **default** figures and is put back in a
**sensitivity** figure published beside each default it moved: both readings
are on the board, and the default is the one a headline quotes.

Each reason is one value of :data:`~fedcourtsai.schemas.SetAsideReason` and one
dated ``docs/freeze-record.md`` entry, because a reason moves a published
figure's population under unchanged digests (``docs/process-version.md``,
*membership rules*). Two kinds of reason exist, and they differ only in where
the fact comes from:

* **Computed** from the committed ledger alone, so every offline build decides
  it identically. :func:`interim_decision_day` is one.
* **Listed** in ``set_aside_events.json`` (:data:`SET_ASIDE_EVENTS`), for a
  reason only the corpus can decide — the post-conference reason reads the
  petition's docket entries. The list is a committed census, appended from the
  corpus by a reviewed edit, so the boards stay offline and deterministic.

**Adding a reason** is three edits here and one in the schema: a new
``SetAsideReason`` value, its predicate, a branch in :func:`set_aside_reason`
(or rows in the registry, for a listed reason), and its freeze-record entry.
Every board inherits it through :func:`fedcourtsai.store.stratify`, which
publishes it in the ``set_aside`` block and the sensitivity lines with no
further change. The grain is the scored cell. A reason that sets aside
individual **claims** inside a cell would add a claim-grain predicate here and
apply it where the claim totals are summed, keeping the same reason vocabulary
and the same block, and it owes two things the cell grain does not: its own
sensitivity line **per reason** — a claim total with that reason's claims
counted back, never stacked with another reason's or another departure's —
and counts in **claim units** (claims set aside, and the cells they sit in),
since a cell-grain count would misstate how much of a total moved.

One claim-grain reason is registered, ``increment-run-day``
(:func:`claim_set_aside_reason`), and it shares its timing reading with a
claim **mask** the scorer applies (:func:`increment_timing`). An increment
claim forecasts that a docket signal not yet on the cell's provisioned record
will arrive; a forward cell runs some time after its record was cut, and may
read the live docket, so the signal can already be there when it runs. Where
the record shows it was — the cell's pre-mint poll read it, or its docket date
is before the run day — the claim forecast nothing and the scorer masks it
(``ClaimScore.mask_reason``). Where the record cannot order the two — the
signal's date is the run day itself and no poll was taken — the claim may be a
forecast or may not, so it is set aside here, at the board, with its own
sensitivity line.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime
from importlib.resources import files
from types import MappingProxyType
from typing import Final, Literal
from zoneinfo import ZoneInfo

from .integrity import cell_clock
from .schemas import (
    DocketPollRecord,
    Outcome,
    PolledSignal,
    Prediction,
    SetAsideEvent,
    SetAsideEventsRegistry,
    SetAsideReason,
    Stage,
)

#: The Court's clock, which a disposition's ``resolved_at`` is dated in.
COURT_TIME: Final = ZoneInfo("America/New_York")

#: The listed set-aside events: a data file, so a listed set-aside is a reviewed
#: edit to one file; append-only, since a removed row would move a default figure
#: across a dated entry's boundary.
SET_ASIDE_EVENTS_RESOURCE = "set_aside_events.json"


def court_day(moment: datetime) -> date:
    """The Court-time (America/New_York) calendar day of an aware instant."""
    return moment.astimezone(COURT_TIME).date()


def load_set_aside_events(text: str | None = None) -> Mapping[tuple[str, str], SetAsideEvent]:
    """The listed set-aside events keyed ``(case_id, event_id)``; ``text`` overrides the file.

    Refuses an event listed twice: one key, one reason.
    """
    raw = (
        text
        if text is not None
        else files("fedcourtsai").joinpath(SET_ASIDE_EVENTS_RESOURCE).read_text(encoding="utf-8")
    )
    registry = SetAsideEventsRegistry.model_validate_json(raw)
    listed: dict[tuple[str, str], SetAsideEvent] = {}
    for event in registry.events:
        key = (event.case_id, event.event_id)
        if key in listed:
            raise ValueError(f"set_aside_events.json lists {key[0]} {key[1]} twice")
        listed[key] = event
    return MappingProxyType(listed)


#: The registry as loaded at import; :func:`set_aside_reason` reads it.
SET_ASIDE_EVENTS: Final[Mapping[tuple[str, str], SetAsideEvent]] = load_set_aside_events()


def interim_decision_day(
    prediction: Prediction,
    outcome: Outcome,
    stage: Stage | None,
    pre_mint_poll: Callable[[], str | None],
) -> bool:
    """Whether a forward interim cell ran on or after its decision day, unpolled.

    An application can be decided within hours, and ``resolved_at`` is a date
    with no time of day, so a forward interim cell whose harness clock
    (:func:`fedcourtsai.integrity.cell_clock`) falls, in Court time, on or after
    its outcome's ``resolved_at`` cannot be shown from its timestamps to have
    run before the decision was public. The one record that can show it is the
    harness's pre-mint docket poll: a ``pre_mint_poll`` reading ``open`` says
    the Court's docket JSON, as served just before the cell was minted, showed
    no decision. Any other reading — ``unavailable``, or no poll at all, which
    every cell written before the poll existed is — leaves the ordering
    unresolvable, and the cell is set aside.

    ``pre_mint_poll`` returns the scored prediction's ``usage.json``
    ``pre_mint_poll.state``, or ``None`` where either is absent; it is a thunk,
    asked only for a cell the timing test has already caught, so the ledger
    read is paid only there. A ``replay`` or context-null cell is never set
    aside here: it claims nothing about timing.
    """
    context = prediction.context
    if context is None or context.mode != "forward" or stage != Stage.interim:
        return False
    if court_day(cell_clock(prediction)) < outcome.resolved_at:
        return False
    return pre_mint_poll() != "open"


def set_aside_reason(
    case_id: str,
    event_id: str,
    prediction: Prediction,
    outcome: Outcome,
    stage: Stage | None,
    pre_mint_poll: Callable[[], str | None],
) -> SetAsideReason | None:
    """Why this scored cell is set aside from the default figures, or ``None``.

    The listed reasons are asked first, since they key on the event alone.
    """
    listed = SET_ASIDE_EVENTS.get((case_id, event_id))
    if listed is not None:
        return listed.reason
    if interim_decision_day(prediction, outcome, stage, pre_mint_poll):
        return "interim-decision-day"
    return None


#: How a forward cell's run sits against an increment claim's signal:
#: ``signal-before-run`` — the signal was on the docket before the cell ran, so
#: the claim forecast nothing; ``signal-on-run-day`` — the signal is dated the
#: cell's run day and no poll orders the two.
IncrementTiming = Literal["signal-before-run", "signal-on-run-day"]

#: The increment claims a run can overtake, each keyed to the
#: :class:`~fedcourtsai.schemas.PolledIncrementSignals` field its pre-mint poll
#: reads. String keys rather than the claim constants, which live in
#: :mod:`fedcourtsai.pipeline.claims` and import this module; a test pins the two.
TIMED_INCREMENT_CLAIMS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "response-requested-increment": "response_requested",
        "referral-increment": "referred_to_court",
        "cvsg-increment": "cvsg",
    }
)


def polled_signal(poll: DocketPollRecord | None, claim_id: str) -> PolledSignal | None:
    """What a usable pre-mint poll read of ``claim_id``'s signal, or ``None``.

    Usable means the poll read ``open`` and recorded that signal: an
    ``unavailable`` poll read nothing, and a poll taken before the signal
    reading existed, or of a docket whose form cannot carry the signal, records
    none.
    """
    if poll is None or poll.state != "open" or poll.signals is None:
        return None
    field = TIMED_INCREMENT_CLAIMS.get(claim_id)
    if field is None:
        return None
    seen: PolledSignal | None = getattr(poll.signals, field)
    return seen


def increment_timing(
    claim_id: str,
    prediction: Prediction,
    poll: DocketPollRecord | None,
    signal_day: Callable[[], date | None],
) -> IncrementTiming | None:
    """Whether a forward cell ran after its increment claim's signal was on the docket.

    Asked of the three increment claims in :data:`TIMED_INCREMENT_CLAIMS`, on a
    ``forward`` cell only: a ``replay`` cell runs long after its cut by design
    and its contract bars it from reading past the event, and a context-null
    cell claims nothing about timing.

    **With a usable pre-mint poll** (:func:`polled_signal`) the poll decides:
    the signal read present means it was on the served docket just before the
    cell was minted (``signal-before-run``); read absent, it postdates the poll
    and the claim is a forecast (``None``), whatever day it later landed.

    **Without one**, the signal's docket date decides against the cell's run
    day — its harness clock (:func:`fedcourtsai.integrity.cell_clock`) in Court
    time (:func:`court_day`), the reading the interim decision-day rule takes:
    strictly before is ``signal-before-run``; the same day is
    ``signal-on-run-day``, which nothing in the record can order; later is
    ``None``. ``signal_day`` is a thunk returning that date, asked only here,
    so a caller pays its ledger read only for an unpolled forward cell. Where
    it returns ``None`` — no signal, or no committed date for it (a referral
    has none) — the timing is unassessable and the answer is ``None``: the
    claim keeps the resolution its record gives it.
    """
    context = prediction.context
    if claim_id not in TIMED_INCREMENT_CLAIMS or context is None or context.mode != "forward":
        return None
    seen = polled_signal(poll, claim_id)
    if seen is not None:
        return "signal-before-run" if seen.present else None
    day = signal_day()
    if day is None:
        return None
    run_day = court_day(cell_clock(prediction))
    if day == run_day:
        return "signal-on-run-day"
    return "signal-before-run" if day < run_day else None


def claim_set_aside_reason(
    claim_id: str,
    resolved: int | None,
    prediction: Prediction,
    poll: DocketPollRecord | None,
    signal_day: Callable[[], date | None],
) -> SetAsideReason | None:
    """Why one resolved claim is set aside from the default claim figures, or ``None``.

    The claim-grain predicate: ``increment-run-day`` for an increment claim
    whose signal is dated its unpolled forward cell's run day
    (:func:`increment_timing` reads ``signal-on-run-day``). A claim the record
    leaves unresolved (``resolved`` is ``None``, the run-timing mask included)
    moves no figure and is never set aside. A block stamped before the
    run-timing mask existed can carry a resolved claim the mask would now
    reach (``signal-before-run``); it is left as stamped, not set aside, since
    a set-aside brackets an ordering the record cannot settle and that one it
    can — the stamp's re-run (``stamp-cell --regrade``) is what applies the mask.
    """
    if resolved is None:
        return None
    if increment_timing(claim_id, prediction, poll, signal_day) == "signal-on-run-day":
        return "increment-run-day"
    return None
