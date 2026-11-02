import dataclasses
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from fedcourtsai import corpus, process_version
from fedcourtsai.config import load_pull_config
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline import moments as moments_module
from fedcourtsai.pipeline.pull import _reopenable_moment
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    Disposition,
    EventKind,
    FlagCategory,
    Judgment,
    MeritsTermination,
    ModelUsage,
    Moment,
    Outcome,
    Prediction,
    ProcessVersion,
    Stage,
    UsageRole,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.store import (
    UNDECLARED_STAGE,
    CellCensusRow,
    cases_due_for_pull,
    distribution_conference_considered,
    event_has_claimable_prediction,
    event_recorded_closed,
    forecastable_event_ids,
    forecastable_events,
    forward_refusal_reason,
    iter_flags,
    iter_predictions,
    iter_tooling,
    iter_tracked_cases,
    ledger_cell_counts,
    live_payload_reader,
    normalized_stage,
    open_events,
    petition_distributed,
    recent_cell_census,
    resolved_events,
    unforecastable_listed_events,
)
from tests.conftest import bless_process, frozen_stamp, open_freeze_window, seed_prediction


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


def test_committed_pull_config_spends_every_slot_on_scotus(tmp_path: Path) -> None:
    # A refresh pages every docket entry, so one never-pulled bulk circuit docket
    # with hundreds of entry pages takes a whole window's hourly budget and never
    # completes. The committed reserve must cover the whole cap, so while the
    # SCOTUS-open pool can fill a run no general slot reaches such a docket.
    cfg = load_pull_config(Path(__file__).resolve().parents[1] / "config")
    assert cfg.eligible_refresh_reserve >= cfg.max_cases_per_run
    db = corpus.corpus_db_path(tmp_path)
    rows = [corpus.CorpusRow(case_id="ca1/10249", court="ca1", last_pulled=None)] + [
        corpus.CorpusRow(case_id=f"scotus/{n}", court="scotus", last_pulled=date(2026, 6, 20))
        for n in range(1, cfg.max_cases_per_run + 1)
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    due = cases_due_for_pull(
        db,
        limit=cfg.max_cases_per_run,
        skip_closed=cfg.skip_closed,
        eligible_reserve=cfg.eligible_refresh_reserve,
    )
    assert len(due) == cfg.max_cases_per_run
    assert {court for court, _ in due} == {"scotus"}


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


def _stale_grant_db(tmp_path: Path, granted: date) -> Path:
    """A corpus holding one granted SCOTUS row and its resolved cert event."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9",
                    court="scotus",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                    date_cert_granted=granted,
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-cert",
                    case_id="scotus/9",
                    court="scotus",
                    kind=EventKind.petition,
                    resolved=True,
                )
            ],
        )
    return db


def test_unforecastable_listed_events_names_both_refusal_classes(tmp_path: Path) -> None:
    # What a replayed trigger listing is re-checked against: the event the
    # corpus resolved since queueing, and every merits moment of a proceeding
    # whose grant went stale unparsed — the second stated from the row alone,
    # so a moment absent from the events table is refused too.
    db = _stale_grant_db(tmp_path, date(2020, 1, 6))
    reasons = unforecastable_listed_events(db, "scotus", 9, today=date(2024, 1, 6))
    assert "resolved" in reasons["evt-petition-cert"]
    merits = [spec.event_id for spec in moments.moments_for(Stage.merits)]
    assert set(merits) <= set(reasons)
    assert all("cert grant is more than" in reasons[event_id] for event_id in merits)


def test_unforecastable_listed_events_keeps_a_fresh_grants_merits_moments(tmp_path: Path) -> None:
    # Inside the bound the proceeding is pending, so only the resolved class fires.
    today = date(2024, 1, 6)
    db = _stale_grant_db(tmp_path, today - timedelta(days=30))
    reasons = unforecastable_listed_events(db, "scotus", 9, today=today)
    assert set(reasons) == {"evt-petition-cert"}


def test_unforecastable_listed_events_resolved_reason_wins_on_a_stale_rows_moment(
    tmp_path: Path,
) -> None:
    # The documented precedence, pinned: a merits moment that is both resolved
    # and a moment of a stale proceeding keeps the resolved attribution — it is
    # the reason that says what to do next (grade it).
    db = _stale_grant_db(tmp_path, date(2020, 1, 6))
    merits = [spec.event_id for spec in moments.moments_for(Stage.merits)]
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=merits[0],
                    case_id="scotus/9",
                    court="scotus",
                    kind=EventKind.order,
                    resolved=True,
                )
            ],
        )
    reasons = unforecastable_listed_events(db, "scotus", 9, today=date(2024, 1, 6))
    assert "resolved" in reasons[merits[0]]
    assert all("cert grant is more than" in reasons[event_id] for event_id in merits[1:])


def test_unforecastable_listed_events_refuses_a_latched_judgment_and_a_gvr_row(
    tmp_path: Path,
) -> None:
    # The other row arms of the selection predicate, read back at the plan
    # seam: a latched judgment (decided while the event waits for triage) and a
    # grant re-resolved so it no longer opens a merits proceeding. Neither has
    # a later backstop for the listing path.
    today = date(2024, 1, 6)
    merits = [spec.event_id for spec in moments.moments_for(Stage.merits)]
    latched = corpus.corpus_db_path(tmp_path / "latched")
    with corpus.connect(latched) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9",
                    court="scotus",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                    date_cert_granted=today - timedelta(days=30),
                    merits_judgment=Judgment.affirmed,
                )
            ],
        )
    reasons = unforecastable_listed_events(latched, "scotus", 9, today=today)
    assert all("already carries its merits outcome" in reasons[event_id] for event_id in merits)

    gvr = corpus.corpus_db_path(tmp_path / "gvr")
    with corpus.connect(gvr) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9",
                    court="scotus",
                    docket_number="24-100",
                    disposition=Disposition.gvr,
                    date_cert_granted=today - timedelta(days=30),
                )
            ],
        )
    reasons = unforecastable_listed_events(gvr, "scotus", 9, today=today)
    assert all("no longer opens a merits proceeding" in reasons[event_id] for event_id in merits)


def test_forecastable_events_filters_to_case_baseline_kinds(tmp_path: Path) -> None:
    """A substantive motion event on a cert docket is tracked but never earns a
    forecast cell — its ground truth still flows through `open_events`."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9",
                    court="scotus",
                    # Distributed: the baseline's own moment precondition.
                    distribution_count=1,
                )
            ],
        )
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


def _cvsg_case(
    db: Path,
    docket_id: int,
    *,
    disposition: Disposition | None = None,
    docket_number: str = "24-1234",
    stage: Stage | None = Stage.cert,
    distribution_count: int | None = 1,
) -> None:
    """A SCOTUS petition whose CVSG order has been minted beside its baseline.

    ``distribution_count`` defaults to distributed — the baseline's
    distribution moment has occurred, so its cell may mint (the arrival
    moment owns the pre-distribution forecast). Pass ``None`` for the
    unparsed-distribution shape the corpus really holds: a CVSG latched on a
    row with no distribution signal at all.
    """
    case_id = f"scotus/{docket_id}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=docket_number,
                    disposition=disposition,
                    cvsg_date=date(2025, 3, 3),
                    distribution_count=distribution_count,
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    resolved=disposition is not None,
                ),
                corpus.CorpusEvent(
                    event_id="evt-order-cvsg-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=stage,
                ),
            ],
        )


