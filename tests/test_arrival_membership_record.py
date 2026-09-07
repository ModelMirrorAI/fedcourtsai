"""The committed arrival-backfill membership record stays what was registered.

`metrics/arrival-backfill-membership.json` is a write-once record: the filled
membership of the interim arrival repair, committed because its only other
derivation path — a dry-run against the superseded pre-apply corpus index
object — lapses with the store's lifecycle. Once that object is gone the file
*is* the population, so these tests pin the claim itself: the row set carries
the registered census, every registered aggregate re-derives from the rows,
and any later edit or truncation fails loudly rather than rotting the one copy.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai.pipeline.arrival_backfill import ArrivalFill

RECORD = Path("metrics/arrival-backfill-membership.json")

# The registered figures (docs/freeze-record.md, the arrival-backfill apply
# entry). Dated constants are the point: the record preserves this exact
# population, so a mismatch is corruption, never drift to accommodate.
CANDIDATES = 2070
FILLED = 1956
UNCHANGED = 113
UNPARSED = 1
NEWLY_BOUNDED = 109
MOVED = 1847
WORST_MOVE_DAYS = 473
OVER_ADMITTED_ENTRIES = 936
OVER_ADMITTED_ROWS = 778
ADMITTED_DISPOSITION = 701
ADMITTED_RESPONSE_REQUEST = 15
HISTOGRAM = {"1d": 25, "2-3d": 407, "4-7d": 798, "8-14d": 350, "15-30d": 156, "31+d": 111}


@pytest.fixture(scope="module")
def record() -> dict[str, object]:
    return json.loads(RECORD.read_text())  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def fills(record: dict[str, object]) -> list[ArrivalFill]:
    rows = record["filled"]
    assert isinstance(rows, list)
    return [ArrivalFill.model_validate(row) for row in rows]


def test_census_reconciles_and_matches_the_rows(record: dict[str, object]) -> None:
    census = record["census"]
    assert isinstance(census, dict)
    arms = ["filled", "unchanged", "unparsed", "no_snapshot", "no_proceedings", "later_refused"]
    assert sum(int(census[a]) for a in arms) == int(census["candidates"]) == CANDIDATES
    assert int(census["filled"]) == len(record["filled"]) == FILLED  # type: ignore[arg-type]
    assert int(census["unchanged"]) == len(record["unchanged"]) == UNCHANGED  # type: ignore[arg-type]
    assert int(census["unparsed"]) == len(record["unparsed"]) == UNPARSED  # type: ignore[arg-type]


def test_rows_are_unique_and_disjoint_across_arms(record: dict[str, object]) -> None:
    def keys(name: str) -> set[tuple[str, str]]:
        rows = record[name]
        assert isinstance(rows, list)
        return {(str(r["case_id"]), str(r["event_id"])) for r in rows}

    filled, unchanged, unparsed = keys("filled"), keys("unchanged"), keys("unparsed")
    assert len(filled) == FILLED and len(unchanged) == UNCHANGED and len(unparsed) == UNPARSED
    assert not (filled & unchanged) and not (filled & unparsed) and not (unchanged & unparsed)


def test_registered_aggregates_re_derive_from_the_rows(fills: list[ArrivalFill]) -> None:
    newly_bounded = [f for f in fills if f.previous is None]
    moved = [f for f in fills if f.previous is not None]
    assert len(newly_bounded) == NEWLY_BOUNDED and len(moved) == MOVED
    deltas = [(f.previous - f.opened_at).days for f in moved if f.previous is not None]
    # The direction guard: the pass only ever moves a stamp earlier.
    assert min(deltas) >= 1 and max(deltas) == WORST_MOVE_DAYS
    assert sum(f.over_admitted for f in fills) == OVER_ADMITTED_ENTRIES
    assert sum(1 for f in fills if f.over_admitted > 0) == OVER_ADMITTED_ROWS
    assert sum(1 for f in fills if f.admitted_the_disposition) == ADMITTED_DISPOSITION
    assert sum(1 for f in fills if f.admitted_the_response_request) == ADMITTED_RESPONSE_REQUEST


def test_move_histogram_matches_the_registered_buckets(fills: list[ArrivalFill]) -> None:
    buckets = dict.fromkeys(HISTOGRAM, 0)
    for fill in fills:
        if fill.previous is None:
            continue
        days = (fill.previous - fill.opened_at).days
        if days <= 1:
            key = "1d"
        elif days <= 3:
            key = "2-3d"
        elif days <= 7:
            key = "4-7d"
        elif days <= 14:
            key = "8-14d"
        elif days <= 30:
            key = "15-30d"
        else:
            key = "31+d"
        buckets[key] += 1
    assert buckets == HISTOGRAM


def test_the_reading_and_vintage_travel_with_the_counterfactual_columns(
    record: dict[str, object],
) -> None:
    # The exposure columns are bounds over the corpus at a fixed vintage; a copy
    # of this file without that basis states a bound whose basis is unrecoverable.
    assert date.fromisoformat(str(record["corpus_vintage"])) == date(2026, 9, 5)
    reading = str(record["reading"])
    assert "corpus_vintage" in reading and "bound" in reading
    assert record["field_semantics"] == "fedcourtsai.pipeline.arrival_backfill.ArrivalFill"
