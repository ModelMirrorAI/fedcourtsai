"""The evaluate backlog deriver — what makes ``run:evaluate`` level-triggered.

The poll seams queue evaluate off *this cycle's* resolutions, and resolution
latches closed, so a failed or paused evaluate run drops those gradings with no
automatic recovery. :func:`fedcourtsai.pipeline.pull.evaluate_backlog` re-derives
them from committed ledger state (resolved event + prediction + no evaluation).
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.pipeline.pull import PullQueues, evaluate_backlog
from fedcourtsai.registry import enabled_evaluators
from fedcourtsai.schemas import EventKind
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


def _derive(tmp_path: Path, *, cap: int = 25, **kwargs: object) -> PullQueues:
    queues = PullQueues()
    evaluate_backlog(
        corpus.corpus_db_path(tmp_path / "corpus"),
        tmp_path / "data",
        EVALUATORS,
        queues,
        cap=cap,
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

    drained: set[int] = set()
    day = date(2026, 7, 20)
    for _ in range(3):  # ceil(5 / cap=2) = 3 cycles
        queues = _derive(tmp_path, cap=2, today=day)
        drained |= {int(e["docket"]) for e in queues.evaluate}
        day += timedelta(days=1)
    assert drained == {1, 2, 3, 4, 5}, "every owed case is reached within ceil(n/cap) cycles"
