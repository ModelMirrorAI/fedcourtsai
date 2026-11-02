"""Reading a docket's entries in part: the pieces ``pull`` and ``watchlist-refresh`` share.

Both keep a stored docket current by asking upstream only for the entries
modified since the stored copy (``date_modified__gte``, less an overlap) and
laying them over it by id, with a whole re-read on a day the docket's id picks.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from typing import Any, Final

#: Entries upstream serves on one page of ``docket-entries/``.
ENTRIES_PER_PAGE: Final = 20


def full_read_due(docket_id: int, today: date, every_days: int) -> bool:
    """Whether ``today`` is the docket's day for a whole re-read.

    The docket id picks the day, so the period's full reads spread across its
    days rather than all falling on one.
    """
    return (docket_id + today.toordinal()) % every_days == 0


def full_read_owed(docket_id: int, last_read: date, today: date, every_days: int) -> bool:
    """Whether this read of the docket should be whole rather than incremental.

    For a reader that does not reach every docket every day (the pull rotation).
    Within a period of the last read, the read is whole when the docket's
    whole-read day fell after ``last_read`` and by ``today``: asking only
    whether today is the day would skip it whenever the rotation lands
    elsewhere, and for ever if its cycle is a multiple of the period. A second
    read on the same day owes nothing.

    A period or more after the last read, every read would be whole under that
    rule, and a rotation whose cycle runs a period or longer would never read
    incrementally. So such a read is whole one time in ``every_days``, drawn
    from a hash of the docket, the last read's date and today's: each read draws
    afresh, even when the last read's date does not move, so no cycle length can
    keep a docket from its whole read. The spacing of whole reads is then
    about ``every_days`` refreshes, not days, and has no upper bound: the
    chance a docket goes ``n`` such refreshes without one is
    ``(1 - 1/every_days) ** n``.
    """
    gap = (today - last_read).days
    if gap >= every_days:
        draw = hashlib.sha256(
            f"{docket_id}:{last_read.isoformat()}:{today.isoformat()}".encode()
        ).digest()
        return int.from_bytes(draw[:8], "big") % every_days == 0
    return any(
        full_read_due(docket_id, last_read + timedelta(days=step), every_days)
        for step in range(1, gap + 1)
    )


def merge_entries(
    stored: Iterable[Mapping[str, Any]], changed: Iterable[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """The stored entries with the changed ones laid over them by id, newest id first."""
    by_id: dict[int, dict[str, Any]] = {int(e["id"]): dict(e) for e in stored}
    by_id.update({int(e["id"]): dict(e) for e in changed})
    return [by_id[key] for key in sorted(by_id, reverse=True)]