def test_forecastable_events_fans_out_the_cvsg_event(tmp_path: Path) -> None:
    """The cert admission: a minted CVSG order earns its re-forecast cell.

    The later cert moment's fan-out surface — an order-kind, cert-stage event
    on a still-pending petition — alongside the baseline the case-kind arm
    already admits. Neither of the other stage arms reaches it (interim is
    keyed on a motion, merits on the merits stage), so this arm is what puts
    the budgeted CVSG cells in front of a predictor at all.
    """
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 21)

    assert set(forecastable_events(db, "scotus", 21)) == {
        "evt-petition-disposition",
        "evt-order-cvsg-disposition",
    }


def test_forecastable_events_refuses_a_cvsg_event_on_a_decided_row(tmp_path: Path) -> None:
    # A disposition latched while the CVSG event still awaits its outcome
    # record (the unrecorded-triage shape) must not mint a cell per predictor,
    # per day, that provisioning then refuses — same guard the merits arm
    # keys on its latched judgment. Ground truth still flows via open_events.
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 22, disposition=Disposition.denied)

    assert forecastable_events(db, "scotus", 22) == []
    assert open_events(db, "scotus", 22) == ["evt-order-cvsg-disposition"]


def test_forecastable_events_refuses_a_cvsg_event_out_of_predict_scope(tmp_path: Path) -> None:
    # An IFP docket serial is a documented predict-scope exclusion: its CVSG
    # cell is refused by the row rules at this seam, while its baseline rides
    # the case-kind arm until the scope reconcile latches the row out.
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 23, docket_number="24-5001")

    assert forecastable_events(db, "scotus", 23) == ["evt-petition-disposition"]


def test_forecastable_events_requires_the_cert_stage_on_the_cvsg_order(tmp_path: Path) -> None:
    # A stage-less order is never admitted, here as on the merits arm: the
    # stage is the decision standard, and the register check reads the stamp,
    # not the id.
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 24, stage=None)

    assert forecastable_events(db, "scotus", 24) == ["evt-petition-disposition"]


def test_forecastable_events_admits_a_cvsg_order_before_any_distribution(tmp_path: Path) -> None:
    # The premature-distribution refusal is the distribution moment's alone: a
    # CVSG latched on a row with no distribution signal (the
    # unparsed-distribution backlog shape) keeps its cell, while the baseline
    # beside it stays refused. Pins the refusal against widening to another
    # cert moment.
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 25, distribution_count=None)

    assert forecastable_events(db, "scotus", 25) == ["evt-order-cvsg-disposition"]


def test_forecastable_events_refuses_a_predistribution_baseline_through_every_arm(
    tmp_path: Path,
) -> None:
    """A zero-distribution petition baseline is refused by the whole or-chain.

    The distribution moment has not happened, so no arm may admit its cell —
    asserted on :func:`forecastable_events` rather than either predicate in
    isolation, because the admission is an or-chain and a refusal one arm
    applies alone is re-admitted by the other. (The cert-stage arm reaches
    the baseline too: it is a declared cert-stage event of a pending
    petition.)
    """
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/26",
                    court="scotus",
                    docket_number="24-2600",
                    # Undistributed: no conference distribution has occurred.
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/26",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                )
            ],
        )

    assert forecastable_events(db, "scotus", 26) == []


def test_forecastable_events_refuses_a_stale_unparsed_grant(tmp_path: Path) -> None:
    """A grant two Terms past with neither judgment nor termination latched is
    a decided docket the record never resolved, not a pending case — the
    merits analogue of the petition stage's stale-Term refusal. The first
    post-freeze fan-out spent ~25 events' cells on exactly this class; the
    class is the same population `validate`'s no_stale_unparsed_grants check
    reports, so a row the check turns red can never also earn a cell."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _granted_case(db, 83, disposition=Disposition.granted)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/83",
                    court="scotus",
                    docket_number="24-1234",
                    disposition=Disposition.granted,
                    # Far past the 730-day bound relative to any present run.
                    date_cert_granted=date(2019, 2, 4),
                )
            ],
        )

    assert "evt-order-judgment" not in forecastable_events(db, "scotus", 83)
    # The helper's 180-day-old grant stays admitted — the refusal is
    # the staleness, not the stage.
    db2 = corpus.corpus_db_path(tmp_path / "corpus2")
    _granted_case(db2, 84, disposition=Disposition.granted)
    assert "evt-order-judgment" in forecastable_events(db2, "scotus", 84)


def test_forecastable_events_admits_the_arrival_moment_before_any_distribution(
    tmp_path: Path,
) -> None:
    # The arrival event is petition-kind too, and it is defined at zero
    # distributions — the docketing-time information set is its whole point —
    # so the shared premature-distribution refusal must key on the declared
    # moment, never the kind. The baseline beside it stays refused.
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/27",
                    court="scotus",
                    docket_number="24-2700",
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/27",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
                corpus.CorpusEvent(
                    event_id="evt-petition-arrival-disposition",
                    case_id="scotus/27",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
            ],
        )

    assert forecastable_events(db, "scotus", 27) == ["evt-petition-arrival-disposition"]


def test_forecastable_events_keeps_an_application_row_out_of_the_cert_arm(
    tmp_path: Path,
) -> None:
    # The pin behind the arm's superset claim: an application-form row whose
    # events wear cert-shaped ids and stamps is refused by the cert arm's form
    # check exactly as the case-baseline arm refuses its mislabeled baseline —
    # the new arm opens no side door around that refusal.
    db = corpus.corpus_db_path(tmp_path)
    case_id = "scotus/9525000010"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="25A10",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
                corpus.CorpusEvent(
                    event_id="evt-order-cvsg-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.cert,
                ),
            ],
        )

    assert forecastable_events(db, "scotus", 9525000010) == []


def test_forecastable_events_honors_a_switched_off_moment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A declared moment with ``forecastable=False`` earns no cell anywhere.

    The register's documented off-switch: a moment can stay declared, parsed,
    and latched — its events minted, its ground truth tracked — while the
    fan-out refuses it, because `_declares_forecastable` reads the flag off the
    spec. This is the one dial an issue-class "does a moment earn its cells"
    decision turns, so pin that turning it actually empties the fan-out rather
    than merely re-labelling it.
    """
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 25)
    spec = moments.spec_for("evt-order-cvsg-disposition")
    assert spec is not None and spec.forecastable
    switched_off = dataclasses.replace(spec, forecastable=False)
    real_spec_for = moments.spec_for
    monkeypatch.setattr(
        moments,
        "spec_for",
        lambda event_id: (
            switched_off if event_id == switched_off.event_id else real_spec_for(event_id)
        ),
    )

    # The CVSG cell drops out of the fan-out; the baseline (admitted by the
    # case-kind arm, which never consults the register) and the unfiltered
    # ground-truth seam are untouched.
    assert forecastable_events(db, "scotus", 25) == ["evt-petition-disposition"]
    assert set(open_events(db, "scotus", 25)) == {
        "evt-petition-disposition",
        "evt-order-cvsg-disposition",
    }


def _granted_case(
    db: Path,
    docket_id: int,
    *,
    disposition: Disposition,
    stage: Stage | None = Stage.merits,
    docket_number: str = "24-1234",
    merits_judgment: Judgment | None = None,
    merits_terminated: MeritsTermination | None = None,
) -> None:
    """A granted SCOTUS docket with its resolved cert baseline and merits event."""
    case_id = f"scotus/{docket_id}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=docket_number,
                    disposition=disposition,
                    # Relative, not fixed: a fresh grant must stay inside the
                    # stale-grant bound whatever today is, or every merits
                    # test here starts failing two Terms after the date was
                    # typed.
                    date_cert_granted=date.today() - timedelta(days=180),
                    merits_judgment=merits_judgment,
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    resolved=True,
                ),
                corpus.CorpusEvent(
                    event_id="evt-order-judgment",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=stage,
                ),
            ],
        )
        if merits_terminated is not None:
            # Owned by the judgment sweep, not by an ingestion upsert.
            corpus.set_merits_termination(conn, case_id, merits_terminated)


