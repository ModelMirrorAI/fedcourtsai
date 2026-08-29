"""The evaluate backlog deriver — what makes ``run:evaluate`` level-triggered.

The poll seams queue evaluate off *this cycle's* resolutions, and resolution
latches closed, so a failed or paused evaluate run drops those gradings with no
automatic recovery. :func:`fedcourtsai.pipeline.pull.evaluate_backlog` re-derives
them from committed ledger state (resolved event + prediction + no evaluation).
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.pull import PullQueues, derive_evaluate_backlog, evaluate_backlog
from fedcourtsai.registry import enabled_evaluators
from fedcourtsai.schemas import CellFailure, EventKind
from fedcourtsai.serialize import write_json
from tests.conftest import seed_evaluation, seed_prediction

EVALUATORS = Path("config/evaluators.yaml")


def _resolved_event(
    db: Path, court: str, docket: int, event_id: str = "evt-petition-disposition"
) -> None:
    """Record a case row and a resolved event in the corpus — a grading candidate."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id=f"{court}/{docket}", court=court)])
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event_id,
                    case_id=f"{court}/{docket}",
                    court=court,
                    kind=EventKind.petition,
                    title="Disposition of the petition",
                    resolved=True,
                )
            ],
        )


def _derive(
    tmp_path: Path, *, cap: int = 25, max_attempts: int = 0, **kwargs: object
) -> PullQueues:
    queues = PullQueues()
    evaluate_backlog(
        corpus.corpus_db_path(tmp_path / "corpus"),
        tmp_path / "data",
        EVALUATORS,
        queues,
        cap=cap,
        max_attempts=max_attempts,
        **kwargs,  # type: ignore[arg-type]
    )
    return queues


def test_the_whole_feature_a_dropped_run_re_derives_then_stops(tmp_path: Path) -> None:
    """The load-bearing test. An evaluate run is queued, dropped on the floor
    (nothing committed), re-derived on a later cycle, then — once graded — stops
    re-queuing. This is the level-trigger the whole PR exists to provide."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)

    # Cycle 1: resolved + predicted + ungraded -> the deriver owes this grading.
    first = _derive(tmp_path, today=date(2026, 7, 20))
    assert first.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}]
    assert first.evaluate_from_backlog == 1

    # The run is dropped: nothing is committed. A later cycle re-derives it.
    later = _derive(tmp_path, today=date(2026, 7, 21))
    assert later.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}]

    # Now the gradings land. The deriver goes quiet — the level has been reached.
    for ev in enabled_evaluators(EVALUATORS):
        seed_evaluation(data, "scotus", 1, event, evaluator_id=ev.id)
    done = _derive(tmp_path, today=date(2026, 7, 22))
    assert done.evaluate == []
    assert done.evaluate_from_backlog == 0


def test_only_the_missing_judges_events_are_owed(tmp_path: Path) -> None:
    """Partial coverage still counts as backlog: an event graded by one judge but
    not the others is owed, so it re-queues (the matrix gate then mints only the
    missing judges)."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)
    seed_evaluation(data, "scotus", 1, event, evaluator_id=enabled_evaluators(EVALUATORS)[0].id)

    owed = _derive(tmp_path, today=date(2026, 7, 20))
    assert owed.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}]


def test_a_resolved_event_with_no_prediction_is_not_owed(tmp_path: Path) -> None:
    """Nothing to score — the cost gate, mirrored on the deriver side so it does
    not queue a case an empty matrix would immediately close."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _resolved_event(db, "scotus", 1)  # resolved, but no prediction seeded
    assert _derive(tmp_path).evaluate == []


def test_the_daily_debounce_stops_a_same_day_re_queue(tmp_path: Path) -> None:
    """A case queued today waits for tomorrow, so an in-flight or failed run PR is
    not re-queued every cycle."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, "evt-petition-disposition")

    first = _derive(tmp_path, today=date(2026, 7, 20))
    assert first.evaluate  # queued, and the stamp is written

    same_day = _derive(tmp_path, today=date(2026, 7, 20))
    assert same_day.evaluate == [], "the daily debounce holds a same-day re-queue"

    next_day = _derive(tmp_path, today=date(2026, 7, 21))
    assert next_day.evaluate, "but it re-derives the next day if still ungraded"


