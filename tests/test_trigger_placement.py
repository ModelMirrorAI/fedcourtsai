"""A placed cell's snapshot must carry the docket entry that opened its moment."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from fedcourtsai.corpus import CorpusEvent
from fedcourtsai.pipeline import moments
from fedcourtsai.provision import (
    TRIGGER_READERS,
    CellRead,
    TriggerAbsent,
    is_interim_arrival,
    place_at_moment,
    shows_the_moment,
    trigger_reader,
)
from fedcourtsai.schemas import Moment, Stage

_RESPONSE_REQUESTED = "evt-order-response-requested-disposition"
_RESPONSE_FILED = "evt-brief-response-disposition"
_CVSG = "evt-order-cvsg-disposition"
_SG_BRIEF = "evt-brief-sg-disposition"
_CALL_FOR_RESPONSE = "evt-order-call-for-response-disposition"

_APPLICATION = "Application (26A477) for an administrative stay, submitted to Justice Kavanaugh."
_REQUEST = "Response to application (26A477) requested by Justice Kavanaugh, due October 10, 2026."
_RESPONSE = "Response to application (26A477) filed by Sherrod Brown, et al."
_CVSG_TEXT = (
    "The Solicitor General is invited to file a brief in this case expressing "
    + "the views of the United States."
)


def _live(entries: list[tuple[str, str]], number: str = "26A477") -> dict[str, Any]:
    """A live supremecourt.gov-shaped payload, the shape the forward lane stores."""
    return {
        "CaseNumber": number,
        "ProceedingsandOrder": [{"Date": when, "Text": text} for when, text in entries],
    }


def _read(
    event_id: str,
    opened_at: date,
    latest: dict[str, Any],
    dated: tuple[date, dict[str, Any]] | None,
) -> tuple[date, CellRead]:
    cutoff = opened_at + timedelta(days=1)
    event = CorpusEvent(
        event_id=event_id,
        case_id="scotus/9526000477",
        court="scotus",
        kind="order",
        title="NRCC v. Brown",
        opened_at=opened_at,
    )
    return cutoff, CellRead(
        latest=(date(2026, 10, 13), latest),
        documents=[],
        events=[event],
        row=None,
        cutoff=cutoff,
        dated=dated,
    )


def _place(event_id: str, cutoff: date, read: CellRead) -> Any:
    assert read.latest is not None
    snapshot_date, payload = read.latest
    return place_at_moment(
        "scotus/9526000477",
        event_id,
        cutoff,
        read,
        payload=payload,
        snapshot_date=snapshot_date,
        documents=[],
    )


def test_the_reported_shape_is_reconstructed_rather_than_taken_as_dated() -> None:
    # The pull on the request day held only the application, docketed that same
    # day; the request and an amicus brief were docketed after it. The day rule
    # took that pull as `dated` and froze `response_requested=false` for a cell
    # filed under the response-requested moment.
    request_day = date(2026, 10, 8)
    early_pull = _live([("Oct 08 2026", _APPLICATION)])
    later = _live(
        [
            ("Oct 08 2026", _APPLICATION),
            ("Oct 08 2026", _REQUEST),
            ("Oct 10 2026", _RESPONSE),
        ]
    )
    cutoff, read = _read(_RESPONSE_REQUESTED, request_day, later, (request_day, early_pull))

    placement = _place(_RESPONSE_REQUESTED, cutoff, read)

    assert placement.provenance == "truncated"
    assert placement.snapshot_date == cutoff
    texts = [entry["Text"] for entry in placement.payload["ProceedingsandOrder"]]
    assert texts == [_APPLICATION, _REQUEST]


def test_a_dated_pull_whose_trigger_is_older_than_the_event_is_not_taken() -> None:
    # The lower bound: a stored pull carrying a request from two days before the
    # event's date, and nothing from the event's day, is not the docket as it
    # stood at the moment. The dated branch needs the trigger ON the opened day;
    # the reconstruction from the latest payload is what the cell gets.
    request_day = date(2026, 10, 8)
    old_pull = _live([("Oct 06 2026", _APPLICATION), ("Oct 06 2026", _REQUEST)])
    later = _live(
        [("Oct 06 2026", _APPLICATION), ("Oct 06 2026", _REQUEST), ("Oct 08 2026", _RESPONSE)]
    )
    cutoff, read = _read(_RESPONSE_REQUESTED, request_day, later, (date(2026, 10, 6), old_pull))

    assert not shows_the_moment(old_pull, cutoff, _RESPONSE_REQUESTED)
    placement = _place(_RESPONSE_REQUESTED, cutoff, read)
    # The reconstruction keeps the looser bound: a trigger before the cutoff is
    # the moment having happened, and no later pull would resolve the date
    # disagreement, so the cell is placed rather than refused.
    assert placement.provenance == "truncated"
    assert _REQUEST in [e["Text"] for e in placement.payload["ProceedingsandOrder"]]


def test_the_day_rule_alone_would_have_taken_that_pull() -> None:
    # Pins the defect: the early pull does carry an entry from the trigger day.
    request_day = date(2026, 10, 8)
    early_pull = _live([("Oct 08 2026", _APPLICATION)])
    cutoff = request_day + timedelta(days=1)

    assert not shows_the_moment(early_pull, cutoff, _RESPONSE_REQUESTED)
    # An entry-pinned id with no trigger reader keeps the day rule and takes it.
    assert shows_the_moment(early_pull, cutoff, "evt-order-some-entry")


def test_no_payload_carrying_the_trigger_refuses() -> None:
    request_day = date(2026, 10, 8)
    stale = _live([("Oct 08 2026", _APPLICATION)])
    cutoff, read = _read(_RESPONSE_REQUESTED, request_day, stale, (request_day, stale))

    with pytest.raises(TriggerAbsent, match="opened the moment"):
        _place(_RESPONSE_REQUESTED, cutoff, read)


def test_a_trigger_dated_on_or_after_the_cutoff_does_not_count() -> None:
    # The event says the request was on the 8th; a payload whose only request is
    # docketed on the 9th is not evidence of the 8th's, and the cut drops it.
    request_day = date(2026, 10, 8)
    later = _live([("Oct 08 2026", _APPLICATION), ("Oct 09 2026", _REQUEST)])
    cutoff, read = _read(_RESPONSE_REQUESTED, request_day, later, None)

    with pytest.raises(TriggerAbsent):
        _place(_RESPONSE_REQUESTED, cutoff, read)


def test_the_response_filed_moment_needs_the_response() -> None:
    filed_day = date(2026, 10, 10)
    before_response = _live(
        [
            ("Oct 08 2026", _APPLICATION),
            ("Oct 08 2026", _REQUEST),
            ("Oct 10 2026", "Brief amicus curiae of X filed."),
        ]
    )
    with_response = _live(
        [
            ("Oct 08 2026", _APPLICATION),
            ("Oct 08 2026", _REQUEST),
            ("Oct 10 2026", "Brief amicus curiae of X filed."),
            ("Oct 10 2026", _RESPONSE),
        ]
    )
    cutoff, read = _read(_RESPONSE_FILED, filed_day, with_response, (filed_day, before_response))

    placement = _place(_RESPONSE_FILED, cutoff, read)

    assert placement.provenance == "truncated"
    assert _RESPONSE in [e["Text"] for e in placement.payload["ProceedingsandOrder"]]


def test_the_cvsg_moment_needs_the_invitation() -> None:
    cvsg_day = date(2026, 3, 2)
    before = _live([("Mar 02 2026", "DISTRIBUTED for Conference of 3/20/2026.")], "25-100")
    after = _live(
        [
            ("Mar 02 2026", "DISTRIBUTED for Conference of 3/20/2026."),
            ("Mar 02 2026", _CVSG_TEXT),
        ],
        "25-100",
    )
    cutoff, read = _read(_CVSG, cvsg_day, after, (cvsg_day, before))
    placement = _place(_CVSG, cutoff, read)
    assert placement.provenance == "truncated"

    cutoff, read = _read(_CVSG, cvsg_day, after, (cvsg_day, after))
    assert _place(_CVSG, cutoff, read).provenance == "dated"


def test_the_sg_brief_moment_needs_the_brief() -> None:
    brief_day = date(2026, 9, 15)
    head = [
        ("Mar 02 2026", "DISTRIBUTED for Conference of 3/20/2026."),
        ("Mar 23 2026", _CVSG_TEXT),
    ]
    before = _live([*head, ("Sep 15 2026", "Brief amicus curiae of X filed.")], "25-100")
    after = _live(
        [
            *head,
            ("Sep 15 2026", "Brief amicus curiae of X filed."),
            ("Sep 15 2026", "Brief amicus curiae of United States filed."),
        ],
        "25-100",
    )
    cutoff, read = _read(_SG_BRIEF, brief_day, after, (brief_day, before))
    placement = _place(_SG_BRIEF, cutoff, read)
    assert placement.provenance == "truncated"

    cutoff, read = _read(_SG_BRIEF, brief_day, after, (brief_day, after))
    assert _place(_SG_BRIEF, cutoff, read).provenance == "dated"


def test_the_cert_call_for_response_moment_needs_the_call() -> None:
    called = date(2026, 8, 12)
    head = [("Aug 01 2026", "DISTRIBUTED for Conference of 9/29/2026.")]
    before = _live(head, "26-120")
    after = _live(
        [*head, ("Aug 12 2026", "Response Requested. (Due September 11, 2026)")], "26-120"
    )
    cutoff, read = _read(_CALL_FOR_RESPONSE, called, after, (called, before))
    assert _place(_CALL_FOR_RESPONSE, cutoff, read).provenance == "truncated"
    cutoff, read = _read(_CALL_FOR_RESPONSE, called, after, (called, after))
    assert _place(_CALL_FOR_RESPONSE, cutoff, read).provenance == "dated"


def test_the_rest_shape_is_read_too() -> None:
    request_day = date(2026, 6, 25)
    rest = {
        "docket_number": "26A11",
        "docket_entries": [
            {"date_filed": "2026-06-22", "description": _APPLICATION},
            {"date_filed": "2026-06-25", "description": _REQUEST},
        ],
    }
    assert shows_the_moment(rest, request_day + timedelta(days=1), _RESPONSE_REQUESTED)


def test_every_declared_moment_is_bounded_by_some_rule() -> None:
    # A moment added to the table takes the day rule unless it is named here,
    # so this lists, per moment, which rule places it. A new moment fails until
    # someone decides.
    day_rule = {
        (Stage.cert, Moment.distribution),  # never placed: opened_at is docketing
        (Stage.cert, Moment.arrival),
        (Stage.merits, Moment.grant),
        (Stage.merits, Moment.briefed),
    }
    for spec in moments.DECLARED_MOMENTS:
        key = (spec.stage, spec.moment)
        if is_interim_arrival(spec.event_id):
            # Bounded by the anchor rule (`pipeline.arrival_cut`), never both.
            assert trigger_reader(spec.event_id) is None
            continue
        assert (key in TRIGGER_READERS) != (key in day_rule), key
