"""The interim arrival moment's anchor bound: what it keeps, drops, and refuses."""

from datetime import date
from typing import Any

from fedcourtsai import provision
from fedcourtsai.pipeline import arrival_cut

_OPENED = date(2026, 6, 22)

_SUBMITTED = (
    "Application (26A11) for a stay of the mandate pending the filing and "
    + "disposition of a petition for a writ of certiorari, submitted to The Chief Justice."
)
_REFERRED = "Application (26A11) referred to the Court."
_DENIED = "Application (26A11) referred to the Court. Application denied by the Court."
_AMICUS = "Brief amicus curiae of Grid Reliability Council filed."
_RESPONSE_REQUESTED = "Response to application (26A11) requested, due July 2, 2026."
_EARLIER = "Motion for leave to proceed in forma pauperis filed."


def _live(*entries: tuple[str, str]) -> dict[str, Any]:
    """A live supremecourt.gov-shaped payload carrying ``(date, text)`` entries."""
    return {
        "CaseNumber": "26A11",
        "ProceedingsandOrder": [{"Date": when, "Text": text} for when, text in entries],
    }


def _texts(payload: dict[str, Any]) -> list[str]:
    return [entry["Text"] for entry in payload["ProceedingsandOrder"]]


def _dated(*raw: str | None) -> list[tuple[str, str | None]]:
    """Entries carrying only dates — the chronology reading looks at nothing else."""
    return [("", when) for when in raw]


# --- the chronology reading the anchor bound rests on -------------------------


def test_an_oldest_first_list_reads_as_ascending() -> None:
    assert arrival_cut.docket_order(_dated("2026-06-20", "2026-06-22", "2026-07-14")) == (
        "ascending"
    )


def test_a_newest_first_list_reads_as_descending() -> None:
    # The shape a naive positional slice gets exactly backwards.
    assert arrival_cut.docket_order(_dated("2026-07-14", "2026-06-22", "2026-06-20")) == (
        "descending"
    )


def test_a_single_day_docket_reads_as_neither() -> None:
    # Every date equal is consistent with either direction, so the chronology
    # says nothing and the caller has to fail closed rather than pick one.
    assert arrival_cut.docket_order(_dated("2026-06-22", "2026-06-22", "2026-06-22")) is None


def test_a_non_monotone_list_reads_as_neither() -> None:
    assert arrival_cut.docket_order(_dated("2026-06-20", "2026-07-14", "2026-06-22")) is None


def test_an_undated_entry_does_not_make_the_chronology_unreadable() -> None:
    # It is dropped by the date bound anyway; letting it break the direction
    # reading would refuse cells the anchor can place.
    assert arrival_cut.docket_order(_dated("2026-06-20", None, "2026-07-14")) == "ascending"


# --- locating the opening entry -----------------------------------------------


def test_the_anchor_is_the_submission_entry_stamped_at_the_opening_date() -> None:
    payload = _live(
        ("2026-06-22", _SUBMITTED),
        ("2026-06-22", _REFERRED),
        ("2026-07-14", _DENIED),
    )
    entries = [(e["Text"], e["Date"]) for e in payload["ProceedingsandOrder"]]
    assert arrival_cut.anchor_index(entries, docket_number="26A11", opened_at=_OPENED) == 0


def test_a_stale_stamp_refuses_rather_than_anchoring_on_another_entry() -> None:
    # The docketing date rather than the submission date: the stamp names a day
    # the submission entry is not on, so the moment's own entry cannot be
    # identified and the row refuses.
    payload = _live(("2026-06-22", _SUBMITTED), ("2026-06-26", _REFERRED))
    entries = [(e["Text"], e["Date"]) for e in payload["ProceedingsandOrder"]]
    docketed = date(2026, 6, 26)
    assert arrival_cut.anchor_index(entries, docket_number="26A11", opened_at=docketed) is None


