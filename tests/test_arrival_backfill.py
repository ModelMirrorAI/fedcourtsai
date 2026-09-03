"""The interim baseline's arrival-stamp back-fill.

No network at all: the pass re-parses each row's newest stored live-shaped
snapshot with the same pure parsers ingest uses, so the fixtures are rows,
events and snapshots.

What the tests are really about is **direction**. The cut provisioning takes
keeps everything filed strictly before the day after ``opened_at``, so an
earlier stamp admits less docket and a later one admits more — which makes the
stamp a leakage control and not a label. The pass therefore only ever moves a
stamp earlier or supplies a missing one, and the tests that matter most are the
ones proving it refuses the other direction and reports how far each repaired
row had been over-admitting.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.arrival_backfill import (
    MOTION_BASELINE_EVENT_ID,
    MOVE_BUCKETS,
    ArrivalBackfillResult,
    arrival_candidates,
    backfill_arrival_stamps,
)
from fedcourtsai.schemas import EventKind, Moment, Stage

runner = CliRunner()

_CASE = "scotus/1"
_DOCKET = "26A203"
#: The day the Clerk docketed the application, which is the fallback stamp and
#: systematically the *later* of the two readings.
_DOCKETED = date(2026, 6, 10)
#: The day it was actually submitted to a Justice, which is the declared moment.
_SUBMITTED = date(2026, 6, 5)


def _submission(
    *, number: str = _DOCKET, day: str = "Jun 05 2026", justice: str = "Kagan"
) -> dict[str, Any]:
    """The application's own submission entry — the anchor the arrival is read from."""
    return {
        "Text": (
            f"Application ({number}) for a stay of the mandate, submitted to Justice {justice}."
        ),
        "Date": day,
    }


def _renewal(*, number: str = _DOCKET, day: str = "Jun 20 2026") -> dict[str, Any]:
    """The Clerk's renewal form, which carries the filing verb and is never the arrival.

    An application denied by one Justice is refiled to another under the same
    number. It is common — and it postdates a disposition of the same
    application, so reading it as an arrival would stamp the moment after its
    own first denial.
    """
    return {
        "Text": f"Application ({number}) refiled and submitted to Justice Alito.",
        "Date": day,
    }


def _disposition(*, number: str = _DOCKET, day: str = "Jun 25 2026") -> dict[str, Any]:
    """The disposing order, which names the number and must not read as a submission."""
    return {"Text": f"Application ({number}) denied by Justice Kagan.", "Date": day}


def _payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {"CaseNumber": f"{_DOCKET} ", "ProceedingsandOrder": list(entries)}


def _row(case_id: str = _CASE, **fields: Any) -> corpus.CorpusRow:
    base: dict[str, Any] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": _DOCKET,
        "date_filed": _DOCKETED,
        # Live-slice membership: the repair reads the stored live-shaped snapshot.
        "last_live_polled": date(2026, 7, 1),
    }
    return corpus.CorpusRow.model_validate({**base, **fields})


def _event(
    case_id: str = _CASE,
    *,
    opened_at: date | None = None,
    event_id: str = MOTION_BASELINE_EVENT_ID,
    docket_entry_id: int | None = None,
    resolved: bool = True,
) -> corpus.CorpusEvent:
    """An interim baseline event, decided by default — the class this pass repairs."""
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id=case_id,
        court="scotus",
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        title="Application for a stay",
        docket_entry_id=docket_entry_id,
        opened_at=opened_at,
        resolved=resolved,
    )


@contextmanager
def _seeded(
    corpus_root: Path,
    rows: list[corpus.CorpusRow],
    events: list[corpus.CorpusEvent],
    snapshots: dict[str, tuple[date, dict[str, Any]]] | None = None,
) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_events(conn, events)
        for case_id, (day, payload) in (snapshots or {}).items():
            corpus.upsert_snapshot(conn, case_id, day, payload)
        conn.commit()
        yield conn


def _stored(conn: sqlite3.Connection, case_id: str = _CASE) -> date | None:
    (event,) = [
        event
        for event in corpus.events_for_case(conn, case_id)
        if event.event_id == MOTION_BASELINE_EVENT_ID
    ]
    return event.opened_at


# --- The population predicate ------------------------------------------------


