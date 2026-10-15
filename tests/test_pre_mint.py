from datetime import UTC, datetime
from typing import Any, Literal

import httpx
import pytest

from fedcourtsai.pipeline.pre_mint import PreMintPoll, docket_coordinates, poll_before_mint

_NOON = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)

_PENDING_APPLICATION = {
    "CaseNumber": "26A477 ",
    "ProceedingsandOrder": [
        {"Text": "Application (26A477) for a stay, submitted to Justice Sotomayor."},
        {"Text": "Response to application (26A477) requested by Justice Sotomayor."},
    ],
}
_DECIDED_APPLICATION = {
    "CaseNumber": "26A477 ",
    "ProceedingsandOrder": [
        *_PENDING_APPLICATION["ProceedingsandOrder"],
        {"Text": "Application (26A477) denied as moot by Justice Sotomayor."},
    ],
}


class _Fetcher:
    def __init__(self, payload: dict[str, Any] | None = None, error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.calls: list[tuple[int, int, str]] = []

    def get_docket(
        self, term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
    ) -> dict[str, Any] | None:
        self.calls.append((term, serial, form))
        if self.error is not None:
            raise self.error
        return self.payload


def _poll(fetcher: _Fetcher, number: str = "26A477", court: str = "scotus") -> PreMintPoll:
    return poll_before_mint(court, number, "evt-motion-disposition", fetcher, now=lambda: _NOON)


def test_an_open_docket_records_the_poll_time_and_open() -> None:
    fetcher = _Fetcher(_PENDING_APPLICATION)

    poll = _poll(fetcher)

    assert poll == PreMintPoll(_NOON, "open")
    assert fetcher.calls == [(26, 477, "application")]
    assert poll.as_record() == {
        "polled_at": "2026-10-14T12:00:00Z",
        "state": "open",
        "reason": None,
    }


def test_a_docket_already_showing_the_outcome_reads_decided() -> None:
    poll = _poll(_Fetcher(_DECIDED_APPLICATION))

    assert poll.state == "decided"
    assert poll.reason


def test_a_cert_docket_number_polls_the_cert_form() -> None:
    fetcher = _Fetcher({"CaseNumber": "26-221 ", "ProceedingsandOrder": []})

    poll = poll_before_mint(
        "scotus", "26-221", "evt-petition-disposition", fetcher, now=lambda: _NOON
    )

    assert poll.state == "open"
    assert fetcher.calls == [(26, 221, "cert")]


@pytest.mark.parametrize(
    ("fetcher", "number", "court", "reason"),
    [
        (_Fetcher(None), "26A477", "scotus", "no docket served"),
        (_Fetcher(error=httpx.ConnectError("down")), "26A477", "scotus", "fetch failed"),
        (_Fetcher(_PENDING_APPLICATION), "", "scotus", "no live spelling"),
        (_Fetcher(_PENDING_APPLICATION), "26A477", "ca9", "not a SCOTUS docket"),
    ],
)
def test_a_poll_that_establishes_nothing_reads_unavailable(
    fetcher: _Fetcher, number: str, court: str, reason: str
) -> None:
    poll = _poll(fetcher, number, court)

    assert poll.state == "unavailable"
    assert poll.reason is not None and reason in poll.reason


def test_docket_coordinates_spell_both_forms() -> None:
    assert docket_coordinates("26A477 ") == (26, 477, "application")
    assert docket_coordinates("26-221") == (26, 221, "cert")
    assert docket_coordinates("Orig. 141") is None