def test_a_refiled_application_is_not_the_arrival() -> None:
    # The renewal form carries the submission verb; read the same way the
    # arrival parser reads it, or the two would disagree about which entry
    # opened the event.
    payload = _live(("2026-06-22", "Application (26A11) refiled and submitted to Justice Alito."))
    entries = [(e["Text"], e["Date"]) for e in payload["ProceedingsandOrder"]]
    assert arrival_cut.anchor_index(entries, docket_number="26A11", opened_at=_OPENED) is None


def test_a_docket_with_no_number_cannot_be_anchored() -> None:
    entries = [(_SUBMITTED, "2026-06-22")]
    assert arrival_cut.anchor_index(entries, docket_number="", opened_at=_OPENED) is None


# --- the cut itself -----------------------------------------------------------


def test_the_opening_days_later_entries_are_outside_the_information_set() -> None:
    cut = arrival_cut.cut_at_arrival(
        _live(
            ("2026-06-20", _EARLIER),
            ("2026-06-22", _SUBMITTED),
            ("2026-06-22", _REFERRED),
            ("2026-06-22", _AMICUS),
        ),
        docket_number="26A11",
        opened_at=_OPENED,
    )

    assert cut is not None
    # Everything filed before the opening day survives whatever its position;
    # the opening day is kept only up to the opening entry.
    assert _texts(cut.payload) == [_EARLIER, _SUBMITTED]
    assert cut.anchor_index == 1
    assert cut.dropped_same_day == 2


def test_a_same_day_disposed_application_is_not_shown_its_own_disposition() -> None:
    # The measured shape (docket 25A1295): submitted, referred and disposed of
    # inside one day, which is exactly what a date-valued cutoff cannot express
    # — `cutoff` is the day after, so the date rule admits all three.
    entries = (
        ("2026-06-22", _SUBMITTED),
        ("2026-06-22", _REFERRED),
        ("2026-06-22", _DENIED),
    )
    # The chronology of an all-one-day docket is unreadable, so the bound fails
    # closed to the anchor entry alone — which is the whole of what the arrival
    # moment saw on this shape.
    assert arrival_cut.docket_order([(text, when) for when, text in entries]) is None

    cut = arrival_cut.cut_at_arrival(_live(*entries), docket_number="26A11", opened_at=_OPENED)

    assert cut is not None
    assert _texts(cut.payload) == [_SUBMITTED]
    assert cut.dropped_a_disposition is True


def test_a_newest_first_docket_keeps_the_right_half() -> None:
    # THE ORDERING GUARD. Payload entry order is not pinned across the upstream
    # shapes, and on a newest-first list a naive `entries[:anchor]` keeps
    # precisely the tail the cut exists to remove — silently. Removing the
    # direction reading from `same_day_tail` fails this test: the disposition
    # sits BEFORE the anchor here, so an ascending-only bound would keep it and
    # drop the pre-arrival entry instead.
    cut = arrival_cut.cut_at_arrival(
        _live(
            ("2026-06-22", _DENIED),
            ("2026-06-22", _REFERRED),
            ("2026-06-22", _SUBMITTED),
            ("2026-06-20", _EARLIER),
        ),
        docket_number="26A11",
        opened_at=_OPENED,
    )

    assert cut is not None
    assert _texts(cut.payload) == [_SUBMITTED, _EARLIER]
    assert cut.anchor_index == 2
    assert cut.dropped_a_disposition is True


def test_entries_from_before_the_opening_day_survive_whatever_their_position() -> None:
    # A back-filled entry sitting after the anchor in a non-monotone list still
    # predates the moment, so the date half keeps it and only the same-day run
    # is split around the anchor.
    cut = arrival_cut.cut_at_arrival(
        _live(
            ("2026-06-22", _SUBMITTED),
            ("2026-06-20", _EARLIER),
            ("2026-06-22", _REFERRED),
        ),
        docket_number="26A11",
        opened_at=_OPENED,
    )

    assert cut is not None
    assert _texts(cut.payload) == [_SUBMITTED, _EARLIER]