def test_forecastable_events_fans_out_the_merits_event(tmp_path: Path) -> None:
    """The merits admission: the minted merits event earns a forecast cell.

    The order-kind, merits-stage event a cert grant mints is the merits path's
    fan-out surface, so a granted docket queues its merits cell the way an
    application docket queues its interim one. Neither of the other admissions
    reaches it — the case-baseline path is keyed on the petition/appeal kinds
    and the interim path on a motion — so this arm is load-bearing on its own.
    """
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 11, disposition=Disposition.granted)

    assert forecastable_events(db, "scotus", 11) == ["evt-order-judgment"]
    assert open_events(db, "scotus", 11) == ["evt-order-judgment"]


def test_forecastable_events_refuses_a_merits_event_on_a_cert_order_grant(
    tmp_path: Path,
) -> None:
    """A GVR's judgment rides in the cert order, so it earns no merits cell.

    The row predicate, not the event, decides: `opens_merits_proceeding` is the
    rule that mints the event *and* the population the statpack merits section
    measures its disturbed rate over, so re-checking it here keeps the forecast
    population and the baseline population one population where a re-resolved
    docket leaves a stale merits event behind. Its ground truth still flows
    through `open_events`.
    """
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 12, disposition=Disposition.gvr)

    assert forecastable_events(db, "scotus", 12) == []
    assert open_events(db, "scotus", 12) == ["evt-order-judgment"]


def test_forecastable_events_refuses_a_merits_event_out_of_predict_scope(
    tmp_path: Path,
) -> None:
    # A date-inconsistent row opens a merits proceeding like any other grant,
    # so the scope rules, not the merits predicate, are what keep its cell out.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 14, disposition=Disposition.granted)
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET date_filed = '2025-06-01', date_decided = '2025-01-01' "
            + "WHERE case_id = 'scotus/14'"
        )
        conn.commit()
        row = corpus.get_row(conn, "scotus/14")
    assert row is not None
    assert corpus.is_date_inconsistent(row)

    assert forecastable_events(db, "scotus", 14) == []
    assert open_events(db, "scotus", 14) == ["evt-order-judgment"]


def test_forecastable_events_admits_the_merits_event_of_an_ifp_grant(tmp_path: Path) -> None:
    # The IFP scope rule is a cert-stage funding decision and stops at the
    # grant: a granted IFP docket's merits events are forecast like a paid
    # grant's, while its resolved petition owes no cert cell.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 18, disposition=Disposition.granted, docket_number="24-5001")
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_briefed_event("scotus/18")])

    assert set(forecastable_events(db, "scotus", 18)) == {
        "evt-order-judgment",
        "evt-brief-judgment",
    }


def test_forecastable_events_refuses_the_merits_event_of_an_ifp_gvr(tmp_path: Path) -> None:
    # A GVR opens no merits proceeding, so the IFP rule still holds on it.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 19, disposition=Disposition.gvr, docket_number="24-5002")

    assert forecastable_events(db, "scotus", 19) == []
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/19")
    assert row is not None
    assert corpus.out_of_scope_reason(row) == (
        "in-forma-pauperis petition — a documented predict-scope exclusion"
    )


def test_forecastable_events_refuses_a_merits_event_whose_judgment_is_latched(
    tmp_path: Path,
) -> None:
    # A parsed judgment whose entry carries no usable date surfaces for triage
    # rather than resolving the event, so the row reads decided while the event
    # stays open. No cell: it would only be refused at provisioning, daily.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 15, disposition=Disposition.granted, merits_judgment=Judgment.reversed)

    assert forecastable_events(db, "scotus", 15) == []
    assert open_events(db, "scotus", 15) == ["evt-order-judgment"]


def test_forecastable_events_refuses_a_terminated_merits_proceeding(tmp_path: Path) -> None:
    # A post-grant Rule 46 dismissal ends the case with no disposition, so no
    # judgment will ever latch. Without the terminated arm the event stays
    # forecastable forever, and on a long-decided docket that is a forward cell
    # on a case whose answer is already public.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(
        db,
        16,
        disposition=Disposition.granted,
        merits_terminated=MeritsTermination.voluntary_dismissal,
    )

    assert forecastable_events(db, "scotus", 16) == []
    assert open_events(db, "scotus", 16) == ["evt-order-judgment"]


def test_forecastable_events_requires_the_merits_stage_on_an_order(tmp_path: Path) -> None:
    # A stage-less order is never admitted: the stage is the decision standard,
    # and an order event of any other sort — the kind carries no stage at all —
    # would be forecast against no declared rule. Same shape as the motion path.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 13, disposition=Disposition.granted, stage=None)

    assert forecastable_events(db, "scotus", 13) == []
    assert open_events(db, "scotus", 13) == ["evt-order-judgment"]


def _briefed_event(case_id: str) -> corpus.CorpusEvent:
    """The merits stage's second moment, minted once both sides have briefed."""
    return corpus.CorpusEvent(
        event_id="evt-brief-judgment",
        case_id=case_id,
        court="scotus",
        kind=EventKind.brief,
        stage=Stage.merits,
    )


def test_forecastable_events_fans_out_the_briefed_merits_event(tmp_path: Path) -> None:
    """The merits admission carries the briefed moment too: a brief-kind event
    at the merits stage is admitted through the same `_merits_forecastable`
    arm as the grant-moment order, because the arm reads the register's
    kind/stage pair rather than hard-coding the order kind — so the later
    moment's cells reach a predictor without a second admission existing
    anywhere."""
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 16, disposition=Disposition.granted)
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_briefed_event("scotus/16")])

    assert set(forecastable_events(db, "scotus", 16)) == {
        "evt-order-judgment",
        "evt-brief-judgment",
    }


def test_forecastable_events_refuses_a_briefed_merits_event_on_a_cert_order_grant(
    tmp_path: Path,
) -> None:
    # The refusal mirror: the briefed moment rides the same row predicate as
    # the grant moment, so a GVR — whose judgment is a cert-stage fact — earns
    # neither merits cell, while both events' ground truth stays tracked.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 17, disposition=Disposition.gvr)
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_briefed_event("scotus/17")])

    assert forecastable_events(db, "scotus", 17) == []
    assert set(open_events(db, "scotus", 17)) == {
        "evt-order-judgment",
        "evt-brief-judgment",
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


def _response_events(case_id: str) -> list[corpus.CorpusEvent]:
    """The interim stage's later moments: response requested, response filed."""
    return [
        corpus.CorpusEvent(
            event_id="evt-order-response-requested-disposition",
            case_id=case_id,
            court="scotus",
            kind=EventKind.order,
            stage=Stage.interim,
        ),
        corpus.CorpusEvent(
            event_id="evt-brief-response-disposition",
            case_id=case_id,
            court="scotus",
            kind=EventKind.brief,
            stage=Stage.interim,
        ),
    ]


def test_forecastable_events_fans_out_the_interim_response_moments(tmp_path: Path) -> None:
    """The interim admission carries the later response moments too: the
    order-kind requested event and the brief-kind filed event ride the same
    `_interim_forecastable` arm as the motion baseline, because the arm reads
    the register's kind/stage pair rather than hard-coding the motion kind —
    so a substantive application fans out every declared interim moment."""
    db = corpus.corpus_db_path(tmp_path)
    case_id = "scotus/9525000005"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="25A5",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(conn, [_application_event(case_id), *_response_events(case_id)])

    assert set(forecastable_events(db, "scotus", 9525000005)) == {
        "evt-motion-disposition",
        "evt-order-response-requested-disposition",
        "evt-brief-response-disposition",
    }


def test_forecastable_events_refuses_the_response_moments_of_a_non_substantive_application(
    tmp_path: Path,
) -> None:
    # The refusal mirror: the response moments ride the same row-only scope
    # rules as the baseline, so an extension application earns none of the
    # three interim cells — while every event's ground truth stays tracked.
    db = corpus.corpus_db_path(tmp_path)
    case_id = "scotus/9525000006"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="25A6",
                    application_kind="extension",
                )
            ],
        )
        corpus.upsert_events(conn, [_application_event(case_id), *_response_events(case_id)])

    assert forecastable_events(db, "scotus", 9525000006) == []
    assert set(open_events(db, "scotus", 9525000006)) == {
        "evt-motion-disposition",
        "evt-order-response-requested-disposition",
        "evt-brief-response-disposition",
    }


