"""The pre-mint docket poll: is a forward cell's event still open right now?

A forward cell is provisioned from the corpus's latest stored snapshot, and that
snapshot can be days behind the docket: the live rotation re-polls a pending
application or petition on its own cadence, not at the moment a predict round
mints. An interim application in particular can be decided within hours of a
response or a reply, and an order list issues every disposition of the day at
once, so a cell minted from a snapshot that predates the order can run after
the order is public. The disposition's date carries no time of day, so nothing
after the fact can say which came first.

This module answers the question at the one moment it can be answered: just
before the cell's record is written, it fetches the docket's current JSON from
the Court and runs the same outcome scan the forward gate runs on the stored
snapshot (:func:`fedcourtsai.pipeline.outcome.forward_leakage`). A disposed
event refuses the cell; an open one is recorded with the poll's UTC time, so
the cell's own record shows it began against an open docket. The fresh payload
is read and discarded: it is evidence for the gate, never the cell's input,
which stays the stored snapshot the rest of provisioning placed.

The poll is best-effort by design. A docket the Court does not serve, a number
that does not parse, or an upstream failure records ``unavailable`` and lets the
cell proceed on the stored-snapshot gates alone, exactly as it did before the
poll existed: a forward cell must not be lost to an upstream hiccup, and the
record says the poll did not establish the ordering.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

import httpx

from ..supremecourt import (
    OffHostFetch,
    parse_scotus_application_number,
    parse_scotus_docket_number,
)
from .outcome import forward_leakage

PollState = Literal["open", "decided", "unavailable"]


class DocketFetcher(Protocol):
    """The one call the poll makes: :meth:`SupremeCourtClient.get_docket`."""

    def get_docket(
        self, term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
    ) -> dict[str, Any] | None: ...


@dataclass(frozen=True)
class PreMintPoll:
    """What the docket showed when polled just before a forward cell was minted."""

    polled_at: datetime
    state: PollState
    reason: str | None = None

    def as_record(self) -> dict[str, str | None]:
        """The JSON shape the usage record carries."""
        return {
            "polled_at": self.polled_at.isoformat().replace("+00:00", "Z"),
            "state": self.state,
            "reason": self.reason,
        }


def docket_coordinates(
    docket_number: str,
) -> tuple[int, int, Literal["cert", "application"]] | None:
    """``(term, serial, form)`` for a Term-form or application docket number, or ``None``."""
    application = parse_scotus_application_number(docket_number)
    if application is not None:
        return application[0], application[1], "application"
    cert = parse_scotus_docket_number(docket_number)
    if cert is not None:
        return cert[0], cert[1], "cert"
    return None


def poll_before_mint(
    court: str,
    docket_number: str,
    event_id: str,
    fetcher: DocketFetcher,
    *,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> PreMintPoll:
    """Poll the docket once and say whether ``event_id`` is still open on it.

    ``decided`` carries the outcome scan's reason. ``unavailable`` covers every
    way the poll can fail to establish the answer — not a SCOTUS docket, a docket
    number with no Term-form or application spelling, no docket served at that
    number, or a fetch error — and names which in ``reason``. The time recorded
    is the moment the fetch was made, in UTC.
    """
    polled_at = now()
    if court != "scotus":
        return PreMintPoll(polled_at, "unavailable", "not a SCOTUS docket")
    coordinates = docket_coordinates(docket_number)
    if coordinates is None:
        return PreMintPoll(polled_at, "unavailable", "docket number has no live spelling")
    term, serial, form = coordinates
    try:
        payload = fetcher.get_docket(term, serial, form=form)
    except (OffHostFetch, httpx.HTTPError) as exc:
        return PreMintPoll(polled_at, "unavailable", f"fetch failed: {type(exc).__name__}")
    if payload is None:
        return PreMintPoll(polled_at, "unavailable", "no docket served at that number")
    return poll_from_payload(polled_at, payload, court, event_id)


def poll_from_payload(
    polled_at: datetime, payload: Mapping[str, Any], court: str, event_id: str
) -> PreMintPoll:
    """The verdict on a freshly fetched payload: the forward outcome scan, nothing else."""
    reason = forward_leakage(payload, court, event_id)
    if reason is not None:
        return PreMintPoll(polled_at, "decided", reason)
    return PreMintPoll(polled_at, "open")