def test_a_payload_disclosing_no_proceedings_refuses() -> None:
    assert (
        arrival_cut.cut_at_arrival(
            {"CaseNumber": "26A11"}, docket_number="26A11", opened_at=_OPENED
        )
        is None
    )


def test_the_rest_shape_is_cut_on_its_own_keys() -> None:
    payload: dict[str, Any] = {
        "docket_number": "26A11",
        "docket_entries": [
            {"date_filed": "2026-06-22", "description": _SUBMITTED},
            {"date_filed": "2026-06-22", "description": _RESPONSE_REQUESTED},
        ],
    }

    cut = arrival_cut.cut_at_arrival(payload, docket_number="26A11", opened_at=_OPENED)

    assert cut is not None
    assert [e["description"] for e in cut.payload["docket_entries"]] == [_SUBMITTED]


def test_the_docket_number_is_read_from_either_payload_shape() -> None:
    assert arrival_cut.payload_docket_number({"CaseNumber": "26A11"}) == "26A11"
    assert arrival_cut.payload_docket_number({"docket_number": "26A11"}) == "26A11"
    assert arrival_cut.payload_docket_number({}) == ""


def test_a_capital_case_marking_does_not_defeat_the_anchor() -> None:
    # The live channel appends the marking to the number while ingest stores it
    # stripped and stamps `opened_at` from the stripped form. Reading the raw
    # payload value would build a pattern no entry matches, and the cell would
    # refuse — falling hardest on the shape this module exists for, since a
    # capital stay application is the one most likely to be decided in a day.
    payload = _live(("2026-06-22", _SUBMITTED), ("2026-06-22", _DENIED))
    payload["CaseNumber"] = "26A11 *** CAPITAL CASE ***"

    assert arrival_cut.payload_docket_number(payload) == "26A11"

    cut = arrival_cut.cut_at_arrival(
        payload,
        docket_number=arrival_cut.payload_docket_number(payload),
        opened_at=_OPENED,
    )

    assert cut is not None
    assert _texts(cut.payload) == [_SUBMITTED]


def test_a_non_mapping_entry_does_not_misalign_the_cut() -> None:
    # `proceedings_entries` skips a non-mapping element, so the read view and the
    # stored list can differ in length and an index from one names a different
    # entry in the other. Applying a read-view index to the stored list fails
    # OPEN here: it would drop the submission entry and keep the same-day denial,
    # while the context recorded that the tighter bound ran.
    payload: dict[str, Any] = {
        "CaseNumber": "26A11",
        "ProceedingsandOrder": [
            None,
            {"Date": "2026-06-22", "Text": _SUBMITTED},
            {"Date": "2026-06-22", "Text": _DENIED},
        ],
    }

    cut = arrival_cut.cut_at_arrival(payload, docket_number="26A11", opened_at=_OPENED)

    assert cut is not None
    kept = cut.payload["ProceedingsandOrder"]
    # The stray element is untouched, the submission entry survives, the
    # same-day denial goes.
    assert kept[0] is None
    assert [e["Text"] for e in kept[1:]] == [_SUBMITTED]
    # And the reported anchor is a position in the payload's own list, so an
    # auditor counting entries in the stored snapshot lands on the right entry.
    assert cut.anchor_index == 1


# --- which moments take the bound ---------------------------------------------


def test_only_the_interim_arrival_moment_takes_the_anchor_bound() -> None:
    assert provision.is_interim_arrival("evt-motion-disposition") is True
    # The cert baseline's declared moment is the distribution, and the merits
    # moments open at a grant — neither has an intra-day tail to exclude.
    assert provision.is_interim_arrival("evt-petition-disposition") is False
    assert provision.is_interim_arrival("evt-order-judgment") is False
    assert provision.is_interim_arrival("evt-nothing-declared") is False
