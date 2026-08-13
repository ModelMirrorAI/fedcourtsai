import dataclasses
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline import moments as moments_module
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    Disposition,
    EventKind,
    FlagCategory,
    Judgment,
    Moment,
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
) -> None:
    """A SCOTUS petition whose CVSG order has been minted beside its baseline."""
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
                    # Distributed: the baseline's distribution moment has
                    # occurred, so its cell may mint (the arrival moment owns
                    # the pre-distribution forecast).
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
                    date_cert_granted=date(2025, 1, 10),
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
    # An IFP docket serial is a documented predict-scope exclusion, and a
    # granted IFP petition opens a merits proceeding like any other — so the
    # scope rules, not the merits predicate, are what keep its cell out.
    db = corpus.corpus_db_path(tmp_path)
    _granted_case(db, 14, disposition=Disposition.granted, docket_number="24-5001")

    assert forecastable_events(db, "scotus", 14) == []
    assert open_events(db, "scotus", 14) == ["evt-order-judgment"]


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
        corpus.upsert_events(conn, [_briefed_event("scotus/82")])
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
    assert forecastable_events(db, "scotus", 93) == ["evt-petition-disposition"]
