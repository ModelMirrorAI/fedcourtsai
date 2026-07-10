from datetime import date
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    Disposition,
    EventKind,
    FlagCategory,
    UsageRole,
)
from fedcourtsai.store import (
    cases_due_for_pull,
    iter_flags,
    iter_tooling,
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


def test_open_events_drops_a_predict_excluded_case(tmp_path: Path) -> None:
    # A case the scope reconcile latched out of scope yields no predictable
    # events, so it leaves the predict/queueing universe at the source.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id="ca9/7", court="ca9")])
        corpus.upsert_events(conn, [_event("evt-appeal-disposition", resolved=False)])
        assert open_events(db, "ca9", 7) == ["evt-appeal-disposition"]  # in scope
        corpus.set_predict_excluded(conn, "ca9/7", True)
    assert open_events(db, "ca9", 7) == []  # latched out of scope


def test_event_queries_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert open_events(db, "ca9", 7) == []
    assert resolved_events(db, "ca9", 7) == []
    assert not db.exists()  # reading must not create the corpus as a side effect


def _write(path: Path, model: AgentFlags | AgentToolingFeedback) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json())


def test_iter_flags_spans_all_three_stages(tmp_path: Path) -> None:
    # A flags.json from each stage's layout, including reconcile's case-level path.
    ep = CasePaths(tmp_path, "ca9", 1).event("evt-motion-x")
    cp = CasePaths(tmp_path, "ca9", 1)

    def flagset(actor: str, role: UsageRole) -> AgentFlags:
        return AgentFlags(
            case_id="ca9/1",
            run_id="r1",
            role=role,
            actor_id=actor,
            flags=[AgentFlag(category=FlagCategory.scope, message="m")],
        )

    _write(ep.prediction_flags("p", "r1"), flagset("p", UsageRole.predictor))
    _write(ep.evaluation_flags("e", "r1"), flagset("e", UsageRole.evaluator))
    _write(cp.reconcile_flags("r1"), flagset("codex", UsageRole.reconciler))

    actors = {fs.actor_id for fs in iter_flags(tmp_path)}
    assert actors == {"p", "e", "codex"}


def test_iter_tooling_spans_all_three_stages(tmp_path: Path) -> None:
    ep = CasePaths(tmp_path, "ca9", 1).event("evt-motion-x")
    cp = CasePaths(tmp_path, "ca9", 1)

    def report(actor: str, role: UsageRole, used: bool) -> AgentToolingFeedback:
        return AgentToolingFeedback(
            case_id="ca9/1", run_id="r1", role=role, actor_id=actor, used_corpus_query=used
        )

    _write(ep.prediction_tooling("p", "r1"), report("p", UsageRole.predictor, used=True))
    _write(ep.evaluation_tooling("e", "r1"), report("e", UsageRole.evaluator, used=False))
    _write(cp.reconcile_tooling("r1"), report("codex", UsageRole.reconciler, used=True))

    reports = iter_tooling(tmp_path)
    assert {r.actor_id for r in reports} == {"p", "e", "codex"}
    assert sum(1 for r in reports if r.used_corpus_query) == 2


def test_iter_tooling_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert iter_tooling(tmp_path) == []  # no data/cases yet -> nothing, no creation