def test_every_declared_forecastable_moment_is_admitted_somewhere(tmp_path: Path) -> None:
    """Denominator invariant: each ``forecastable=True`` moment in the register
    has an admission path through ``forecastable_events``.

    The per-arm tests above prove each admission on its own; nothing couples
    the *register* to them, so a new declared moment — or a kind/stage edit to
    an existing one — can arrive with no arm reaching it, and the fan-out
    simply never mints its cells while `predict-matrix` reports an empty
    matrix as in-scope work correctly done. Three corpus shapes, one per
    stage, must jointly admit every declared forecastable event; extending the
    register obliges extending a shape until this passes again.
    """
    db = corpus.corpus_db_path(tmp_path)
    _cvsg_case(db, 81)
    _granted_case(db, 82, disposition=Disposition.granted)
    interim_case = "scotus/9525000081"
    with corpus.connect(db) as conn:
        # The sal-v2 arrival moment, minted beside case 81's baseline: the
        # generic cert arm admits any declared cert moment of a pending
        # petition, which is exactly what this invariant obliges a shape for.
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-arrival-disposition",
                    case_id="scotus/81",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                )
            ],
        )
        # The sg-brief, first-relist and call-for-response moments, minted on
        # the same pending petition: the generic cert arm admits them as it does
        # the arrival one.
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event_id,
                    case_id="scotus/81",
                    court="scotus",
                    kind=kind,
                    stage=Stage.cert,
                    opened_at=date(2025, 3, 3),
                )
                for event_id, kind in (
                    ("evt-brief-sg-disposition", EventKind.brief),
                    ("evt-order-relist-disposition", EventKind.order),
                    ("evt-order-call-for-response-disposition", EventKind.order),
                )
            ],
        )
        # All three are bounded by the next conference, read off the live
        # payload: the relist entry names a conference still ahead, so all stay
        # open.
        corpus.upsert_snapshot(
            conn,
            "scotus/81",
            date(2025, 3, 4),
            {
                "ProceedingsandOrder": [
                    {"Date": "Mar 03 2025", "Text": "DISTRIBUTED for Conference of 1/5/2099."}
                ]
            },
        )
        corpus.upsert_events(
            conn,
            [
                _briefed_event("scotus/82"),
                corpus.CorpusEvent(
                    event_id="evt-argument-judgment",
                    case_id="scotus/82",
                    court="scotus",
                    kind=EventKind.argument,
                    stage=Stage.merits,
                ),
            ],
        )
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=interim_case,
                    court="scotus",
                    docket_number="25A81",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(
            conn, [_application_event(interim_case), *_response_events(interim_case)]
        )

    admitted = (
        set(forecastable_events(db, "scotus", 81))
        | set(forecastable_events(db, "scotus", 82))
        | set(forecastable_events(db, "scotus", 9525000081))
    )
    declared = {spec.event_id for spec in moments.DECLARED_MOMENTS if spec.forecastable}
    assert declared, "the register declares no forecastable moment — the invariant is vacuous"
    assert declared <= admitted, (
        f"declared forecastable moment(s) no fixture shape admits: {sorted(declared - admitted)}"
    )


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
                    # Distributed: the baseline's own moment precondition.
                    distribution_count=1,
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


def test_forecastable_events_refuses_an_application_dockets_cert_shaped_baseline(
    tmp_path: Path,
) -> None:
    """An application docket whose baseline still reads petition-kind carries a
    mislabel, not a cert petition. Admitting it on the strength of the kind would
    forecast a stay application under the cert contract — so forecastability is
    correct on its own terms, not conditional on the relabel pass having run."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9525000010",
                    court="scotus",
                    docket_number="25A99",
                    application_kind="substantive",
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/9525000010",
                    court="scotus",
                    kind=EventKind.petition,
                    stage=None,
                )
            ],
        )
    assert forecastable_events(db, "scotus", 9525000010) == []


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


def test_ledger_cell_counts_reads_the_scotus_population_only(tmp_path: Path) -> None:
    # The funnel sits beside SCOTUS-only stratified cells, so a prediction
    # slice's cell must not swell its census.
    data_root = tmp_path / "data"
    seed_prediction(data_root, "scotus", 1, "evt-petition-disposition", predictor_id="a")
    seed_prediction(data_root, "cand", 101, "evt-motion-dismiss", predictor_id="a")
    assert ledger_cell_counts(data_root) == (1, 1, 0)


def test_ledger_cell_counts_empty_ledger_is_zero(tmp_path: Path) -> None:
    assert ledger_cell_counts(tmp_path / "data") == (0, 0, 0)


def test_the_arrival_moment_obeys_the_register_not_the_baseline_arm(tmp_path: Path) -> None:
    """A declared later moment sharing the baseline's kind defers to its
    stage arm: a decided-but-unrecorded row refuses it, and flipping the
    spec's forecastable switch actually switches it off — neither held while
    the petition-kind baseline arm admitted it registry-blind."""
    db = corpus.corpus_db_path(tmp_path)
    case_id = "scotus/91"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="26-91",
                    disposition=Disposition.denied,  # decided, outcome unrecorded
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                ),
                corpus.CorpusEvent(
                    event_id="evt-petition-arrival-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    moment=Moment.arrival,
                ),
            ],
        )
    # Decided row: the stage arm refuses the arrival moment (the baseline's
    # own admission is that arm's separate, documented tolerance).
    assert "evt-petition-arrival-disposition" not in forecastable_events(db, "scotus", 91)


def test_a_switched_off_declared_moment_stays_out_whatever_its_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The register's forecastable switch binds petition-kind moments too."""
    db = corpus.corpus_db_path(tmp_path)
    case_id = "scotus/92"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id=case_id, court="scotus", docket_number="26-92")],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-arrival-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    moment=Moment.arrival,
                )
            ],
        )
    switched = tuple(
        dataclasses.replace(s, forecastable=False)
        if s.event_id == "evt-petition-arrival-disposition"
        else s
        for s in moments_module.DECLARED_MOMENTS
    )
    monkeypatch.setattr(moments_module, "DECLARED_MOMENTS", switched)
    monkeypatch.setattr(moments_module, "_BY_EVENT_ID", {s.event_id: s for s in switched})
    assert "evt-petition-arrival-disposition" not in forecastable_events(db, "scotus", 92)