def test_both_shapes_of_the_defect_are_one_class(tmp_path: Path) -> None:
    """No stamp and the docketing stamp are the same defect, seen from two sides.

    A row that never got the arrival read carries the docketing date where one is
    stored and nothing where it is not, so a predicate covering only the null arm
    would repair half a class and leave the other half conditioned exactly as it
    was.
    """
    rows = [_row("scotus/1"), _row("scotus/2"), _row("scotus/3"), _row("scotus/4")]
    events = [
        _event("scotus/1", opened_at=None),  # never stamped — in
        _event("scotus/2", opened_at=_DOCKETED),  # the docketing fallback — in
        _event("scotus/3", opened_at=_SUBMITTED),  # already the arrival — out
        # An entry-pinned motion event names one specific filing rather than the
        # docket's arrival, so the derivation is the wrong reading for it.
        _event("scotus/4", opened_at=None, docket_entry_id=77),
    ]
    with _seeded(tmp_path / "corpus", rows, events) as conn:
        candidates, seen = arrival_candidates(conn)
    assert [candidate.case_id for candidate in candidates] == ["scotus/1", "scotus/2"]
    # The denominator is every baseline interim event, not the class.
    assert seen == 4


def test_a_row_outside_the_live_slice_is_never_read(tmp_path: Path) -> None:
    """The repair reads the stored live-shaped snapshot, so it frames on that channel."""
    rows = [_row("scotus/1"), _row("scotus/2", last_live_polled=None)]
    events = [_event("scotus/1"), _event("scotus/2")]
    with _seeded(tmp_path / "corpus", rows, events) as conn:
        candidates, seen = arrival_candidates(conn)
    assert [candidate.case_id for candidate in candidates] == ["scotus/1"]
    assert seen == 1


def test_the_class_is_not_predicated_on_resolution(tmp_path: Path) -> None:
    """An unresolved row with the defect is repaired too, and that is the point.

    The defect exists *because* resolution status decides which stamp a row gets
    — the poller re-polls only unresolved rows — so a repair predicated on
    resolution would condition the population on the outcome all over again. Both
    halves are in the class; re-deriving an unresolved row costs one stored-read
    and converges to what its next poll would write anyway.
    """
    rows = [_row("scotus/1"), _row("scotus/2")]
    events = [_event("scotus/1", resolved=True), _event("scotus/2", resolved=False)]
    with _seeded(tmp_path / "corpus", rows, events) as conn:
        candidates, _ = arrival_candidates(conn)
    assert [candidate.case_id for candidate in candidates] == ["scotus/1", "scotus/2"]


# --- The re-derivation --------------------------------------------------------


def test_a_missing_stamp_is_supplied_from_the_submission_entry(tmp_path: Path) -> None:
    """An unstamped interim event takes no cut at all, so what it gains is the window."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=None)],
        {_CASE: (date(2026, 7, 1), _payload(_submission(), _disposition()))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
        stored = _stored(conn)
    assert stored == _SUBMITTED
    assert result.stamped == 1 and result.moved == 0
    assert [fill.opened_at for fill in result.filled] == [_SUBMITTED]
    assert result.filled[0].previous is None
    assert result.filled[0].moved_days is None


def test_a_docketing_stamp_moves_back_to_the_arrival(tmp_path: Path) -> None:
    """The move this pass exists to make, and the histogram that reports it."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission(), _disposition()))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
        stored = _stored(conn)
    assert stored == _SUBMITTED
    assert result.moved == 1 and result.stamped == 0
    assert result.filled[0].moved_days == (_DOCKETED - _SUBMITTED).days == 5
    # Five days lands in the 4-7 bucket, and every bucket is present.
    assert result.move_histogram == {"1": 0, "2-3": 0, "4-7": 1, "8-14": 0, "15-30": 0, "31+": 0}
    assert result.move_days_max == 5
    assert list(result.move_histogram) == [label for label, _ in MOVE_BUCKETS]


