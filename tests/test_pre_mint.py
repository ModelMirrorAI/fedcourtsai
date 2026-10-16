import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any, Literal

import httpx
import pytest

from fedcourtsai.pipeline import pre_mint
from fedcourtsai.pipeline.pre_mint import (
    POLL_DEADLINE_SECONDS,
    DocketFetcher,
    DocketPoll,
    IncrementSignals,
    SignalSeen,
    bounded_client,
    docket_coordinates,
    poll_docket,
)
from fedcourtsai.schemas import DocketPollRecord
from fedcourtsai.supremecourt import SupremeCourtClient

_NOON = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)

_PENDING_APPLICATION: dict[str, Any] = {
    "CaseNumber": "26A477 ",
    "ProceedingsandOrder": [
        {"Text": "Application (26A477) for a stay, submitted to Justice Sotomayor."},
        {"Text": "Response to application (26A477) requested by Justice Sotomayor."},
    ],
}
_DECIDED_APPLICATION: dict[str, Any] = {
    "CaseNumber": "26A477 ",
    "ProceedingsandOrder": [
        *_PENDING_APPLICATION["ProceedingsandOrder"],
        {"Text": "Application (26A477) denied as moot by Justice Sotomayor."},
    ],
}


def _response(body: object, *, raw: bytes | None = None) -> httpx.Response:
    content = raw if raw is not None else json.dumps(body).encode()
    return httpx.Response(200, content=content, request=httpx.Request("GET", "https://x"))