def test_already_queued_by_the_poll_is_not_double_queued(tmp_path: Path) -> None:
    """The fresh-resolution path and the deriver share one queue; a case the poll
    just queued must not appear twice."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, "evt-petition-disposition")

    queues = PullQueues()
    queues.evaluate.append({"court": "scotus", "docket": 1, "events": ["evt-petition-disposition"]})
    evaluate_backlog(
        corpus.corpus_db_path(tmp_path / "corpus"),
        data,
        EVALUATORS,
        queues,
        cap=25,
        max_attempts=0,
        already_queued={"scotus/1"},
    )
    assert len(queues.evaluate) == 1
    assert queues.evaluate_from_backlog == 0


def test_a_salience_deferred_case_with_a_prediction_is_still_owed(tmp_path: Path) -> None:
    """The scope trap. `_in_predict_scope` drops a salience-deferred case, which
    is a predict *funding* decision — but a case predicted before it drifted
    below the funding line still has a prediction that must be graded. The
    deriver must not inherit that gate, or exactly those gradings strand."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    salience_score=0.01,  # scored, but far below any funding line
                    salience_version="sal-v1",
                    salience_selected=False,  # deferred: not funded for predict
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event,
                    case_id="scotus/1",
                    court="scotus",
                    kind=EventKind.petition,
                    title="Disposition of the petition",
                    resolved=True,
                )
            ],
        )
    seed_prediction(data, "scotus", 1, event)

    owed = _derive(tmp_path, today=date(2026, 7, 20))
    assert owed.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}], (
        "a deferred-but-predicted case must still be graded"
    )


def test_the_cap_bounds_the_queue_and_drains_stalest_first(tmp_path: Path) -> None:
    """The cap bounds spend/PR volume; the backlog drains across cycles, oldest
    `evaluate_queued_at` first, so nothing is starved."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    for docket in (1, 2, 3):
        _resolved_event(db, "scotus", docket)
        seed_prediction(data, "scotus", docket, event)
    # Pre-stamp docket 2 as queued longest ago, 3 more recently, 1 never.
    with corpus.connect(db) as conn:
        corpus.stamp_evaluate_queued(conn, ["scotus/2"], date(2026, 7, 1))
        corpus.stamp_evaluate_queued(conn, ["scotus/3"], date(2026, 7, 10))

    first = _derive(tmp_path, cap=2, today=date(2026, 7, 20))
    dockets = [e["docket"] for e in first.evaluate]
    # Never-queued (None) sorts first, then the stalest stamp.
    assert dockets == [1, 2], "stalest first, capped at two"

    # Next cycle picks up the one held back (3), plus 1 and 2 remain ungraded but
    # are debounced to tomorrow — so only 3 is fresh this cycle.
    second = _derive(tmp_path, cap=2, today=date(2026, 7, 20))
    assert [e["docket"] for e in second.evaluate] == [3]


def test_cap_zero_is_a_no_op(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, "evt-petition-disposition")
    assert _derive(tmp_path, cap=0).evaluate == []


def _fail_cell(
    data_root: Path, court: str, docket: int, evaluator_id: str, event_id: str, times: int
) -> None:
    """Commit `times` evaluate-seam failure facts for one cell into the ledger.

    One run-scoped `attempt.json` per distinct run, so the deriver's ledger glob
    (`cell_failure_count`) counts `times`, mirroring what the collect job writes."""
    for i in range(times):
        run_id = f"20260101T0000{i:02d}Z"
        write_json(
            CasePaths(data_root, court, docket)
            .event(event_id)
            .evaluation_attempt(evaluator_id, run_id),
            CellFailure(
                seam="evaluate",
                actor=evaluator_id,
                court=court,
                docket=docket,
                event_id=event_id,
                run_id=run_id,
                error_class="no_output",
            ),
        )


def test_a_fresh_never_attempted_cell_is_owed_under_the_cap(tmp_path: Path) -> None:
    """The baseline the cap must not disturb: a cell with no recorded attempts is
    below any positive cap, so it re-derives exactly as it would with no cap."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)

    owed = _derive(tmp_path, max_attempts=5, today=date(2026, 7, 20))
    assert owed.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}]


