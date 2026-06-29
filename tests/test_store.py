from datetime import date
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition, EventKind
from fedcourtsai.store import (
    cases_due_for_pull,
    cases_with_predictions,
    iter_tracked_cases,
    open_events,
    resolved_events,
)


def _event(event_id: str, *, resolved: bool) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id="ca9/7",
        court="ca9",
        kind=EventKind.appeal,
        resolved=resolved,
    )


def test_iter_tracked_cases_reads_from_corpus(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/2", court="ca9"),
        corpus.CorpusRow(case_id="ca1/10", court="ca1"),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Sorted by case_id, parsed back into (court, docket) pairs.
    assert iter_tracked_cases(db) == [("ca1", 10), ("ca9", 2)]


def test_iter_tracked_cases_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert iter_tracked_cases(db) == []
    assert not db.exists()  # reading must not create the corpus as a side effect


def _predictions_dir(data_root: Path, court: str, docket: int, event: str) -> Path:
    d = data_root / "cases" / court / str(docket) / "events" / event / "predictions"
    d.mkdir(parents=True)
    return d


def test_cases_with_predictions_groups_by_case(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    a1 = _predictions_dir(data_root, "scotus", 801, "evt-petition-disposition")
    a2 = _predictions_dir(data_root, "scotus", 801, "evt-merits-disposition")
    b1 = _predictions_dir(data_root, "ca9", 102, "evt-appeal-disposition")
    # event.yaml beside the predictions and an outcome-only event are not predictions.
    (a1.parent / "event.yaml").write_text("kind: petition\n")
    (data_root / "cases" / "ca9" / "102" / "events" / "evt-other").mkdir(parents=True)
    grouped = cases_with_predictions(data_root)
    assert grouped == {"scotus/801": [a2, a1], "ca9/102": [b1]}


def test_cases_with_predictions_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert cases_with_predictions(tmp_path / "data") == {}


def test_cases_due_for_pull_rotates_stalest_first_and_caps(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/1", court="ca9", last_pulled=date(2026, 6, 20)),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=None),  # stalest
        corpus.CorpusRow(case_id="ca1/3", court="ca1", last_pulled=date(2026, 6, 10)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Never-pulled first, then oldest stamp; capped at the per-run limit.
    assert cases_due_for_pull(db, limit=2) == [("ca9", 2), ("ca1", 3)]


def test_cases_due_for_pull_skips_closed(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/1", court="ca9"),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", disposition=Disposition.denied),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    assert cases_due_for_pull(db, limit=10) == [("ca9", 1)]


def test_cases_due_for_pull_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert cases_due_for_pull(db, limit=10) == []
    assert not db.exists()  # reading must not create the corpus as a side effect


def test_eligible_reserve_pulls_eligible_ahead_of_staler_general(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        # Eligible, but recently pulled — it would lose the normal staleness race.
        corpus.CorpusRow(
            case_id="scotus/1", court="scotus", last_pulled=date(2026, 6, 20), predict_eligible=True
        ),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=None),  # stalest general
        corpus.CorpusRow(case_id="ca9/3", court="ca9", last_pulled=date(2026, 6, 10)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Without the reserve, the two stalest general cases win both slots.
    assert cases_due_for_pull(db, limit=2) == [("ca9", 2), ("ca9", 3)]
    # The reserve gives one slot to the stalest eligible case; the rest stays general.
    assert cases_due_for_pull(db, limit=2, eligible_reserve=1) == [("scotus", 1), ("ca9", 2)]


def test_eligible_reserve_does_not_double_count(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        # Eligible AND the stalest overall: it must be picked once, not twice.
        corpus.CorpusRow(
            case_id="scotus/1", court="scotus", last_pulled=None, predict_eligible=True
        ),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=date(2026, 6, 10)),
        corpus.CorpusRow(case_id="ca9/3", court="ca9", last_pulled=date(2026, 6, 20)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    due = cases_due_for_pull(db, limit=2, eligible_reserve=1)
    assert due == [("scotus", 1), ("ca9", 2)]
    assert len(due) == len(set(due))  # the general fill skips the reserved case


def test_eligible_reserve_unfilled_falls_through_to_general(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/1", court="ca9", last_pulled=None),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=date(2026, 6, 10)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # No eligible cases exist, so the reserve wastes nothing — the full budget is
    # still spent on the general rotation.
    assert cases_due_for_pull(db, limit=2, eligible_reserve=2) == [("ca9", 1), ("ca9", 2)]


def test_eligible_reserve_respects_skip_closed(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        # Eligible but resolved: skip_closed must exclude it from the reserve too.
        corpus.CorpusRow(
            case_id="scotus/1",
            court="scotus",
            predict_eligible=True,
            disposition=Disposition.denied,
        ),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    assert cases_due_for_pull(db, limit=2, eligible_reserve=1) == [("ca9", 2)]


def test_open_and_resolved_events_partition_corpus_events(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                _event("evt-appeal-disposition", resolved=False),
                _event("evt-motion-stay", resolved=True),
            ],
        )
    # The corpus resolved flag is the single source of truth for event state.
    assert open_events(db, "ca9", 7) == ["evt-appeal-disposition"]
    assert resolved_events(db, "ca9", 7) == ["evt-motion-stay"]


def test_event_queries_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert open_events(db, "ca9", 7) == []
    assert resolved_events(db, "ca9", 7) == []
    assert not db.exists()  # reading must not create the corpus as a side effect