class _Fetcher:
    def __init__(
        self, response: httpx.Response | None = None, error: Exception | None = None
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[tuple[int, int, str]] = []

    def get_docket_response(
        self, term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
    ) -> httpx.Response | None:
        self.calls.append((term, serial, form))
        if self.error is not None:
            raise self.error
        return self.response


def _poll(fetcher: DocketFetcher, number: str = "26A477", court: str = "scotus") -> DocketPoll:
    return poll_docket(court, number, "evt-motion-disposition", fetcher, now=lambda: _NOON)


def test_an_open_docket_records_the_fetch_time_and_open() -> None:
    fetcher = _Fetcher(_response(_PENDING_APPLICATION))

    poll = _poll(fetcher)

    assert poll == DocketPoll(
        _NOON,
        "26A477",
        "open",
        signals=IncrementSignals(
            response_requested=SignalSeen(True, None),
            referred_to_court=SignalSeen(False, None),
        ),
    )
    assert fetcher.calls == [(26, 477, "application")]
    assert poll.as_record() == {
        "polled_at": "2026-10-14T12:00:00Z",
        "docket_number": "26A477",
        "state": "open",
        "reason": None,
        "signals": {
            "response_requested": {"present": True, "entry_date": None},
            "referred_to_court": {"present": False, "entry_date": None},
            "cvsg": None,
        },
    }


def test_an_application_poll_records_each_signal_and_its_ingest_date() -> None:
    payload = {
        "CaseNumber": "26A477 ",
        "ProceedingsandOrder": [
            {"Date": "Sep 30 2026", "Text": "Application (26A477) for a stay, submitted."},
            {
                "Date": "Oct 02 2026",
                "Text": "Response to application (26A477) requested by Justice Kagan, due "
                + "Oct 9.",
            },
            {
                "Date": "Oct 03 2026",
                "Text": "Application (26A477) referred to the Court by Justice Kagan.",
            },
        ],
    }

    poll = _poll(_Fetcher(_response(payload)))

    assert poll.state == "open"
    assert poll.signals == IncrementSignals(
        response_requested=SignalSeen(True, date(2026, 10, 2)),
        referred_to_court=SignalSeen(True, date(2026, 10, 3)),
    )
    record = DocketPollRecord.model_validate(poll.as_record())
    assert record.signals is not None and record.signals.referred_to_court is not None
    assert record.signals.referred_to_court.entry_date == date(2026, 10, 3)
    assert record.signals.cvsg is None


def test_a_cert_poll_records_the_cvsg_and_nothing_interim() -> None:
    payload = {
        "CaseNumber": "26-221 ",
        "ProceedingsandOrder": [
            {"Date": "Oct 05 2026", "Text": "DISTRIBUTED for Conference of 10/9/2026."},
            {
                "Date": "Oct 13 2026",
                "Text": "The Solicitor General is invited to file a brief in this case "
                + "expressing the views of the United States.",
            },
        ],
    }

    poll = poll_docket("scotus", "26-221", "evt-petition-disposition", _Fetcher(_response(payload)))

    assert poll.signals == IncrementSignals(cvsg=SignalSeen(True, date(2026, 10, 13)))


def test_a_payload_without_proceedings_records_no_signals() -> None:
    poll = _poll(_Fetcher(_response({"CaseNumber": "26A477"})))

    assert poll.signals is None
    assert "signals" not in poll.as_record()


def test_a_signal_reading_that_fails_never_unrefuses_a_decided_docket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(_payload: object, _form: object) -> None:
        raise RuntimeError("parser broke")

    monkeypatch.setattr(pre_mint, "read_increment_signals", boom)

    poll = _poll(_Fetcher(_response(_DECIDED_APPLICATION)))

    assert poll.state == "decided"
    assert poll.signals is None


def test_a_docket_already_showing_the_outcome_reads_decided() -> None:
    poll = _poll(_Fetcher(_response(_DECIDED_APPLICATION)))

    assert poll.state == "decided"
    assert poll.reason


def test_a_cert_docket_number_polls_the_cert_form() -> None:
    fetcher = _Fetcher(_response({"CaseNumber": "26-221 ", "ProceedingsandOrder": []}))

    poll = poll_docket("scotus", "26-221", "evt-petition-disposition", fetcher, now=lambda: _NOON)

    assert poll.state == "open"
    assert fetcher.calls == [(26, 221, "cert")]


@pytest.mark.parametrize(
    ("fetcher", "number", "court", "reason"),
    [
        (_Fetcher(None), "26A477", "scotus", "no docket served"),
        (_Fetcher(_response(None, raw=b"<html>busy</html>")), "26A477", "scotus", "not JSON"),
        (_Fetcher(_response([1, 2])), "26A477", "scotus", "not an object"),
        (_Fetcher(error=httpx.ReadTimeout("slow")), "26A477", "scotus", "timed out"),
        (
            _Fetcher(error=httpx.ConnectError("down")),
            "26A477",
            "scotus",
            "poll error: ConnectError",
        ),
        (_Fetcher(error=RuntimeError("boom")), "26A477", "scotus", "poll error: RuntimeError"),
        (_Fetcher(_response(_PENDING_APPLICATION)), "", "scotus", "no live spelling"),
        (_Fetcher(_response(_PENDING_APPLICATION)), "26A477", "ca9", "not a SCOTUS docket"),
    ],
)
def test_a_poll_that_cannot_answer_reads_unavailable(
    fetcher: _Fetcher, number: str, court: str, reason: str
) -> None:
    poll = _poll(fetcher, number, court)

    assert poll.state == "unavailable"
    assert poll.reason is not None and reason in poll.reason


def test_a_malformed_payload_never_raises() -> None:
    # A scalar where the entry list belongs: whatever the scan makes of it, the
    # poll answers rather than failing the cell.
    poll = _poll(_Fetcher(_response({"CaseNumber": "26A477", "ProceedingsandOrder": 7})))

    assert poll.state in {"open", "decided", "unavailable"}


def test_docket_coordinates_spell_both_forms() -> None:
    assert docket_coordinates("26A477 ") == (26, 477, "application")
    assert docket_coordinates("26-221") == (26, 221, "cert")
    assert docket_coordinates("Orig. 141") is None


class _Clock:
    """A monotonic clock the test moves by hand."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def _deadline_client(
    clock: _Clock, handler: Callable[[httpx.Request], httpx.Response]
) -> SupremeCourtClient:
    return SupremeCourtClient(
        throttle_seconds=0.0,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=lambda _seconds: None,
        deadline_seconds=POLL_DEADLINE_SECONDS,
        clock=clock,
    )


def test_the_deadline_stops_the_retry_once_spent() -> None:
    clock = _Clock()
    requests: list[str] = []

    def slow_503(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        clock.now += POLL_DEADLINE_SECONDS  # the first attempt spends the budget
        return httpx.Response(503)

    poll = _poll(_deadline_client(clock, slow_503))

    assert poll == DocketPoll(_NOON, "26A477", "unavailable", "poll deadline exceeded")
    assert len(requests) == 1


def test_the_deadline_stops_a_redirect_chain_between_hops() -> None:
    clock = _Clock()
    requests: list[str] = []

    def redirect_onward(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        clock.now += 7.0
        return httpx.Response(
            302, headers={"Location": f"https://www.supremecourt.gov/hop{len(requests)}"}
        )

    poll = _poll(_deadline_client(clock, redirect_onward))

    assert poll.state == "unavailable"
    assert poll.reason == "poll deadline exceeded"
    # Requests start at 0 s, 7 s and 14 s; at 21 s the 18 s budget is spent.
    assert len(requests) == 3


def test_the_poll_client_carries_the_deadline() -> None:
    clock = _Clock()
    with bounded_client(clock=clock) as client:
        clock.now = POLL_DEADLINE_SECONDS
        # Spent before the first request, so no network is touched.
        poll = _poll(client)

    assert poll.reason == "poll deadline exceeded"


def test_a_client_without_a_deadline_is_unbounded() -> None:
    clock = _Clock()

    def slow_ok(request: httpx.Request) -> httpx.Response:
        clock.now += 1_000.0
        return httpx.Response(200, json=_PENDING_APPLICATION)

    client = SupremeCourtClient(
        throttle_seconds=0.0,
        client=httpx.Client(transport=httpx.MockTransport(slow_ok)),
        clock=clock,
    )
    clock.now = 1_000_000.0

    assert _poll(client).state == "open"