def test_the_baseline_waits_for_its_own_moment_on_a_cert_docket(tmp_path: Path) -> None:
    """The distribution-moment cell cannot mint before a distribution exists:
    an undistributed pending petition forecasts at the arrival moment or not
    at all, so an arrival-selected case can never sweep premature baseline
    cells whose snapshots carry no conference."""
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/93", court="scotus", docket_number="26-93")],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id="scotus/93",
                    court="scotus",
                    kind=EventKind.petition,
                )
            ],
        )
    assert forecastable_events(db, "scotus", 93) == []
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET distributed_for_conference = '2026-09-28' WHERE case_id = ?",
            ("scotus/93",),
        )
        conn.commit()
    assert forecastable_events(db, "scotus", 93, today=date(2026, 9, 20)) == [
        "evt-petition-disposition"
    ]


def _docket(*entries: tuple[str, str]) -> dict[str, object]:
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


#: Distributed for the 2026-09-28 conference, which sat on it.
_SAT = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Aug 12 2026", "DISTRIBUTED for Conference of 9/28/2026."),
)
#: The shape of Nos. 26-18, 26-23, 26-60 and 25-1366: a call for response
#: entered after the distribution took the petition off the conference.
_CALLED_FOR_RESPONSE = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Aug 12 2026", "DISTRIBUTED for Conference of 9/28/2026."),
    ("Sep 02 2026", "Response Requested. (Due October 2, 2026)"),
)
_RESCHEDULED = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Aug 12 2026", "DISTRIBUTED for Conference of 9/28/2026."),
    ("Sep 25 2026", "Rescheduled."),
)
#: The shape of No. 25-1313: the CVSG came after the conference sat, so it took
#: nothing off it.
_CVSG_AFTER = _docket(
    ("Jun 01 2026", "Petition for a writ of certiorari filed."),
    ("Aug 12 2026", "DISTRIBUTED for Conference of 9/28/2026."),
    ("Oct 05 2026", "The Solicitor General is invited to file a brief in this case."),
)


def _distributed_petition(
    db: Path, docket_id: int, payload: dict[str, object] | None, *, stored: date
) -> None:
    """A pending petition the row says is distributed for 2026-09-28."""
    case_id = f"scotus/{docket_id}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"26-{docket_id}",
                    distributed_for_conference=date(2026, 9, 28),
                    distribution_count=1,
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                    moment=Moment.distribution,
                )
            ],
        )
        if payload is not None:
            corpus.upsert_snapshot(conn, case_id, stored, payload)


@pytest.mark.parametrize(
    ("payload", "today", "admitted"),
    [
        # The conference is ahead: open, and no payload is read at all.
        (None, date(2026, 9, 27), True),
        # The conference sat on it: the moment is over (the 26-53 … 26-183 run).
        (_SAT, date(2026, 10, 4), False),
        # The conference day itself counts as sat.
        (_SAT, date(2026, 9, 28), False),
        # Taken off the conference before it sat: legitimately undecided.
        (_CALLED_FOR_RESPONSE, date(2026, 10, 4), True),
        (_RESCHEDULED, date(2026, 10, 4), True),
        # A CVSG entered after the conference sat takes nothing off it.
        (_CVSG_AFTER, date(2026, 10, 6), False),
        # No readable docket: no evidence the petition is still open.
        (None, date(2026, 10, 4), False),
    ],
)
def test_a_distribution_cell_is_never_first_minted_after_its_conference_considered_it(
    tmp_path: Path, payload: dict[str, object] | None, today: date, admitted: bool
) -> None:
    """First-time admission shares the re-predict rule's conference bound, keyed
    on whether the conference actually considered the petition."""
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 53, payload, stored=date(2026, 10, 6))
    found = forecastable_events(db, "scotus", 53, today=today)
    assert found == (["evt-petition-disposition"] if admitted else [])


def test_a_payload_stored_before_the_conference_cannot_show_it_was_taken_off(
    tmp_path: Path,
) -> None:
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 54, _CALLED_FOR_RESPONSE, stored=date(2026, 9, 20))
    assert forecastable_events(db, "scotus", 54, today=date(2026, 10, 4)) == []


def test_a_relisted_petition_is_open_against_its_next_conference(tmp_path: Path) -> None:
    """A later distribution moves the column ahead, so nothing is read."""
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 55, None, stored=date(2026, 10, 1))
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET distributed_for_conference = '2026-10-09' WHERE case_id = ?",
            ("scotus/55",),
        )
        conn.commit()
    assert forecastable_events(db, "scotus", 55, today=date(2026, 10, 4)) == [
        "evt-petition-disposition"
    ]


