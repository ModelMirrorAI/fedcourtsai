"""Docket polls that bracket a forward cell: once before it is minted, once after it ran.

A forward cell is provisioned from the corpus's latest stored snapshot, and that
snapshot can be days behind the docket: the live rotation re-polls a pending
application or petition on its own cadence, not at the moment a predict round
mints. An interim application in particular can be decided within hours of a
response or a reply, and an order list issues every disposition of the day at
once, so a cell minted from a snapshot that predates the order can run after
the order is public. The disposition's date carries no time of day, so nothing
after the fact can say which came first.

This module asks the Court's docket JSON directly, at the two moments the harness
controls. The **pre-mint** poll runs just before the cell's record is written: a
disposed event refuses the cell, an undisposed one is recorded with the poll's
time. The **post-run** poll runs after the engine step ends and only records.
Both run the outcome scan the forward gate already runs on the stored snapshot
(:func:`fedcourtsai.pipeline.outcome.forward_leakage`); the fresh payload is read
and discarded, never the cell's input.

A poll that read a payload also records, record-only, what the served docket
showed of each **increment signal** the cell's claims forecast — on an
application, whether a response had been requested and whether the application
had been referred to the full Court; on a petition, whether the Solicitor
General had been invited — each with the entry date the ingest parser reads for
it (:func:`read_increment_signals`). The claim scorer reads the pre-mint
reading to tell an increment that happened before the cell ran from one it
forecast (:func:`fedcourtsai.set_aside.increment_timing`). It decides nothing
here: the verdict is the outcome scan's alone, and a signal reading that fails
leaves the verdict standing and records no signals.

What a poll reading ``open`` means, exactly: at ``polled_at`` the Court's docket
JSON, as served, carried no disposition that ``forward_leakage`` recognises. It is
not proof the event was undecided. Three residuals stand: the JSON can lag the
order or be served from a cache; the scan's recall is not perfect; and a
disposition can land after the poll. Two ``open`` polls bracketing a run do say
the run ended before the served docket showed a decision, though not that the
order was unpublished: an order list or a press account can precede the JSON.

A poll is best-effort and bounded. It fetches through the same host-locked
client the live poller uses, with a short per-phase timeout and a total
deadline checked before every request, retry and redirect hop. Every way it
can fail to answer — not a SCOTUS docket, a number with no live spelling, no
docket served, a body that is not JSON, a timeout, the spent deadline, any
unexpected error in the fetch or the scan — records ``unavailable`` with the
reason, and never refuses a cell.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, Literal, Protocol

import httpx

from ..supremecourt import (
    BROWSER_USER_AGENT,
    DeadlineExceeded,
    SupremeCourtClient,
    parse_scotus_application_number,
    parse_scotus_docket_number,
)
from .cert_signals import (
    CVSG_RE,
    entry_date,
    proceedings_entries,
    snapshot_carries_proceedings,
    snapshot_cvsg_date,
)
from .interim_signals import (
    ReferralPosture,
    referral_date,
    referral_posture,
    response_requested,
    response_requested_date,
)
from .outcome import forward_leakage

PollState = Literal["open", "decided", "unavailable"]

#: How long one poll may wait on the Court, per attempt. Short, because a slow
#: upstream must never hold a cell: a poll that times out reads ``unavailable``.
POLL_TIMEOUT_SECONDS = 10.0

#: The poll's total budget across its retry and any redirect hops, checked before
#: each request. The per-phase timeout alone would let a retry and a redirect chain
#: each start fresh, and the provisioning step that runs the pre-mint poll has no
#: step timeout (a killed step would never record the refusal).
POLL_DEADLINE_SECONDS = 18.0


class DocketFetcher(Protocol):
    """The one call a poll makes: :meth:`SupremeCourtClient.get_docket_response`."""

    def get_docket_response(
        self, term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
    ) -> httpx.Response | None: ...


def bounded_client(clock: Callable[[], float] = time.monotonic) -> SupremeCourtClient:
    """The poll's own client: short timeout, no pauses, and a total deadline.

    The live poller's client paces requests and retries once after a pause, which
    suits a sweep and would stall a cell. This one keeps the host lock and the
    single retry but drops the waits, and refuses to start another request once
    :data:`POLL_DEADLINE_SECONDS` have passed since it was built. The deadline is
    checked between requests, not within one: a body trickling in under the
    per-phase timeout is bounded only by that timeout.
    """
    return SupremeCourtClient(
        throttle_seconds=0.0,
        client=httpx.Client(
            headers={"User-Agent": BROWSER_USER_AGENT},
            timeout=httpx.Timeout(POLL_TIMEOUT_SECONDS),
        ),
        sleep=lambda _seconds: None,
        deadline_seconds=POLL_DEADLINE_SECONDS,
        clock=clock,
    )


@dataclass(frozen=True)
class SignalSeen:
    """One increment signal as the served docket showed it: whether, and the entry's date.

    ``entry_date`` is ``None`` where the signal is absent, and also where its
    entry carries no full date — the ingest parsers skip an undated entry when
    dating a signal, and so does this record.
    """

    present: bool
    entry_date: date | None

    def as_record(self) -> dict[str, Any]:
        """The JSON shape the usage record carries."""
        return {
            "present": self.present,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
        }


@dataclass(frozen=True)
class IncrementSignals:
    """What one served docket showed of each increment signal; ``None`` where not read.

    An application docket fills the two interim signals and a petition docket
    the CVSG, so the signals a docket cannot carry stay ``None`` rather than
    reading as absent.
    """

    response_requested: SignalSeen | None = None
    referred_to_court: SignalSeen | None = None
    cvsg: SignalSeen | None = None

    def as_record(self) -> dict[str, Any]:
        """The JSON shape the usage record carries."""
        return {
            name: seen.as_record() if seen is not None else None
            for name, seen in (
                ("response_requested", self.response_requested),
                ("referred_to_court", self.referred_to_court),
                ("cvsg", self.cvsg),
            )
        }


def read_increment_signals(
    payload: Mapping[str, Any], form: Literal["cert", "application"]
) -> IncrementSignals | None:
    """The increment signals a docket payload shows, by the parsers that date them at ingest.

    The presence test is each signal's ingest flag reading
    (:func:`~fedcourtsai.pipeline.interim_signals.response_requested`,
    :func:`~fedcourtsai.pipeline.interim_signals.referral_posture`, the CVSG
    pattern), and the date is the reading that dates it
    (:func:`~fedcourtsai.pipeline.interim_signals.response_requested_date`,
    :func:`~fedcourtsai.pipeline.interim_signals.referral_date`,
    :func:`~fedcourtsai.pipeline.cert_signals.snapshot_cvsg_date`). ``None``
    where the payload carries no proceedings list, which leaves every signal
    unobserved rather than absent.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    entries = proceedings_entries(payload)
    texts = [text for text, _ in entries]
    if form == "application":
        return IncrementSignals(
            response_requested=SignalSeen(
                response_requested(texts), response_requested_date(entries)
            ),
            referred_to_court=SignalSeen(
                referral_posture(texts) is ReferralPosture.referred_to_court,
                referral_date(entries),
            ),
        )
    return IncrementSignals(
        cvsg=SignalSeen(
            any(CVSG_RE.search(text) for text in texts),
            entry_date(snapshot_cvsg_date(payload)),
        )
    )


