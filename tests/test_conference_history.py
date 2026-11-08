"""A petition's conference history: every DISTRIBUTED date, each classified, and its latch."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.cert_signals import (
    conference_history,
    first_relist_date,
    relist_count,
    snapshot_distribution_count,
)
from fedcourtsai.pipeline.live import ingest_live_payload
from fedcourtsai.schedule import build_schedule
from fedcourtsai.schemas import ConferenceStep, Schedule, ScheduleEntry
from fedcourtsai.supremecourt import live_docket_id

_FILED = ("Sep 02 2026", "Petition for a writ of certiorari filed. (Response due October 2, 2026)")


def _docket(*entries: tuple[str, str]) -> dict[str, Any]:
    return {"ProceedingsandOrder": [{"Date": day, "Text": text} for day, text in entries]}


def _distributed(day: str, conference: str) -> tuple[str, str]:
    return (day, f"DISTRIBUTED for Conference of {conference}.")


def _steps(payload: dict[str, Any]) -> list[tuple[date, str]]:
    history = conference_history(payload)
    assert history is not None
    return [(step.conference, step.transition) for step in history]


def test_two_relists_after_conferences_that_sat() -> None:
    payload = _docket(
        _FILED,
        _distributed("Oct 07 2026", "10/30/2026"),
        _distributed("Nov 02 2026", "11/6/2026"),
        _distributed("Nov 09 2026", "11/13/2026"),
    )
    assert _steps(payload) == [
        (date(2026, 10, 30), "first"),
        (date(2026, 11, 6), "relist"),
        (date(2026, 11, 13), "relist"),
    ]
    history = conference_history(payload)
    assert relist_count(history) == 2
    assert history is not None and history[1].distributed == date(2026, 11, 2)
    # The first relist step is the one the relist moment is dated by.
    assert first_relist_date(payload) == date(2026, 11, 2)
    assert snapshot_distribution_count(payload) == len(history)


def test_a_move_before_the_conference_sat_is_a_reschedule_not_a_relist() -> None:
    # Re-distributed before the first conference day.
    early = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        _distributed("Oct 20 2026", "11/6/2026"),
    )
    assert _steps(early)[1] == (date(2026, 11, 6), "reschedule")
    # A call for response took it off the first conference; redistributed after.
    called = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        ("Oct 15 2026", "Response Requested. (Due November 16, 2026)"),
        _distributed("Nov 24 2026", "12/12/2026"),
    )
    assert _steps(called)[1] == (date(2026, 12, 12), "reschedule")
    # A bare "Rescheduled" entry does the same.
    moved = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        ("Oct 29 2026", "Rescheduled."),
        _distributed("Nov 02 2026", "11/6/2026"),
    )
    assert _steps(moved)[1] == (date(2026, 11, 6), "reschedule")
    for payload in (early, called, moved):
        assert relist_count(conference_history(payload)) == 0
        assert first_relist_date(payload) is None


def test_a_late_redistribution_and_a_decided_docket_are_not_relists() -> None:
    held = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        _distributed("Feb 02 2027", "2/20/2027"),
    )
    assert _steps(held)[1] == (date(2027, 2, 20), "redistributed")
    decided = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        ("Nov 02 2026", "Petition DENIED."),
        _distributed("Dec 01 2026", "1/9/2027"),
    )
    assert _steps(decided)[1] == (date(2027, 1, 9), "after_decision")
    # Docketed on the conference day itself: the day cannot say whether it sat.
    same_day = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        _distributed("Oct 30 2026", "11/6/2026"),
    )
    assert _steps(same_day)[1] == (date(2026, 11, 6), "unknown")
    for payload in (held, decided, same_day):
        assert relist_count(conference_history(payload)) == 0


def test_one_step_per_distinct_conference_and_ancillary_papers_ignored() -> None:
    payload = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        _distributed("Oct 08 2026", "October 30, 2026"),  # re-docketed, same conference
        ("Oct 09 2026", "Motion to dismiss filed. DISTRIBUTED for Conference of 11/6/2026."),
        _distributed("Nov 02 2026", "11/6/2026"),
    )
    assert _steps(payload) == [(date(2026, 10, 30), "first"), (date(2026, 11, 6), "relist")]
    assert snapshot_distribution_count(payload) == 2


def test_nothing_disclosed_is_not_an_empty_history() -> None:
    assert conference_history({}) is None
    assert relist_count(None) is None
    assert conference_history(_docket(_FILED)) == []
    assert relist_count([]) == 0


def _live(*entries: tuple[str, str]) -> dict[str, Any]:
    return {
        "CaseNumber": "26-100 ",
        "DocketedDate": "September 2, 2026",
        "PetitionerTitle": "Doe, Petitioner",
        "RespondentTitle": "Roe, Respondent",
        **_docket(*entries),
    }


def test_the_live_poll_latches_the_longest_reading(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    docket_id = live_docket_id(26, 100)

    def _poll(payload: dict[str, Any]) -> corpus.CorpusRow:
        result = ingest_live_payload(db, data_root, payload, docket_id, today=date(2026, 11, 10))
        with corpus.connect(db) as conn:
            stored = corpus.get_row(conn, result.case_id)
        assert stored is not None
        return stored

    first = _distributed("Oct 07 2026", "10/30/2026")
    relist = _distributed("Nov 02 2026", "11/6/2026")
    stored = _poll(_live(_FILED))
    assert stored.conference_history == []
    stored = _poll(_live(_FILED, first, relist))
    assert stored.conference_history is not None
    assert [step.transition for step in stored.conference_history] == ["first", "relist"]
    assert stored.distribution_count == len(stored.conference_history)
    # A payload served without its proceedings, or with entries missing, keeps it.
    degraded = _live()
    del degraded["ProceedingsandOrder"]
    assert _poll(degraded).conference_history == stored.conference_history
    assert _poll(_live(_FILED, first)).conference_history == stored.conference_history
    # A writer that carries no history keeps it too.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [stored.model_copy(update={"conference_history": None})])
        kept = corpus.get_row(conn, stored.case_id)
    assert kept is not None and kept.conference_history == stored.conference_history
    # A longer reading replaces it.
    grown = _poll(_live(_FILED, first, relist, _distributed("Nov 09 2026", "11/13/2026")))
    assert grown.conference_history is not None and len(grown.conference_history) == 3


def test_the_schedule_carries_the_history_and_its_exact_relist_count(tmp_path: Path) -> None:
    history = [
        ConferenceStep(
            conference=date(2026, 10, 30), distributed=date(2026, 10, 7), transition="first"
        ),
        ConferenceStep(
            conference=date(2026, 11, 6), distributed=date(2026, 11, 2), transition="relist"
        ),
    ]
    rows = [
        corpus.CorpusRow(
            case_id="scotus/2",
            court="scotus",
            docket_number="26-1",
            distributed_for_conference=date(2026, 11, 6),
            distribution_count=2,
            conference_history=history,
        ),
        # Distributed, but its history not read since the column existed.
        corpus.CorpusRow(
            case_id="scotus/3",
            court="scotus",
            docket_number="26-2",
            distributed_for_conference=date(2026, 11, 6),
            distribution_count=1,
        ),
    ]
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    for docket in ("2", "3"):
        (data_root / "cases" / "scotus" / docket).mkdir(parents=True)
    built = build_schedule(data_root=data_root, corpus_db_path=db, as_of=date(2026, 11, 4))
    assert built.schema_version == "1.2"
    by_case = {entry.case_id: entry for entry in built.entries}
    assert by_case["scotus/2"].conferences == history
    assert by_case["scotus/2"].relists == 1
    assert by_case["scotus/3"].conferences is None and by_case["scotus/3"].relists is None


def test_relists_must_count_the_history_and_need_1_2() -> None:
    history = [
        ConferenceStep(conference=date(2026, 10, 30), transition="first"),
        ConferenceStep(conference=date(2026, 11, 6), transition="relist"),
    ]
    conference = {
        "distributed_for_conference": date(2026, 11, 6),
        "next_conference": date(2026, 11, 6),
    }
    with pytest.raises(ValueError, match="relists counts"):
        ScheduleEntry(case_id="scotus/2", conferences=history, relists=2, **conference)
    with pytest.raises(ValueError, match="relists counts"):
        ScheduleEntry(case_id="scotus/2", relists=0, **conference)
    entry = ScheduleEntry(case_id="scotus/2", conferences=history, relists=1, **conference)
    with pytest.raises(ValueError, match=r"need 1\.2"):
        Schedule(schema_version="1.1", as_of=date(2026, 11, 4), entries=[entry])


def test_an_undated_distribution_is_never_read_against() -> None:
    payload = _docket(
        _distributed("Oct 07 2026", "10/30/2026"),
        ("", "DISTRIBUTED for Conference of 11/6/2026."),
        _distributed("Nov 09 2026", "11/13/2026"),
    )
    # The third entry is read against 10/30, the dated conference before it,
    # exactly as the first-relist reader reads it.
    assert _steps(payload) == [
        (date(2026, 10, 30), "first"),
        (date(2026, 11, 6), "unknown"),
        (date(2026, 11, 13), "relist"),
    ]
    assert first_relist_date(payload) == date(2026, 11, 9)
    leading = _docket(
        ("", "DISTRIBUTED for Conference of 10/30/2026."),
        _distributed("Nov 02 2026", "11/6/2026"),
    )
    assert _steps(leading) == [(date(2026, 10, 30), "first"), (date(2026, 11, 6), "unknown")]


def test_a_twin_merge_keeps_the_longer_history() -> None:
    from fedcourtsai.dedupe import _merged_row

    one = [ConferenceStep(conference=date(2026, 10, 30), transition="first")]
    two = [*one, ConferenceStep(conference=date(2026, 11, 6), transition="relist")]

    def _twin(case_id: str, history: list[ConferenceStep] | None) -> corpus.CorpusRow:
        return corpus.CorpusRow(
            case_id=case_id, court="scotus", docket_number="26-1", conference_history=history
        )

    assert _merged_row(_twin("scotus/1", one), _twin("scotus/2", two), 1).conference_history == two
    assert _merged_row(_twin("scotus/1", two), _twin("scotus/2", None), 1).conference_history == two