def test_an_unreadable_content_store_refuses_rather_than_raising(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A store error under the conference bound degrades the decision — the
    cell is refused and deferred — and never fails the plan or the routing."""
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 57, _CALLED_FOR_RESPONSE, stored=date(2026, 10, 6))

    def broken(conn: object, case_id: str) -> None:
        raise RuntimeError("the content store is down")

    monkeypatch.setattr(corpus, "latest_live_snapshot", broken)
    assert forecastable_events(db, "scotus", 57, today=date(2026, 10, 4)) == []


def test_the_payload_reader_reads_each_case_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads: list[str] = []
    real = corpus.latest_live_snapshot

    def counting(conn: corpus.ReadConnection, case_id: str) -> object:
        reads.append(case_id)
        return real(conn, case_id)

    monkeypatch.setattr(corpus, "latest_live_snapshot", counting)
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 58, _SAT, stored=date(2026, 10, 6))
    with corpus.connect_readonly(db) as conn:
        reader = live_payload_reader(conn)
        assert reader("scotus/58") == reader("scotus/58")
    assert reads == ["scotus/58"]
    # Both cert-capable arms ask the same case, and it is still read once.
    reads.clear()
    forecastable_events(db, "scotus", 58, today=date(2026, 10, 4))
    assert reads == ["scotus/58"]


def test_distribution_conference_considered_reads_the_payload_only_once_past(
    tmp_path: Path,
) -> None:
    reads: list[str] = []

    def payloads(case_id: str) -> tuple[date, dict[str, object]] | None:
        reads.append(case_id)
        return date(2026, 10, 6), _SAT

    row = corpus.CorpusRow(
        case_id="scotus/56",
        court="scotus",
        docket_number="26-56",
        distributed_for_conference=date(2026, 9, 28),
    )
    assert not distribution_conference_considered(row, day=date(2026, 9, 27), payloads=payloads)
    assert reads == []
    assert distribution_conference_considered(row, day=date(2026, 10, 4), payloads=payloads)
    assert reads == ["scotus/56"]


def _pending_petition(db: Path, docket_id: int) -> None:
    """A pending, distributed SCOTUS petition with its open cert baseline."""
    case_id = f"scotus/{docket_id}"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="24-77",
                    distribution_count=1,
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-petition-disposition",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.petition,
                    stage=Stage.cert,
                )
            ],
        )


def test_forward_refusal_reason_is_silent_on_a_genuinely_open_event(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_petition(db, 21)

    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 21, "evt-petition-disposition")

    assert reason is None


def test_forward_refusal_reason_reads_the_committed_outcome(tmp_path: Path) -> None:
    # The ledger's own outcome.json is the most specific record of a closed
    # event, and it must refuse the forward cell even when the corpus has not
    # flipped the resolved flag yet.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    data_root = tmp_path / "data"
    _pending_petition(db, 22)
    outcome = CasePaths(data_root, "scotus", 22).event("evt-petition-disposition").outcome
    outcome.parent.mkdir(parents=True)
    outcome.write_text("{}")

    reason = forward_refusal_reason(db, data_root, "scotus", 22, "evt-petition-disposition")

    assert reason is not None and "outcome" in reason


def test_forward_refusal_reason_reads_the_resolved_event_flag(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_petition(db, 23)
    with corpus.connect(db) as conn:
        corpus.set_event_resolved(conn, "scotus/23", "evt-petition-disposition", resolved=True)

    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 23, "evt-petition-disposition")

    assert reason is not None and "resolved" in reason


def test_forward_refusal_reason_reads_the_decided_row(tmp_path: Path) -> None:
    # The paused-pipeline shape: the disposition latched on the row while the
    # event row and the ledger lagged — the record still says decided.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _pending_petition(db, 24)
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/24")
        assert row is not None
        corpus.upsert_rows(conn, [row.model_copy(update={"disposition": Disposition.denied})])

    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 24, "evt-petition-disposition")

    assert reason is not None and "decided" in reason


def test_forward_refusal_reason_keys_a_merits_event_on_the_judgment(tmp_path: Path) -> None:
    # A merits cell's outcome is the judgment, not the cert disposition its own
    # grant latched — the grant must not refuse it, the latched judgment must.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _granted_case(db, 25, disposition=Disposition.granted)

    assert forward_refusal_reason(db, tmp_path / "data", "scotus", 25, "evt-order-judgment") is None

    _granted_case(db, 25, disposition=Disposition.granted, merits_judgment=Judgment.reversed)
    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 25, "evt-order-judgment")

    assert reason is not None and "judgment" in reason


def test_forward_refusal_reason_refuses_a_terminated_merits_proceeding(tmp_path: Path) -> None:
    # The record gate's own arm for the no-disposition exit: nothing will latch
    # a judgment, so provisioning must read the termination instead of trusting
    # an unlatched column — otherwise the predict-scope latch is the only guard.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _granted_case(db, 28, disposition=Disposition.granted)

    assert forward_refusal_reason(db, tmp_path / "data", "scotus", 28, "evt-order-judgment") is None

    _granted_case(
        db,
        28,
        disposition=Disposition.granted,
        merits_terminated=MeritsTermination.voluntary_dismissal,
    )
    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 28, "evt-order-judgment")

    assert reason is not None and "terminated" in reason


def test_event_recorded_closed_checks_nothing_without_an_event_id(tmp_path: Path) -> None:
    assert event_recorded_closed(tmp_path / "data", "scotus", 26, "", []) is None


def test_forward_refusal_reason_is_stricter_than_the_interim_queue_arm(tmp_path: Path) -> None:
    # The interim queue predicate carries no decided-row arm, so here the gate
    # is deliberately stricter than queue time: an application row whose
    # date_decided latched is the record of an outcome, whatever the queue
    # seam asks, and its still-open motion event earns no forward cell.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    case_id = "scotus/27"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="25A77",
                    date_decided=date(2026, 7, 1),
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-motion-stay",
                    case_id=case_id,
                    court="scotus",
                    kind=EventKind.motion,
                    stage=Stage.interim,
                )
            ],
        )

    reason = forward_refusal_reason(db, tmp_path / "data", "scotus", 27, "evt-motion-stay")

    assert reason is not None and "decided" in reason


def test_event_has_claimable_prediction_reads_the_frozen_partition(tmp_path: Path) -> None:
    """The comparability gate on cohort completion. It asks the question the
    boards ask — is the scored predictor's LATEST prediction frozen — so an
    event whose whole cohort is unstamped is refused, and one frozen sibling is
    enough to admit it."""
    data_root = tmp_path / "data"
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")  # no ledger

    # Two unstamped predictions: real cells, but outside the partition every
    # claimable board scores in.
    seed_prediction(data_root, "scotus", 1, "evt-a", predictor_id="claude-baseline")
    seed_prediction(data_root, "scotus", 1, "evt-a", predictor_id="gemini-baseline")
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")

    # One frozen sibling is enough: the board counts that cohort, so completing
    # it adds an engine to a comparison rather than manufacturing one.
    seed_prediction(data_root, "scotus", 1, "evt-a", predictor_id="claude-baseline", frozen=True)
    assert event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")
    # Per event, not per case.
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-b")


def test_event_has_claimable_prediction_keys_on_the_latest_run_per_predictor(
    tmp_path: Path,
) -> None:
    """`stratify` joins an evaluation to the predictor's latest prediction, so a
    predictor whose newest run is unstamped is out of the frozen partition even
    though an older frozen run of its own survives on disk. This predicate must
    read the same way or it answers a question no board asks."""
    data_root = tmp_path / "data"
    event = CasePaths(data_root, "scotus", 1).event("evt-a")
    write_json(
        event.prediction("claude-baseline", "20260101T000000Z"),
        Prediction(
            case_id="scotus/1",
            event_id="evt-a",
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id="20260101T000000Z",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.05,
            predicted_disposition=Disposition.denied,
            process_version=frozen_stamp(),
        ),
    )
    assert event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")

    # A later, unstamped re-run of the same predictor supersedes it for the
    # join. Later by the *harness* clock (`cell_clock`), which reads the frozen
    # cell's `stamped_at` and falls back to `created_at` only when unstamped —
    # so the re-run has to postdate the freeze instant, not merely the sibling's
    # authored date; derive it from the instant so a freeze cutover moves it
    # without touching this test.
    rerun_at = (process_version.FROZEN_SINCE or datetime(2026, 1, 1, tzinfo=UTC)) + timedelta(
        days=30
    )
    rerun_id = rerun_at.strftime("%Y%m%dT%H%M%SZ")
    write_json(
        event.prediction("claude-baseline", rerun_id),
        Prediction(
            case_id="scotus/1",
            event_id="evt-a",
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id=rerun_id,
            created_at=rerun_at,
            input_snapshot=f"record/snapshots/{rerun_at.date().isoformat()}.json",
            granted=0,
            probability=0.05,
            predicted_disposition=Disposition.denied,
        ),
    )
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")


def test_a_window_prediction_is_ledgered_but_not_claimable(tmp_path: Path) -> None:
    """A cell minted between the bless moment and the counting instant.

    Its digest is blessed and its stamp postdates the promotion that made
    those bytes immutable, so it is an honest ledger cell and the
    retroactive-blessing tripwire does not fire on it. The counting boundary
    is what keeps it out: every claimable surface reads the partition through
    `is_frozen`, which gates on the instant. Pinned here because the window is
    open whenever a freeze commit guesses the instant late, and a membership
    test that forgot the timing limb would silently admit these.
    """
    opening = open_freeze_window()
    if opening is None:
        pytest.skip("no window between a bless moment and the counting instant is open")
    digest, minted = opening

    data_root = tmp_path / "data"
    run_id = minted.strftime("%Y%m%dT%H%M%SZ")
    stamp = ProcessVersion(
        label=process_version.CURRENT_PROCESS_LABEL, digest=digest, stamped_at=minted
    )
    write_json(
        CasePaths(data_root, "scotus", 1).event("evt-a").prediction("claude-baseline", run_id),
        Prediction(
            case_id="scotus/1",
            event_id="evt-a",
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id=run_id,
            created_at=minted,
            input_snapshot=f"record/snapshots/{minted.date().isoformat()}.json",
            granted=0,
            probability=0.05,
            predicted_disposition=Disposition.denied,
            process_version=stamp,
        ),
    )
    assert process_version.at_or_after_bless(stamp)
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")


def test_the_claimable_gate_reads_the_instant_and_not_only_membership(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The window predicate on patched constants, where the live ones cannot reach.

    The test above reads the real `[bless, instant)` window and skips where a
    freeze commit leaves none open — an instant placed at its carrying merge
    closes it by construction, which is the point of placing it there. What it
    guards stays live either way: this predicate reads the partition through
    `is_frozen`, and a membership-only check that dropped the timing limb
    would keep every digest test above green. So the window is patched in here
    rather than read off the module, and the same cell is put on both sides of
    one instant so the refusal is attributable to timing alone.
    """
    bless = datetime(2026, 1, 1, tzinfo=UTC)
    instant = datetime(2026, 2, 1, tzinfo=UTC)
    bless_process(monkeypatch, "sha256:blessed", since=instant, blessed_at=bless)
    data_root = tmp_path / "data"
    event = CasePaths(data_root, "scotus", 1).event("evt-a")

    def write_cell(minted: datetime) -> ProcessVersion:
        stamp = ProcessVersion(
            label=process_version.CURRENT_PROCESS_LABEL,
            digest="sha256:blessed",
            stamped_at=minted,
        )
        run_id = minted.strftime("%Y%m%dT%H%M%SZ")
        write_json(
            event.prediction("claude-baseline", run_id),
            Prediction(
                case_id="scotus/1",
                event_id="evt-a",
                predictor_id="claude-baseline",
                engine="claude-code",
                model="claude-fable-5",
                run_id=run_id,
                created_at=minted,
                input_snapshot=f"record/snapshots/{minted.date().isoformat()}.json",
                granted=0,
                probability=0.05,
                predicted_disposition=Disposition.denied,
                process_version=stamp,
            ),
        )
        return stamp

    # Inside the window: blessed digest, stamp after the bless and before the
    # instant. An honest ledger cell the tripwire passes and the gate refuses.
    windowed = write_cell(instant - timedelta(days=1))
    assert process_version.at_or_after_bless(windowed)
    assert not event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")

    # The same predictor's later run, stamped at the instant, is claimable —
    # so the refusal above was the timing limb and not the membership one.
    write_cell(instant)
    assert event_has_claimable_prediction(data_root, "scotus", 1, "evt-a")


def _usage_record(
    case: str, event: str, role: UsageRole, actor: str, created_at: datetime
) -> ModelUsage:
    return ModelUsage(
        case_id=case,
        event_id=event,
        run_id="20260901T000000Z",
        role=role,
        actor_id=actor,
        engine="claude-code",
        model="claude-fable-5",
        created_at=created_at,
        input_tokens=10,
        output_tokens=1,
        estimated_cost_usd=0.5,
    )


def _write_usage(data_root: Path, record: ModelUsage, *, run: str = "20260901T000000Z") -> None:
    court, _, docket = record.case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(record.event_id)
    path = (
        event.prediction_usage(record.actor_id, run)
        if record.role is UsageRole.predictor
        else event.evaluation_usage(record.actor_id, run)
    )
    write_json(path, record)


def test_recent_cell_census_groups_by_role_and_stage(tmp_path: Path) -> None:
    """The week's production, split the way a reader asks about it.

    A usage record names its event but not the standard governing it, so the
    stage comes off the moment register — the same table the fan-out mints
    from — rather than being guessed from the id.
    """
    data_root = tmp_path / "data"
    now = datetime(2026, 9, 8, tzinfo=UTC)
    inside = now - timedelta(days=2)
    outside = now - timedelta(days=30)
    _write_usage(
        data_root,
        _usage_record("scotus/1", "evt-petition-disposition", UsageRole.predictor, "a", inside),
    )
    _write_usage(
        data_root,
        _usage_record("scotus/2", "evt-petition-disposition", UsageRole.predictor, "a", inside),
    )
    _write_usage(
        data_root,
        _usage_record("scotus/1", "evt-petition-disposition", UsageRole.evaluator, "j", inside),
    )
    _write_usage(
        data_root,
        _usage_record("scotus/3", "evt-petition-disposition", UsageRole.predictor, "a", outside),
    )

    census = recent_cell_census(data_root, window_days=7, now=now)

    assert census.window_days == 7
    assert census.cells == 3  # the 30-day-old cell is out of the window
    assert census.events == 2
    assert census.rows == [
        CellCensusRow(role="evaluator", stage="cert", cells=1),
        CellCensusRow(role="predictor", stage="cert", cells=2),
    ]


def test_recent_cell_census_names_an_undeclared_stage_rather_than_dropping_it(
    tmp_path: Path,
) -> None:
    """A bucket that vanished would make the rows stop summing to the total."""
    data_root = tmp_path / "data"
    now = datetime(2026, 9, 8, tzinfo=UTC)
    _write_usage(
        data_root,
        _usage_record(
            "scotus/1", "evt-motion-something-nobody-declared", UsageRole.predictor, "a", now
        ),
    )

    census = recent_cell_census(data_root, window_days=7, now=now)

    assert census.rows == [CellCensusRow(role="predictor", stage=UNDECLARED_STAGE, cells=1)]
    assert sum(row.cells for row in census.rows) == census.cells


def test_recent_cell_census_reads_a_naive_stamp_as_utc(tmp_path: Path) -> None:
    """A schema-valid naive `created_at` must not crash the comparison — the
    same tolerance `trailing_spend` applies to the very same records, so the
    count and the cost describe one set of cells."""
    data_root = tmp_path / "data"
    now = datetime(2026, 9, 8, tzinfo=UTC)
    _write_usage(
        data_root,
        _usage_record(
            "scotus/1",
            "evt-petition-disposition",
            UsageRole.predictor,
            "a",
            datetime(2026, 9, 7),  # naive
        ),
    )

    assert recent_cell_census(data_root, window_days=7, now=now).cells == 1


def test_recent_cell_census_on_an_empty_ledger_is_empty(tmp_path: Path) -> None:
    census = recent_cell_census(tmp_path / "data", window_days=7)
    assert census.cells == 0
    assert census.events == 0
    assert census.rows == []


def test_normalized_stage_reads_a_null_petition_stage_as_cert() -> None:
    """One rule in one place: the boards and every surface that captions a
    number by its stage have to agree about what a null means, or the same cell
    reads as two different populations."""
    assert normalized_stage(EventKind.petition, None) is Stage.cert
    assert normalized_stage(EventKind.appeal, None) is Stage.cert
    # Nothing says which rule would govern a motion, so none is invented.
    assert normalized_stage(EventKind.motion, None) is None
    # A recorded stage is never overridden.
    assert normalized_stage(EventKind.petition, Stage.merits) is Stage.merits


def test_iter_predictions_reads_every_committed_prediction_in_a_total_order(
    tmp_path: Path,
) -> None:
    """Identity comes off the path, and the order is total, so two readers of one
    tree collapse the same runs the same way."""
    for case, event, predictor, run in (
        ("scotus/2", "evt-petition-disposition", "codex-baseline", "r2"),
        ("scotus/1", "evt-order-response-requested-disposition", "claude-baseline", "r1"),
        ("scotus/1", "evt-petition-disposition", "claude-baseline", "r1"),
        ("scotus/1", "evt-petition-disposition", "claude-baseline", "r0"),
    ):
        court, _, docket = case.partition("/")
        seed_prediction(tmp_path, court, int(docket), event, predictor_id=predictor, run_id=run)
    rows = iter_predictions(tmp_path)
    assert [(r.case_id, r.event_id, r.predictor_id, r.run_id) for r in rows] == [
        ("scotus/1", "evt-order-response-requested-disposition", "claude-baseline", "r1"),
        ("scotus/1", "evt-petition-disposition", "claude-baseline", "r0"),
        ("scotus/1", "evt-petition-disposition", "claude-baseline", "r1"),
        ("scotus/2", "evt-petition-disposition", "codex-baseline", "r2"),
    ]
    assert rows[0].court_id == "scotus" and rows[0].docket_id == 1
    assert rows[0].cell_path.endswith("predictions/claude-baseline/r1")
    assert rows[0].prediction.case_id == "scotus/1"


def test_iter_predictions_on_an_absent_ledger_creates_nothing(tmp_path: Path) -> None:
    absent = tmp_path / "absent"
    assert iter_predictions(absent) == []
    assert not absent.exists()


#: The No. 26-455 shape: the only distribution on the docket is a sealing
#: motion's, filed under its own M-number; the petition is undistributed.
_MOTION_ONLY = _docket(
    ("Sep 01 2026", "Motion (26M8) for leave to file under seal filed."),
    ("Sep 09 2026", "Motion (26M8) DISTRIBUTED for Conference of 10/9/2026."),
    ("Oct 05 2026", "Petition for a writ of certiorari filed."),
)


@pytest.mark.parametrize(
    ("count", "conference", "distributed"),
    [
        # An ancillary paper's distribution sets the membership column only.
        (0, date(2026, 10, 9), False),
        (1, date(2026, 10, 9), True),
        (0, None, False),
        # No count was ever derived: the column is the only evidence there is.
        (None, date(2026, 10, 9), True),
        (None, None, False),
    ],
)
def test_petition_distributed_reads_the_petitions_own_count(
    count: int | None, conference: date | None, distributed: bool
) -> None:
    row = corpus.CorpusRow(
        case_id="scotus/60",
        court="scotus",
        docket_number="26-60",
        distributed_for_conference=conference,
        distribution_count=count,
    )
    assert petition_distributed(row) is distributed


def test_an_ancillary_motions_distribution_mints_no_distribution_cell(tmp_path: Path) -> None:
    """The motion's conference is still ahead, so the upper bound reads nothing
    and admits; only the lower bound, keyed on the petition's own count, refuses."""
    db = corpus.corpus_db_path(tmp_path)
    _distributed_petition(db, 61, _MOTION_ONLY, stored=date(2026, 10, 6))
    with corpus.connect(db) as conn:
        conn.execute(
            "UPDATE cases SET distributed_for_conference = '2026-10-09', "
            "distribution_count = 0 WHERE case_id = ?",
            ("scotus/61",),
        )
        conn.commit()
    assert forecastable_events(db, "scotus", 61, today=date(2026, 10, 6)) == []
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET distribution_count = 1 WHERE case_id = ?", ("scotus/61",))
        conn.commit()
    assert forecastable_events(db, "scotus", 61, today=date(2026, 10, 6)) == [
        "evt-petition-disposition"
    ]


def test_a_re_predict_never_targets_a_petition_only_its_motion_distributed() -> None:
    row = corpus.CorpusRow(
        case_id="scotus/62",
        court="scotus",
        docket_number="26-62",
        distributed_for_conference=date(2026, 10, 9),
        distribution_count=0,
    )

    def payloads(case_id: str) -> tuple[date, dict[str, object]] | None:
        return date(2026, 10, 6), _MOTION_ONLY

    day = date(2026, 10, 6)
    assert not _reopenable_moment("evt-petition-disposition", row, day=day, payloads=payloads)
    distributed = row.model_copy(update={"distribution_count": 1})
    assert _reopenable_moment("evt-petition-disposition", distributed, day=day, payloads=payloads)


def _bounded_moment_case(
    db: Path, event_id: str, kind: EventKind, entries: list[dict[str, str]]
) -> None:
    """A pending petition carrying one conference-bounded cert moment, opened 2026-10-05."""
    case_id = "scotus/91"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number="25-910",
                    cvsg_date=date(2026, 1, 12),
                    distribution_count=2,
                    distributed_for_conference=date(2026, 10, 16),
                )
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=event_id,
                    case_id=case_id,
                    court="scotus",
                    kind=kind,
                    stage=Stage.cert,
                    opened_at=date(2026, 10, 5),
                )
            ],
        )
        corpus.upsert_snapshot(conn, case_id, date(2026, 10, 20), {"ProceedingsandOrder": entries})