@dataclass(frozen=True)
class DocketPoll:
    """What the Court's docket JSON showed for one event at one moment."""

    polled_at: datetime
    docket_number: str
    state: PollState
    reason: str | None = None
    signals: IncrementSignals | None = None

    def as_record(self) -> dict[str, Any]:
        """The JSON shape the usage record carries; ``signals`` only where read."""
        record: dict[str, Any] = {
            "polled_at": self.polled_at.isoformat().replace("+00:00", "Z"),
            "docket_number": self.docket_number,
            "state": self.state,
            "reason": self.reason,
        }
        if self.signals is not None:
            record["signals"] = self.signals.as_record()
        return record


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


def poll_docket(
    court: str,
    docket_number: str,
    event_id: str,
    fetcher: DocketFetcher,
    *,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> DocketPoll:
    """Poll the docket once and say whether ``event_id``'s outcome shows on it.

    ``polled_at`` is when the fetch began, in UTC. ``decided`` carries the outcome
    scan's reason; ``unavailable`` names why the poll could not answer. Nothing
    here raises: an unexpected error anywhere in the fetch or the scan reads
    ``unavailable`` with the error's type, because a poll must never be the
    reason a cell is lost.
    """
    polled_at = now()
    number = docket_number.strip()
    state, reason, signals = _read_docket(court, number, event_id, fetcher)
    return DocketPoll(polled_at, number, state, reason, signals)


def _read_docket(
    court: str, number: str, event_id: str, fetcher: DocketFetcher
) -> tuple[PollState, str | None, IncrementSignals | None]:
    """The poll's verdict, its reason, and the signals read; every failure is ``unavailable``."""
    if court != "scotus":
        return "unavailable", "not a SCOTUS docket", None
    coordinates = docket_coordinates(number)
    if coordinates is None:
        return "unavailable", "docket number has no live spelling", None
    try:
        payload = _fetch_payload(fetcher, *coordinates)
        if isinstance(payload, str):
            return "unavailable", payload, None
        reason = forward_leakage(payload, court, event_id)
    except (httpx.TimeoutException, DeadlineExceeded) as exc:
        spent = isinstance(exc, DeadlineExceeded)
        return "unavailable", "poll deadline exceeded" if spent else "fetch timed out", None
    # Anything else, from the fetch or the scan: a poll degrades, never fails the cell.
    except Exception as exc:
        return "unavailable", f"poll error: {type(exc).__name__}", None
    signals = _signals_or_none(payload, coordinates[2])
    return ("decided", reason, signals) if reason is not None else ("open", None, signals)


def _signals_or_none(
    payload: Mapping[str, Any], form: Literal["cert", "application"]
) -> IncrementSignals | None:
    """:func:`read_increment_signals`, with any error read as no signals.

    Taken after the verdict and guarded on its own, so a signal reading that
    fails can never turn a ``decided`` verdict — the one that refuses a cell —
    into ``unavailable``.
    """
    try:
        return read_increment_signals(payload, form)
    except Exception:
        return None


def _fetch_payload(
    fetcher: DocketFetcher, term: int, serial: int, form: Literal["cert", "application"]
) -> dict[str, Any] | str:
    """The docket JSON object, or the reason there is none to scan."""
    response = fetcher.get_docket_response(term, serial, form=form)
    if response is None:
        return "no docket served at that number"
    try:
        payload = response.json()
    except json.JSONDecodeError:
        return "docket body is not JSON"
    if not isinstance(payload, dict):
        return "docket JSON is not an object"
    return payload