def test_the_renewal_entry_is_never_read_as_the_arrival(tmp_path: Path) -> None:
    """An application refiled to a second Justice carries the filing verb.

    It is never the arrival — a disposition of the same application has already
    landed at or before it — so a payload whose head entry is missing would
    otherwise be stamped after its own first denial. The exclusion rides along
    with the parser, and this pins that it does.
    """
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        # Renewal and disposition only: no arrival is observable here.
        {_CASE: (date(2026, 7, 1), _payload(_disposition(day="Jun 15 2026"), _renewal()))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
        stored = _stored(conn)
    assert result.unparsed == 1
    assert not result.filled
    # The docketing fallback is kept, which is late — the safe way to be wrong.
    assert stored == _DOCKETED


def test_the_earliest_submission_wins(tmp_path: Path) -> None:
    """The second half of the renewal defence, for a docket carrying two anchors."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {
            _CASE: (
                date(2026, 7, 1),
                _payload(_submission(day="Jun 08 2026"), _submission(day="Jun 05 2026")),
            )
        },
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert result.filled[0].opened_at == _SUBMITTED


def test_a_stamp_that_already_equals_the_arrival_is_unchanged(tmp_path: Path) -> None:
    """An application docketed the day it was submitted reads this way and is right."""
    with _seeded(
        tmp_path / "corpus",
        [_row(date_filed=_SUBMITTED)],
        [_event(opened_at=_SUBMITTED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert result.unchanged == 1
    assert not result.filled


# --- Direction is a safety property -------------------------------------------


def test_a_stamp_that_would_move_later_is_refused_and_named(tmp_path: Path) -> None:
    """The enlarging direction, refused rather than written.

    The cut keeps everything filed strictly before the day after ``opened_at``,
    so a later stamp admits more docket than the declared moment saw — which is
    the leakage this pass exists to remove, not to introduce. Named rather than
    counted: the parser anchors on the submission entry, which precedes docketing
    on every docket sampled for the rule, so a later reading is a payload to look
    at.
    """
    later = date(2026, 6, 15)
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission(day="Jun 15 2026")))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
        stored = _stored(conn)
    assert result.later_refused == [_CASE]
    assert not result.filled
    assert stored == _DOCKETED != later


# --- The reasons a candidate yields nothing -----------------------------------


def test_a_candidate_with_no_stored_snapshot_is_counted_not_failed(tmp_path: Path) -> None:
    """Under the split the payloads live in the content store; a 404-stamped poll
    stores none, which is an unreadable corpus rather than a clean one."""
    with _seeded(tmp_path / "corpus", [_row()], [_event(opened_at=_DOCKETED)]) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert result.no_snapshot == 1
    assert not result.filled


def test_a_snapshot_disclosing_no_proceedings_is_counted_apart(tmp_path: Path) -> None:
    """Unobservable from this payload, not absent from the docket — a different fact.

    The two readings are separated by the *key*, not the entries: a payload
    carrying no `ProceedingsandOrder` at all is not live-shaped and never
    selected as the snapshot, so it lands in `no_snapshot`; one carrying the key
    with nothing in it is the live payload with its proceedings degraded.
    """
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), {"CaseNumber": _DOCKET, "ProceedingsandOrder": []})},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert result.no_proceedings == 1
    assert result.no_snapshot == 0


def test_a_payload_that_is_not_live_shaped_is_no_snapshot_at_all(tmp_path: Path) -> None:
    """A stored REST docket is the other channel's payload, not a degraded live one."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), {"docket_entries": []})},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert result.no_snapshot == 1
    assert result.no_proceedings == 0


# --- The bound and the write --------------------------------------------------


def test_the_bound_refuses_and_writes_nothing(tmp_path: Path) -> None:
    """A refusal threshold, checked after the plan and before any write."""
    rows = [_row(f"scotus/{n}") for n in range(3)]
    events = [_event(f"scotus/{n}", opened_at=_DOCKETED) for n in range(3)]
    snapshots = {f"scotus/{n}": (date(2026, 7, 1), _payload(_submission())) for n in range(3)}
    with _seeded(tmp_path / "corpus", rows, events, snapshots) as conn:
        result = backfill_arrival_stamps(conn, apply=True, max_fills=2)
        stamps = [_stored(conn, f"scotus/{n}") for n in range(3)]
    assert result.refused and not result.applied
    assert len(result.filled) == 3
    assert stamps == [_DOCKETED] * 3


def test_the_dry_run_plans_and_writes_nothing(tmp_path: Path) -> None:
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ) as conn:
        result = backfill_arrival_stamps(conn, apply=False)
        stored = _stored(conn)
    assert not result.applied
    assert [fill.opened_at for fill in result.filled] == [_SUBMITTED]
    assert stored == _DOCKETED