_RELISTED = [
    {"Date": "Sep 15 2026", "Text": "DISTRIBUTED for Conference of 10/2/2026."},
    {"Date": "Oct 05 2026", "Text": "DISTRIBUTED for Conference of 10/16/2026."},
]


@pytest.mark.parametrize(
    ("event_id", "kind", "entries", "today", "admitted"),
    [
        # The relisted-for conference is ahead: the moment is open.
        ("evt-order-relist-disposition", EventKind.order, _RELISTED, date(2026, 10, 12), True),
        # It sat and left the petition undecided: relisted again or held, so closed.
        ("evt-order-relist-disposition", EventKind.order, _RELISTED, date(2026, 10, 19), False),
        # Taken off that conference before it sat: never considered, so still open.
        (
            "evt-order-relist-disposition",
            EventKind.order,
            [*_RELISTED, {"Date": "Oct 14 2026", "Text": "Rescheduled."}],
            date(2026, 10, 19),
            True,
        ),
        # The conference before the trigger does not count: the brief opened the
        # moment after it, and no distribution follows the brief yet.
        (
            "evt-brief-sg-disposition",
            EventKind.brief,
            [{"Date": "Sep 15 2026", "Text": "DISTRIBUTED for Conference of 10/2/2026."}],
            date(2026, 10, 19),
            True,
        ),
        # The first conference after the brief has sat: closed.
        ("evt-brief-sg-disposition", EventKind.brief, _RELISTED, date(2026, 10, 19), False),
        # A call for a response takes the petition off the conference it was
        # distributed for before the call, which never counts: open.
        (
            "evt-order-call-for-response-disposition",
            EventKind.order,
            [
                {"Date": "Sep 15 2026", "Text": "DISTRIBUTED for Conference of 10/16/2026."},
                {"Date": "Oct 05 2026", "Text": "Response Requested. (Due November 4, 2026)"},
            ],
            date(2026, 10, 19),
            True,
        ),
        # Redistributed after the call, for a conference that has since sat: closed.
        (
            "evt-order-call-for-response-disposition",
            EventKind.order,
            [
                {"Date": "Sep 15 2026", "Text": "DISTRIBUTED for Conference of 10/2/2026."},
                {"Date": "Oct 05 2026", "Text": "Response Requested. (Due October 9, 2026)"},
                {"Date": "Oct 06 2026", "Text": "DISTRIBUTED for Conference of 10/16/2026."},
            ],
            date(2026, 10, 19),
            False,
        ),
        # A relist whose own distribution entry does not parse: the docket was not
        # read as the trigger was, so the cell waits.
        ("evt-order-relist-disposition", EventKind.order, _RELISTED[:1], date(2026, 10, 12), False),
    ],
)
def test_a_conference_bounded_cert_cell_closes_once_the_next_conference_sits(
    tmp_path: Path,
    event_id: str,
    kind: EventKind,
    entries: list[dict[str, str]],
    today: date,
    admitted: bool,
) -> None:
    """Each moment forecasts the next conference, so a petition that conference left
    undecided has moved to another population and earns no cell placed back at it."""
    db = corpus.corpus_db_path(tmp_path)
    _bounded_moment_case(db, event_id, kind, entries)
    with corpus.connect(db) as conn:
        offered = forecastable_event_ids(conn, "scotus", 91, today=today)
    assert (event_id in offered) is admitted


def test_a_relist_cell_refuses_without_a_readable_payload(tmp_path: Path) -> None:
    """No live payload is no evidence the conference has not sat, so the cell waits."""
    db = corpus.corpus_db_path(tmp_path)
    _bounded_moment_case(db, "evt-order-relist-disposition", EventKind.order, _RELISTED)
    with corpus.connect(db) as conn:
        conn.execute("DELETE FROM snapshots")
        offered = forecastable_event_ids(conn, "scotus", 91, today=date(2026, 10, 12))
    assert "evt-order-relist-disposition" not in offered
