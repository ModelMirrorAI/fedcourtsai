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
    Outcome,
    Stage,
    UsageRole,
)
from fedcourtsai.store import (
    cases_due_for_pull,
    forecastable_events,
    iter_flags,
    iter_tooling,
    iter_tracked_cases,
    ledger_cell_counts,
    open_events,
    resolved_events,
)
from tests.conftest import seed_prediction


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


def test_eligible_reserve_pulls_scotus_ahead_of_staler_general(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        # In scope (SCOTUS), but recently pulled — it would lose the staleness race.
        corpus.CorpusRow(case_id="scotus/1", court="scotus", last_pulled=date(2026, 6, 20)),
        # A stale eligible flag on a CoA row must NOT win it a reserve slot: the
        # reserve keys on the court predicate, not the derived column.
        corpus.CorpusRow(
            case_id="ca9/2", court="ca9", last_pulled=None, predict_eligible=True
        ),  # stalest general
        corpus.CorpusRow(case_id="ca9/3", court="ca9", last_pulled=date(2026, 6, 10)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Without the reserve, the two stalest general cases win both slots.
    assert cases_due_for_pull(db, limit=2) == [("ca9", 2), ("ca9", 3)]
    # The reserve gives one slot to the stalest SCOTUS docket; the rest stays general.
    assert cases_due_for_pull(db, limit=2, eligible_reserve=1) == [("scotus", 1), ("ca9", 2)]


def test_eligible_reserve_does_not_double_count(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        # In scope AND the stalest overall: it must be picked once, not twice.
        corpus.CorpusRow(case_id="scotus/1", court="scotus", last_pulled=None),
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


def test_forecastable_events_filters_to_case_baseline_kinds(tmp_path: Path) -> None:
    """A substantive motion event on a cert docket is tracked but never earns a
    forecast cell — its ground truth still flows through `open_events`."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id="scotus/9", court="scotus")])
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/9",
                    court="scotus",
                    kind=EventKind.petition,
                ),
                corpus.CorpusEvent(
                    event_id="evt-motion-stay-pending-appeal",
                    case_id="scotus/9",
                    court="scotus",
                    kind=EventKind.motion,
                ),
            ],
        )
    assert forecastable_events(db, "scotus", 9) == ["evt-petition-disposition"]
    # The unfiltered seam keeps serving the motion: evaluate/outcome still track it.
    assert set(open_events(db, "scotus", 9)) == {
        "evt-petition-disposition",
        "evt-motion-stay-pending-appeal",
    }


def _application_event(case_id: str, *, stage: Stage | None = Stage.interim) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id="evt-motion-disposition",
        case_id=case_id,
        court="scotus",
        kind=EventKind.motion,
        stage=stage,
    )


def test_forecastable_events_admits_the_interim_baseline_of_a_substantive_application(
    tmp_path: Path,
) -> None:
    """The interim predict path's fan-out surface: a motion-kind event carrying
    the interim stage is forecastable when its application row is in scope —
    which the row rules restrict to a substantive ask."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9525000001",
                    court="scotus",
                    docket_number="25A1",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(conn, [_application_event("scotus/9525000001")])
    assert forecastable_events(db, "scotus", 9525000001) == ["evt-motion-disposition"]


def test_forecastable_events_refuses_a_non_substantive_application(tmp_path: Path) -> None:
    """An extension's (or unparsed-ask) baseline never earns a forecast cell,
    even before the scope reconcile latches its row — the row-only rules run
    at this seam too. Its ground truth still flows through `open_events`."""
    db = corpus.corpus_db_path(tmp_path)
    for docket_id, kind in ((9525000002, "extension"), (9525000003, None)):
        case_id = f"scotus/{docket_id}"
        with corpus.connect(db) as conn:
            corpus.upsert_rows(
                conn,
                [
                    corpus.CorpusRow(
                        case_id=case_id,
                        court="scotus",
                        docket_number=f"25A{docket_id % 10}",
                        application_kind=kind,
                    )
                ],
            )
            corpus.upsert_events(conn, [_application_event(case_id)])
        assert forecastable_events(db, "scotus", docket_id) == [], kind
        assert open_events(db, "scotus", docket_id) == ["evt-motion-disposition"], kind


def test_forecastable_events_requires_the_interim_stage_on_a_motion(tmp_path: Path) -> None:
    # A stage-less motion is never admitted, whatever its row reads: the stage
    # is the standard, and admitting an unstaged motion would forecast it
    # against no declared decision rule.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9525000004",
                    court="scotus",
                    docket_number="25A4",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(conn, [_application_event("scotus/9525000004", stage=None)])
    assert forecastable_events(db, "scotus", 9525000004) == []


def test_forecastable_events_keeps_a_cert_dockets_stay_motion_out_of_the_interim_fan_out(
    tmp_path: Path,
) -> None:
    """A cert docket carries interim-stage events too — an entry-pinned stay or
    injunction motion filed on the petition's own docket — and a cert docket is
    in scope, so the stage and scope rules alone would admit one. Its cell would
    freeze the petition's salience band as its conditioning, scoring an interim
    forecast against a cert population. Only the petition baseline fans out."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9525000009",
                    court="scotus",
                    docket_number="24-1234",
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/9525000009",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
                corpus.CorpusEvent(
                    event_id="evt-motion-stay-pending-disposition",
                    case_id="scotus/9525000009",
                    court="scotus",
                    kind=EventKind.motion,
                    stage=Stage.interim,
                ),
            ],
        )
    assert forecastable_events(db, "scotus", 9525000009) == ["evt-petition-disposition"]


def test_forecastable_events_drops_a_predict_excluded_case(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow(case_id="ca9/7", court="ca9", predict_excluded=True)]
        )
        corpus.upsert_events(conn, [_event("evt-appeal-disposition", resolved=False)])
    assert forecastable_events(db, "ca9", 7) == []


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


def test_iter_flags_spans_both_stages(tmp_path: Path) -> None:
    # A flags.json from each stage's layout.
    ep = CasePaths(tmp_path, "ca9", 1).event("evt-motion-x")

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

    actors = {fs.actor_id for fs in iter_flags(tmp_path)}
    assert actors == {"p", "e"}


def test_iter_tooling_spans_both_stages(tmp_path: Path) -> None:
    ep = CasePaths(tmp_path, "ca9", 1).event("evt-motion-x")

    def report(actor: str, role: UsageRole, used: bool) -> AgentToolingFeedback:
        return AgentToolingFeedback(
            case_id="ca9/1", run_id="r1", role=role, actor_id=actor, used_corpus_query=used
        )

    _write(ep.prediction_tooling("p", "r1"), report("p", UsageRole.predictor, used=True))
    _write(ep.evaluation_tooling("e", "r1"), report("e", UsageRole.evaluator, used=False))

    reports = iter_tooling(tmp_path)
    assert {r.actor_id for r in reports} == {"p", "e"}
    assert sum(1 for r in reports if r.used_corpus_query) == 1


def test_iter_tooling_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert iter_tooling(tmp_path) == []  # no data/cases yet -> nothing, no creation


def test_ledger_cell_counts_walks_the_funnel(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    # Two predictions on one event (its outcome landed), one on another (pending).
    seed_prediction(data_root, "scotus", 1, "evt-petition-disposition", predictor_id="a")
    seed_prediction(data_root, "scotus", 1, "evt-petition-disposition", predictor_id="b")
    seed_prediction(data_root, "scotus", 2, "evt-petition-disposition", predictor_id="a")
    event_dir = data_root / "cases/scotus/1/events/evt-petition-disposition"
    outcome = Outcome(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        resolved_at=date(2026, 7, 1),
        actual_disposition=Disposition.denied,
        actual_granted=0,
    )
    (event_dir / "outcome.json").write_text(outcome.model_dump_json())

    assert ledger_cell_counts(data_root) == (3, 2, 1)


def test_ledger_cell_counts_empty_ledger_is_zero(tmp_path: Path) -> None:
    assert ledger_cell_counts(tmp_path / "data") == (0, 0, 0)