def test_a_cell_at_the_cap_is_not_re_derived(tmp_path: Path) -> None:
    """The poison-pill backstop. Once every evaluator's cell for the event has hit
    the attempt cap, the event is no longer owed — so a cell that fails every
    attempt cannot re-queue forever, which the daily debounce alone would allow."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)
    # Drive every enabled evaluator's cell to the cap.
    for ev in enabled_evaluators(EVALUATORS):
        _fail_cell(data, "scotus", 1, ev.id, event, times=3)

    capped = _derive(tmp_path, max_attempts=3, today=date(2026, 7, 20))
    assert capped.evaluate == [], "all cells exhausted the cap — nothing is owed"

    # The cap is the only thing holding it back: raise the ceiling and the same
    # under-cap cells are owed again (they are ungraded).
    reopened = _derive(tmp_path, max_attempts=4, today=date(2026, 7, 21))
    assert reopened.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}]


def test_the_cap_is_per_cell_a_sibling_evaluator_is_still_owed(tmp_path: Path) -> None:
    """Per-(evaluator, event) granularity: one evaluator hitting the cap must not
    suppress a sibling evaluator still owed the same event — the reason the queue
    keys the cap on cell identity rather than a coarse per-case counter."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)
    # Only the first evaluator's cell is a poison pill; the others are fresh.
    poison = enabled_evaluators(EVALUATORS)[0].id
    _fail_cell(data, "scotus", 1, poison, event, times=3)

    owed = _derive(tmp_path, max_attempts=3, today=date(2026, 7, 20))
    assert owed.evaluate == [{"court": "scotus", "docket": 1, "events": [event]}], (
        "a capped cell must not suppress a sibling evaluator still owed the event"
    )


def test_a_backlog_larger_than_the_cap_fully_drains_over_cycles(tmp_path: Path) -> None:
    """The deadlock question: with more owed cases than the cap, and the daily
    debounce holding today's queued cases, does the backlog still drain? It does,
    because a case queued today is stamped today and sorts last tomorrow, so the
    cap advances through the whole set stalest-first — nothing is starved."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    for docket in range(1, 6):  # 5 owed cases
        _resolved_event(db, "scotus", docket)
        seed_prediction(data, "scotus", docket, event)

    drained: set[object] = set()
    day = date(2026, 7, 20)
    for _ in range(3):  # ceil(5 / cap=2) = 3 cycles
        queues = _derive(tmp_path, cap=2, today=day)
        drained |= {e["docket"] for e in queues.evaluate}
        day += timedelta(days=1)
    assert drained == {1, 2, 3, 4, 5}, "every owed case is reached within ceil(n/cap) cycles"


def test_the_deriver_never_indexes_the_whole_court(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Candidates come from the resolved-event set, not from a whole-court index.

    Peak memory must scale with the work (cases holding a resolved event) rather
    than with the corpus, whose SCOTUS slice is hundreds of thousands of rows and
    only grows. `iter_rows` is the whole-court walk, so making it fatal is what
    pins the property — a fixture-sized test cannot observe the memory itself.
    """
    db = tmp_path / "corpus.db"
    _resolved_event(db, "scotus", 1)
    seed_prediction(tmp_path, "scotus", 1, "evt-petition-disposition")

    def _fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("evaluate_backlog must not walk every row in the court")

    monkeypatch.setattr(corpus, "iter_rows", _fail)
    queues = PullQueues()
    evaluate_backlog(db, tmp_path, EVALUATORS, queues, cap=25, max_attempts=5)

    assert queues.evaluate_from_backlog == 1
    assert [e["docket"] for e in queues.evaluate] == [1]


def test_a_resolved_event_whose_case_row_is_absent_is_skipped(tmp_path: Path) -> None:
    """A resolved event with no `cases` row cannot be scope-checked, so it is not a
    candidate — the row lookup replaced a dict membership test, and absence must
    stay a skip rather than becoming a crash."""
    db = tmp_path / "corpus.db"
    _resolved_event(db, "scotus", 1)
    seed_prediction(tmp_path, "scotus", 1, "evt-petition-disposition")
    with corpus.connect(db) as conn:
        conn.execute("DELETE FROM cases WHERE case_id = ?", ("scotus/1",))
        conn.commit()

    queues = PullQueues()
    evaluate_backlog(db, tmp_path, EVALUATORS, queues, cap=25, max_attempts=5)
    assert queues.evaluate_from_backlog == 0
    assert queues.evaluate == []