def test_the_apply_is_idempotent(tmp_path: Path) -> None:
    """A repaired row leaves the class, so a second dispatch plans nothing."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ) as conn:
        backfill_arrival_stamps(conn, apply=True, max_fills=5)
        again = backfill_arrival_stamps(conn, apply=True, max_fills=5)
        stored = _stored(conn)
    assert again.candidates == 0
    assert not again.filled
    assert stored == _SUBMITTED
    # And the histogram is present and zero-filled even over an empty class, so a
    # reader comparing two dispatches' ledgers reads the same keys either way.
    assert again.move_histogram == {label: 0 for label, _ in MOVE_BUCKETS}


def test_the_write_re_mirrors_the_touched_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A direct UPDATE the upsert hook never sees, so the mirror is called here.

    Provisioning reads events back through the content store, so a stale
    `events.json` would hand a cell the very stamp this pass replaced — and the
    cut would still be taken at the docketing date the repair moved off.
    """
    mirrored: list[list[str]] = []

    class _Sink:
        def mirror_events_for_cases(self, _conn: object, case_ids: list[str]) -> None:
            mirrored.append(list(case_ids))

    sink = _Sink()

    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ) as conn:
        # Patched after seeding: the seed's own upserts go through the real
        # (absent) sink, so what this records is the pass's write and only it.
        monkeypatch.setattr(corpus, "_mirror_sink", lambda: sink)
        backfill_arrival_stamps(conn, apply=True, max_fills=5)
    assert mirrored == [[_CASE]]


def test_the_histogram_buckets_every_move(tmp_path: Path) -> None:
    """Bucketed rather than averaged: the distribution is the reading that matters.

    A class that moved a median five days with a tail past a month is a different
    fact from one that moved five days uniformly, and only the second is safely
    describable as merely late — which is the judgement a retrospective interim
    cohort's conditioning turns on.
    """
    days = {0: 1, 1: 3, 2: 7, 3: 14, 4: 30, 5: 60}
    rows = [_row(f"scotus/{n}", date_filed=_SUBMITTED + timedelta(d)) for n, d in days.items()]
    events = [_event(f"scotus/{n}", opened_at=_SUBMITTED + timedelta(d)) for n, d in days.items()]
    snapshots = {f"scotus/{n}": (date(2026, 7, 1), _payload(_submission())) for n in days}
    with _seeded(tmp_path / "corpus", rows, events, snapshots) as conn:
        result = backfill_arrival_stamps(conn, apply=False)
    assert result.moved == 6
    assert result.move_histogram == {"1": 1, "2-3": 1, "4-7": 1, "8-14": 1, "15-30": 1, "31+": 1}
    assert result.move_days_max == 60


# --- The command surface ------------------------------------------------------


def _cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *args: str) -> Any:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return runner.invoke(app, ["backfill-arrival-stamps", *args])


def test_cli_refuses_an_apply_with_no_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _cli(tmp_path, monkeypatch, "--apply")
    assert result.exit_code == 2
    assert "requires an explicit --max-fills" in result.output


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _cli(tmp_path, monkeypatch)
    assert result.exit_code == 1
    assert "corpus database is missing" in result.output


def test_cli_refuses_a_blob_holding_no_interim_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A zero denominator is the wrong blob, not a converged class."""
    with _seeded(tmp_path / "corpus", [_row()], []):
        pass
    result = _cli(tmp_path, monkeypatch)
    assert result.exit_code == 1
    assert "no SCOTUS interim baseline events" in result.output


def test_cli_prints_the_move_histogram_and_the_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The histogram is the reading the apply's bound is decided against."""
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ):
        pass
    result = _cli(tmp_path, monkeypatch)
    assert result.exit_code == 0
    assert "4-7d: 1" in result.output
    assert "would stamp scotus/1" in result.output
    assert '"moved":1' in result.output
    assert set(ArrivalBackfillResult.model_fields) <= set(result.output.split('"'))


def test_cli_refuses_above_the_bound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(
        tmp_path / "corpus",
        [_row()],
        [_event(opened_at=_DOCKETED)],
        {_CASE: (date(2026, 7, 1), _payload(_submission()))},
    ):
        pass
    result = _cli(tmp_path, monkeypatch, "--apply", "--max-fills", "0")
    assert result.exit_code == 1
    assert "refusing to apply 1 stamp(s)" in result.output
