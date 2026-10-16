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
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime
from importlib.resources import files
from types import MappingProxyType
from typing import Final
from zoneinfo import ZoneInfo

from .integrity import cell_clock
from .schemas import (
    Outcome,
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
