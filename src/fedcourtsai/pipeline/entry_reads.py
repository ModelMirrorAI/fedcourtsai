"""Reading a docket's entries in part: the pieces ``pull`` and ``watchlist-refresh`` share.

Both keep a stored docket current by asking upstream only for the entries
modified since the stored copy (``date_modified__gte``, less an overlap) and
laying them over it by id, with a whole re-read on a day the docket's id picks.
"""

from __future__ import annotations

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
    """Whether the docket's whole-read day fell after ``last_read`` and by ``today``.

    For a reader that does not reach every docket every day (the pull rotation):
    asking only whether today is the day would skip the whole read whenever the
    rotation lands elsewhere, and for ever if its cycle is a multiple of the
    period. A second read on the same day owes nothing.
    """
    gap = (today - last_read).days
    if gap >= every_days:
        return True
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