def test_the_deriver_reads_through_a_read_only_connection_and_stamps_nothing(
    tmp_path: Path,
) -> None:
    """`derive_evaluate_backlog` is the scan alone: it finds the owed grading and
    leaves `evaluate_queued_at` untouched. That is the contract the evaluate
    stage's own schedule depends on — it runs outside the writer jobs, so it holds
    no corpus-write credentials and could not stamp even if it wanted to."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)

    with corpus.connect_readonly(db) as conn:
        backlog = derive_evaluate_backlog(
            conn, data, EVALUATORS, cap=25, max_attempts=5, today=date(2026, 7, 20)
        )

    assert [e.as_queue_entry() for e in backlog.entries] == [
        {"court": "scotus", "docket": 1, "events": [event]}
    ]
    assert backlog.case_ids == ("scotus/1",)
    assert backlog.day == date(2026, 7, 20)
    # The stamp the pull lane would have written is absent.
    with corpus.connect_readonly(db) as conn:
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None
    assert row.evaluate_queued_at is None


def test_a_stamp_free_derivation_repeats_until_the_grading_lands(tmp_path: Path) -> None:
    """Without the debounce stamp the same backlog re-derives every cycle — and
    that is correct, not a leak. Idempotency comes from the ledger the scan reads:
    the moment the gradings are committed, the deriver goes quiet on its own."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)

    def _derive_readonly(day: date) -> tuple[str, ...]:
        with corpus.connect_readonly(db) as conn:
            return derive_evaluate_backlog(
                conn, data, EVALUATORS, cap=25, max_attempts=5, today=day
            ).case_ids

    # Same day, same cycle, twice over: no stamp means no self-debounce.
    assert _derive_readonly(date(2026, 7, 20)) == ("scotus/1",)
    assert _derive_readonly(date(2026, 7, 20)) == ("scotus/1",)

    for ev in enabled_evaluators(EVALUATORS):
        seed_evaluation(data, "scotus", 1, event, evaluator_id=ev.id)
    assert _derive_readonly(date(2026, 7, 20)) == ()


def test_a_stamp_the_pull_lane_wrote_still_holds_the_scheduled_derivation_back(
    tmp_path: Path,
) -> None:
    """The two lanes debounce against each other in the one direction that is
    possible: the scheduled scan writes no stamp, but it honours the one the pull
    lane wrote, so a case handed off this morning is not queued again tonight."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data = tmp_path / "data"
    event = "evt-petition-disposition"
    _resolved_event(db, "scotus", 1)
    seed_prediction(data, "scotus", 1, event)
    with corpus.connect(db) as conn:
        corpus.stamp_evaluate_queued(conn, ["scotus/1"], date(2026, 7, 20))

    with corpus.connect_readonly(db) as conn:
        same_day = derive_evaluate_backlog(
            conn, data, EVALUATORS, cap=25, max_attempts=5, today=date(2026, 7, 20)
        )
        next_day = derive_evaluate_backlog(
            conn, data, EVALUATORS, cap=25, max_attempts=5, today=date(2026, 7, 21)
        )

    assert same_day.case_ids == ()
    assert next_day.case_ids == ("scotus/1",)


def test_the_pull_lane_still_stamps_what_it_queued(tmp_path: Path) -> None:
    """The pull lane owns the debounce stamp: it writes `evaluate_queued_at` on
    every case it queued, which is what rotates the next cycle's stalest-first
    ordering past work already handed off."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _resolved_event(db, "scotus", 1)
    seed_prediction(tmp_path / "data", "scotus", 1, "evt-petition-disposition")

    queues = _derive(tmp_path, max_attempts=5, today=date(2026, 7, 20))

    assert queues.evaluate_from_backlog == 1
    with corpus.connect_readonly(db) as conn:
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None
    assert row.evaluate_queued_at == date(2026, 7, 20)
