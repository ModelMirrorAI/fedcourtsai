"""The dockets the Court's recent order documents name, for the live poll's queue.

An order changes a docket the day it issues, but the live rotation reaches a
docket on its own clock: a petition distributed for a conference leads until
its order list is read, and every other docket waits for its staleness turn,
which can be days. A petition denied in a miscellaneous order beside its stay
application, a granted case named among the orders in pending cases and an
application ruled on in an order list are all of the second kind. This module
reads which dockets the documents of the last few days name, so the cycle can
poll those ahead of the rotation
(:func:`fedcourtsai.pipeline.live.live_poll_all`).

Only the docket numbers and each document's listed day are taken. What an
order says is not read here: the poll that follows reads the docket itself,
and the disposition is recorded from the docket's own entries, as on every
other poll. A document that cannot be fetched or extracted is counted and
skipped; the dockets it names keep their ordinary place in the rotation.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta

from .order_lineups import OrderFetcher
from .order_reconcile import document_entries, refs_in_window

#: The most documents one cycle reads, newest first. A window of a few days
#: lists fewer; the bound keeps a listing that grew unexpectedly from spending
#: the cycle's poll budget on downloads.
MAX_DOCUMENTS = 12

# The two number forms the live channel follows: a petition (``26-6187``) and
# an application (``26A716``). A motion or an original number names no row.
_FOLLOWED_DOCKET_RE = re.compile(r"^(?:\d{2}-\d{1,5}|\d{2}A\d{1,5})$")


@dataclass
class OrderNamed:
    """What the order documents of one window name.

    ``days`` maps each docket number to the latest listed day of a document
    naming it. ``documents`` counts the documents the Court lists in the
    window, ``unread`` those among them that gave no text (a failed fetch, a
    PDF with no text, a text the reader raised on) or were not reached before
    the deadline or inside :data:`MAX_DOCUMENTS`.
    """

    days: dict[str, date] = field(default_factory=dict)
    documents: int = 0
    unread: int = 0


def read_order_named(
    fetcher: OrderFetcher,
    *,
    today: date,
    lookback_days: int,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> OrderNamed:
    """Every followed docket the documents listed from ``lookback_days`` ago through ``today`` name.

    Newest document first, so a cycle short on time reads the day's orders
    before an earlier day's. Raises ``httpx.HTTPError`` when a listing page is
    not served; the caller isolates it. A text cut at the extraction cap still
    contributes the dockets it holds: a partial list of names is safe here,
    where it would not be for a check that must account for every entry.
    """
    refs = refs_in_window(fetcher, today - timedelta(days=lookback_days), today)
    named = OrderNamed(documents=len(refs))
    for index, ref in enumerate(sorted(refs, key=lambda r: (r.day, r.url), reverse=True)):
        if index >= MAX_DOCUMENTS or (deadline is not None and time_fn() >= deadline):
            named.unread += len(refs) - index
            break
        # One document the extractor or the reader raises on is that document's
        # loss alone: the same documents are read every cycle of the window, so
        # letting it end the read would cost every cycle the ordering.
        try:
            document = fetcher.document(ref.url, ref)
            entries = document_entries(document.text)[0] if document.text is not None else None
        except Exception:
            entries = None
        if entries is None:
            named.unread += 1
            continue
        for entry in entries:
            if _FOLLOWED_DOCKET_RE.match(entry.docket) is None:
                continue
            held = named.days.get(entry.docket)
            if held is None or ref.day > held:
                named.days[entry.docket] = ref.day
    return named
