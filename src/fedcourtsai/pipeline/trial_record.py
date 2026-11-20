"""What a trial-stage cell is told about its own event, beside the docket.

A district cell's snapshot is the whole docket: hundreds of entries, of which
the event is about one motion. :func:`build` states, from that same snapshot
and the watchlist, what the cell would otherwise have to find for itself:

* **the judge** the docket names as assigned, and the magistrate judge it
  names as referred to, as the snapshot's own header fields give them;
* **the motion's briefing**, as the opener reads it
  (:func:`.trial_opener.read_docket`): the entry that filed the motion, the
  opposition and the reply it took as closing the briefing, and what the
  event's opening day was read from. Entry numbers and filing dates only: the
  entries' text is in the snapshot, and no filing's own text is staged;
* **the listed case's other dockets**, by identifier and relation
  (``config/ai-watchlist.yaml``): the appeal, the docket transferred from, the
  panel's docket, the member and companion dockets. None of their snapshots
  is staged.

The judge and the briefing are derived from the cell's own placed snapshot.
The related dockets come from the watchlist as committed, which carries no
dates, so the record is a forward cell's: the caller builds none for a replay
cell, whose cutoff a listed appeal could postdate. The judgment event names no
motion and carries no briefing.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

from .. import ids
from ..ai_watchlist import AiWatchlist, WatchlistCase
from ..schemas import TrialBriefingEntry, TrialMotionBriefing, TrialRecord, TrialRelatedDocket
from . import moments, trial_opener
from .trial_resolver import Citation

#: The relation stated for the listed case's own docket, on a cell placed on
#: one of its other dockets.
LISTED_RELATION = "listed"


def _named(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value.strip() or None if isinstance(value, str) else None


def _entry(cited: Citation | None) -> TrialBriefingEntry | None:
    if cited is None:
        return None
    return TrialBriefingEntry(entry_number=cited.entry_number, date_filed=cited.date_filed)


def _briefing(
    event_id: str,
    payload: Mapping[str, Any],
    *,
    read_on: date,
    local_rule: trial_opener.LocalRule | trial_opener.DistrictRule | None,
) -> TrialMotionBriefing | None:
    number = moments.trial_entry_number(event_id)
    if number is None:
        return None
    entries = [e for e in payload.get("docket_entries") or [] if isinstance(e, Mapping)]
    openings, _ = trial_opener.read_docket(entries, today=read_on, local_rule=local_rule)
    for opening in openings:
        if opening.event.entry_number != number:
            continue
        motion = _entry(opening.filed)
        assert motion is not None
        return TrialMotionBriefing(
            motion=motion,
            opposition=_entry(opening.opposition),
            reply=_entry(opening.reply),
            opened_on=opening.opens_on,
            opening_basis=None if opening.basis is None else opening.basis.value,
        )
    return None


def _listed(case_id: str, watchlist: AiWatchlist | None) -> WatchlistCase | None:
    if watchlist is None:
        return None
    for case in watchlist.cases:
        if any(ids.case_id(court, docket) == case_id for court, docket in case.dockets()):
            return case
    return None


def _others(case_id: str, listed: WatchlistCase) -> list[TrialRelatedDocket]:
    rows = [
        TrialRelatedDocket(
            case_id=ids.case_id(listed.court, listed.docket_id),
            court=listed.court,
            docket_number=listed.docket_number,
            relation=LISTED_RELATION,
        ),
        *(
            TrialRelatedDocket(
                case_id=ids.case_id(related.court, related.docket_id),
                court=related.court,
                docket_number=related.docket_number,
                relation=related.relation.value,
            )
            for related in listed.related
        ),
    ]
    return [row for row in rows if row.case_id != case_id]


def build(
    case_id: str,
    event_id: str,
    payload: Mapping[str, Any],
    watchlist: AiWatchlist | None,
    *,
    read_on: date,
    local_rule: trial_opener.LocalRule | trial_opener.DistrictRule | None = None,
) -> TrialRecord | None:
    """The trial record of the cell placed on ``payload`` for ``event_id``.

    ``None`` for an event of any other stage. ``payload`` is the snapshot the
    cell is given, and ``read_on`` the day its docket is read as of: the
    opener counts a deadline as passed only before that day. ``briefing`` is
    null for the judgment event, and for a motion the opener does not read on
    this snapshot; ``listed_case`` is null, and ``related_dockets`` empty,
    where the watchlist names the docket nowhere.
    """
    spec = moments.trial_spec_for(event_id)
    if spec is None:
        return None
    listed = _listed(case_id, watchlist)
    return TrialRecord(
        case_id=case_id,
        event_id=event_id,
        moment=spec.moment.value,
        assigned_judge=_named(payload, "assigned_to_str"),
        referred_judge=_named(payload, "referred_to_str"),
        briefing=_briefing(event_id, payload, read_on=read_on, local_rule=local_rule),
        listed_case=None if listed is None else listed.name,
        related_dockets=[] if listed is None else _others(case_id, listed),
    )
