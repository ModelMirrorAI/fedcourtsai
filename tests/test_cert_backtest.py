"""Cert back-test: selection, redaction, scoring (lift + calibration), and replay."""

from __future__ import annotations

import os
import sys
import threading
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, cert_backtest, corpus
from fedcourtsai.backtest import (
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    ConstantBacktester,
)
from fedcourtsai.cert_backtest import (
    _kept_entries_show_a_disposition,
    redact_snapshot,
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
    truncate_snapshot,
)
from fedcourtsai.cli import app
from fedcourtsai.config import load_salience_config
from fedcourtsai.pipeline import arrival_cut, cell_context, cert_signals, ingest
from fedcourtsai.pipeline.asof import replay_cutoff
from fedcourtsai.pipeline.runner import (
    AgenticRunner,
    CommandResult,
    EngineFailed,
    EngineQuotaExhausted,
    EngineUnavailable,
    Runner,
    RunRequest,
    StubRunner,
    get_runner,
)
from fedcourtsai.pricing import DEFAULT_MODELS
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    CertBacktest,
    CertBacktestCellLoss,
    CertBacktestDisclosureTally,
    Disposition,
    FlagCategory,
    PredictionContext,
    PredictorConfig,
    UsageRole,
)
from fedcourtsai.serialize import read_model
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _item(case_id: str, actual: Disposition) -> BacktestItem:
    return BacktestItem(
        BacktestFeatures(
            case_id=case_id,
            court="scotus",
            topic=None,
            judges=(),
            date_filed=None,
            year=None,
        ),
        actual,
    )


class FixedBacktester:
    """Predicts a fixed disposition and probability for every trial."""

    def __init__(self, id: str, disposition: Disposition, probability: float) -> None:
        self.id = id
        self._prediction = BacktestPrediction(disposition, probability)

    def predict(self, features: BacktestFeatures) -> BacktestPrediction:
        return self._prediction


def _seed_selection_corpus(db: Path) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # Modern cert, decided most recently -> selected first.
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="23-100",
                    disposition=Disposition.granted,
                    date_decided=date(2024, 6, 1),
                ),
                # Modern cert, decided earlier -> selected second.
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="21-200",
                    disposition=Disposition.denied,
                    date_decided=date(2022, 1, 10),
                ),
                # Decided but `other` -> not machine-readable, excluded.
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="22-300",
                    disposition=Disposition.other,
                    date_decided=date(2023, 1, 1),
                ),
                # Bare historical docket -> not the modern cert form, excluded.
                corpus.CorpusRow(
                    case_id="scotus/4",
                    court="scotus",
                    docket_number="801",
                    disposition=Disposition.denied,
                    date_decided=date(1900, 1, 1),
                ),
                # Application docket -> not the modern cert form, excluded.
                corpus.CorpusRow(
                    case_id="scotus/5",
                    court="scotus",
                    docket_number="22A123",
                    disposition=Disposition.denied,
                    date_decided=date(2023, 2, 2),
                ),
                # Decided before filed -> internally inconsistent, excluded.
                corpus.CorpusRow(
                    case_id="scotus/6",
                    court="scotus",
                    docket_number="22-400",
                    disposition=Disposition.denied,
                    date_filed=date(2023, 5, 1),
                    date_decided=date(2021, 5, 1),
                ),
                # Not SCOTUS -> excluded by court.
                corpus.CorpusRow(
                    case_id="ca9/7",
                    court="ca9",
                    docket_number="22-15001",
                    disposition=Disposition.denied,
                    date_decided=date(2023, 3, 3),
                ),
            ],
        )


def test_selection_keeps_modern_cert_with_trusted_labels_recent_first(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_selection_corpus(db)
    with corpus.connect(db) as conn:
        items = select_cert_backtest_set(conn)
        capped = select_cert_backtest_set(conn, limit=1)
    assert [i.features.case_id for i in items] == ["scotus/2", "scotus/1"]
    assert [i.actual_disposition for i in items] == [Disposition.granted, Disposition.denied]
    assert [i.features.case_id for i in capped] == ["scotus/2"]


def test_selection_orders_by_petition_stage_resolution(tmp_path: Path) -> None:
    # A granted petition ranks by its cert-grant date, not the merits termination
    # months later — so it slots between denials decided around the grant.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="22-100",
                    disposition=Disposition.granted,
                    date_cert_granted=date(2022, 10, 3),
                    date_decided=date(2023, 6, 30),
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="22-200",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2023, 1, 9),
                ),
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="21-300",
                    disposition=Disposition.denied,
                    date_cert_denied=date(2022, 6, 27),
                ),
            ],
        )
        items = select_cert_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["scotus/2", "scotus/1", "scotus/3"]


def _cert_row(
    case_id: str,
    docket: str,
    *,
    disposition: Disposition = Disposition.denied,
    distribution_count: int = 1,
    cvsg: bool = False,
    conference: date | None = None,
    decided: date = date(2024, 6, 1),
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        disposition=disposition,
        date_decided=decided,
        distribution_count=distribution_count,
        cvsg_date=date(2024, 1, 2) if cvsg else None,
        distributed_for_conference=conference,
    )


def test_scope_paid_drops_ifp_and_selected_keeps_the_carveout_core(tmp_path: Path) -> None:
    # all: every modern-cert petition. paid: drops the IFP row (Tier-0). selected:
    # keeps only the gate's carve-out core — a CVSG petition or one at/above the
    # salience floor — so a below-floor paid petition is dropped too.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _cert_row(
                    "scotus/paidlow", "23-100", distribution_count=1
                ),  # relist-0, below floor
                _cert_row(
                    "scotus/paidhot", "23-200", distribution_count=3
                ),  # relist-2, above floor
                _cert_row("scotus/cvsg", "23-300", distribution_count=1, cvsg=True),  # carve-out
                _cert_row("scotus/ifp", "23-5001", distribution_count=3),  # IFP (serial >= 5001)
            ],
        )
    with corpus.connect(db) as conn:
        all_ids = {i.features.case_id for i in select_cert_backtest_set(conn, scope="all")}
        paid_ids = {i.features.case_id for i in select_cert_backtest_set(conn, scope="paid")}
        selected_ids = {
            i.features.case_id for i in select_cert_backtest_set(conn, scope="selected")
        }
    assert all_ids == {"scotus/paidlow", "scotus/paidhot", "scotus/cvsg", "scotus/ifp"}
    assert paid_ids == {"scotus/paidlow", "scotus/paidhot", "scotus/cvsg"}  # IFP dropped
    assert selected_ids == {"scotus/paidhot", "scotus/cvsg"}  # below-floor paid dropped too


def test_spread_round_robins_across_conferences(tmp_path: Path) -> None:
    # Recency order alone takes the newest N from one conference; --spread instead
    # draws the newest from each conference in turn — a term-cadence sample.
    db = tmp_path / "corpus.db"
    conf_a, conf_b, conf_c = date(2024, 1, 5), date(2024, 2, 16), date(2024, 3, 15)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _cert_row("scotus/a1", "23-101", conference=conf_a, decided=date(2024, 6, 10)),
                _cert_row("scotus/a2", "23-102", conference=conf_a, decided=date(2024, 6, 9)),
                _cert_row("scotus/a3", "23-103", conference=conf_a, decided=date(2024, 6, 8)),
                _cert_row("scotus/b1", "23-201", conference=conf_b, decided=date(2024, 5, 10)),
                _cert_row("scotus/b2", "23-202", conference=conf_b, decided=date(2024, 5, 9)),
                _cert_row("scotus/c1", "23-301", conference=conf_c, decided=date(2024, 4, 10)),
            ],
        )
    with corpus.connect(db) as conn:
        plain = [i.features.case_id for i in select_cert_backtest_set(conn, limit=3)]
        spread = [i.features.case_id for i in select_cert_backtest_set(conn, limit=3, spread=True)]
    assert plain == ["scotus/a1", "scotus/a2", "scotus/a3"]  # all from the newest conference
    assert spread == ["scotus/a1", "scotus/b1", "scotus/c1"]  # one from each, newest-conf first


def test_select_rejects_an_unknown_scope(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_selection_corpus(db)
    with corpus.connect(db) as conn, pytest.raises(ValueError, match="unknown scope"):
        select_cert_backtest_set(conn, scope="bogus")


def test_redact_snapshot_strips_outcome_fields_only() -> None:
    payload = {
        "id": 304,
        "case_name": "In re Pacific Mutual",
        "docket_number": "22-845",
        "date_filed": "2024-01-08",
        "date_terminated": "2024-10-07",
        "disposition": "Certiorari denied",
        "date_argued": "2024-09-01",
        "clusters": ["https://example/clusters/1/"],
        "citation_count": 3,
        "docket_entries": [{"id": 1, "description": "Petition DENIED."}],
    }
    redacted = redact_snapshot(payload)
    # The derived, decision-only fields go. The proceedings do NOT: content offers
    # no rule that separates a disposing order from a pre-decision entry, but a
    # date does, so they are truncated instead — see truncate_snapshot.
    assert set(redacted) == {"id", "case_name", "docket_number", "date_filed", "docket_entries"}


def test_redact_snapshot_strips_accruing_counsel_blocks_but_keeps_captions() -> None:
    payload = {
        "id": 305,
        "PetitionerTitle": "Pacific Mutual",
        "RespondentTitle": "Haslip",
        "Petitioner": [{"name": "A. Counsel", "title": "Counsel of Record"}],
        "Respondent": [{"name": "B. Counsel", "title": "Counsel of Record"}],
        "Other": [{"name": f"Amicus Counsel {n}"} for n in range(10)],
        "AttorneyHeaderPetitioner": "Attorneys for Petitioner",
        "AttorneyHeaderRespondent": "Attorneys for Respondent",
        "AttorneyHeaderOther": "Other",
    }
    redacted = redact_snapshot(payload)
    # The counsel blocks accrue with every amicus filing, so their size on a
    # decided docket is a grant oracle — they go. The two title captions are
    # the arrival-time case name a forward cell sees, so they stay.
    assert set(redacted) == {"id", "PetitionerTitle", "RespondentTitle"}


def test_scoring_reports_lift_over_the_always_deny_floor() -> None:
    # Three petitions, one granted: the always-deny floor scores 2/3.
    items = [
        _item("scotus/1", Disposition.denied),
        _item("scotus/2", Disposition.denied),
        _item("scotus/3", Disposition.granted),
    ]
    always_deny = ConstantBacktester(id="constant-denied", disposition=Disposition.denied)
    perfect = FixedBacktester("oracle-denied", Disposition.denied, 0.0)
    report = run_cert_backtest([always_deny, perfect], items)
    assert report.always_denied_accuracy == 2 / 3
    by_id = {e.predictor_id: e for e in report.entries}
    # The floor's lift is zero by construction.
    assert by_id["constant-denied"].lift_over_always_denied == 0.0
    assert by_id["constant-denied"].accuracy == 2 / 3


def test_scoring_builds_a_calibration_view() -> None:
    items = [
        _item("scotus/1", Disposition.denied),
        _item("scotus/2", Disposition.granted),
    ]
    hedged = FixedBacktester("hedged", Disposition.denied, 0.45)
    report = run_cert_backtest([hedged], items)
    (entry,) = report.entries
    (bin_,) = entry.calibration
    # Both predictions land in the [0.4, 0.5) bin; one of the two was granted.
    assert (bin_.lower, bin_.upper) == (0.4, 0.5)
    assert bin_.predictions == 2
    assert bin_.mean_probability == 0.45
    assert bin_.observed_granted_rate == 0.5


def test_calibration_top_bin_is_closed_at_one() -> None:
    items = [_item("scotus/1", Disposition.granted)]
    certain = FixedBacktester("certain", Disposition.granted, 1.0)
    (entry,) = run_cert_backtest([certain], items).entries
    (bin_,) = entry.calibration
    assert (bin_.lower, bin_.upper) == (0.9, 1.0)
    assert bin_.predictions == 1


def test_ranking_leads_with_lift_then_brier() -> None:
    items = [
        _item("scotus/1", Disposition.denied),
        _item("scotus/2", Disposition.granted),
    ]
    floor = ConstantBacktester(id="constant-denied", disposition=Disposition.denied)
    sharp = FixedBacktester("sharp", Disposition.granted, 0.5)  # same accuracy, worse label mix
    report = run_cert_backtest([floor, sharp], items)
    # Both score 1/2 accuracy -> lift 0; the tie breaks on mean Brier (floor: 0.5, sharp: 0.25).
    assert [e.predictor_id for e in report.entries] == ["sharp", "constant-denied"]


def test_empty_set_yields_empty_report() -> None:
    report = run_cert_backtest([], [])
    assert (report.events_scored, report.predictors_evaluated) == (0, 0)
    assert report.stratum == "retrospective"


class _BigCaseBacktester:
    """Predicts denied@0.2 but attaches a per-case pre-registered big_case_score."""

    def __init__(self, id: str, scores: dict[str, float]) -> None:
        self.id = id
        self._scores = scores

    def predict(self, features: BacktestFeatures) -> BacktestPrediction:
        return BacktestPrediction(
            Disposition.denied, 0.2, big_case_score=self._scores[features.case_id]
        )


def test_big_case_distribution_summarizes_predicted_stakes() -> None:
    items = [_item("scotus/1", Disposition.granted), _item("scotus/2", Disposition.denied)]
    bt = _BigCaseBacktester("stakes", {"scotus/1": 0.9, "scotus/2": 0.3})
    (entry,) = run_cert_backtest([bt], items).entries
    assert entry.big_case is not None
    assert entry.big_case.scored == 2
    assert entry.big_case.mean == pytest.approx(0.6)  # (0.9 + 0.3) / 2
    assert (entry.big_case.minimum, entry.big_case.maximum) == (0.3, 0.9)


def test_offline_baselines_report_no_big_case() -> None:
    # A predictor that emits no big_case_score (the offline reference baselines)
    # leaves the dimension null — the replay never fabricates a stakes read.
    items = [_item("scotus/1", Disposition.granted)]
    floor = ConstantBacktester(id="constant-denied", disposition=Disposition.denied)
    (entry,) = run_cert_backtest([floor], items).entries
    assert entry.big_case is None


def test_offline_run_without_a_statpack_carries_no_segments() -> None:
    # The default (no `segments`) path — offline reference baselines — leaves the
    # per-band breakdown empty; it never fabricates a base rate it wasn't given.
    items = [_item("scotus/1", Disposition.granted), _item("scotus/2", Disposition.denied)]
    (entry,) = run_cert_backtest([FixedBacktester("f", Disposition.denied, 0.2)], items).entries
    assert entry.segments == []


def _seed_segment_corpus(db: Path) -> None:
    # A high-band item in OT24 with a prior-Term high-band anchor in OT23, plus an
    # IFP high-band item (outside the paid scored segment) that must not band.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-100",  # paid, OT24, 2 relists -> high band
                    disposition=Disposition.granted,
                    date_filed=date(2024, 10, 1),
                    date_cert_granted=date(2025, 1, 6),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900",
                    court="scotus",
                    docket_number="23-500",  # paid, OT23 high band -> the prior-Term anchor
                    disposition=Disposition.denied,
                    date_filed=date(2023, 10, 1),
                    date_cert_denied=date(2024, 1, 8),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,
                ),
                corpus.CorpusRow(
                    case_id="scotus/5001",
                    court="scotus",
                    docket_number="24-5900",  # IFP (serial >= 5001): outside the scored segment
                    disposition=Disposition.denied,
                    date_filed=date(2024, 10, 1),
                    date_cert_denied=date(2025, 1, 8),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,
                ),
            ],
        )


def test_segment_context_bands_only_the_paid_scored_segment(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_segment_corpus(db)
    with corpus.connect(db) as conn:
        items = select_cert_backtest_set(conn)
        statpack = analytics.build_statpack(corpus_db_path=db)
        context = cert_backtest.build_segment_context(conn, items, statpack)
    # The IFP petition is selected as an item but is not in the scored segment.
    assert "scotus/5001" not in context
    assert context["scotus/1"].band == "high"
    # OT24's high-band rate pools OT23 only (denied) -> 0%; leakage-safe.
    assert context["scotus/1"].base_rate == 0.0
    # OT23 has no prior Term to anchor on -> no base rate.
    assert context["scotus/900"].base_rate is None


def _seed_gapped_segment_corpus(db: Path) -> None:
    # An OT25 high-band item whose only prior high-band anchor is OT23 — OT24 is
    # absent, so the pack carries a Term GAP. That gap is what lets a lookback
    # window discriminate: a 1-Term window reaches only OT24, which has no rows.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="25-100",  # paid, OT25, 2 relists -> high band
                    disposition=Disposition.granted,
                    date_filed=date(2025, 10, 1),
                    date_cert_granted=date(2026, 1, 6),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,
                ),
                corpus.CorpusRow(
                    case_id="scotus/900",
                    court="scotus",
                    docket_number="23-500",  # paid, OT23 high band -> the only anchor
                    disposition=Disposition.denied,
                    date_filed=date(2023, 10, 1),
                    date_cert_denied=date(2024, 1, 8),
                    last_live_polled=date(2026, 7, 1),
                    sample_weight=1,
                    distribution_count=3,
                ),
            ],
        )


def test_build_segment_context_honours_the_lookback_window(tmp_path: Path) -> None:
    # The seam that carries `salience.base_rate_lookback_terms` into the back-test.
    # Over a gapped pack (OT25 item, OT23 anchor, no OT24) the window is decisive:
    # unbounded reaches OT23 and yields its rate, while a 1-Term window reaches
    # only the empty OT24 and leaves the item with no anchor at all. `None` must
    # behave as the shipped default, 0 — dropping the kwarg fails this test.
    db = tmp_path / "corpus.db"
    _seed_gapped_segment_corpus(db)
    with corpus.connect(db) as conn:
        items = select_cert_backtest_set(conn)
        statpack = analytics.build_statpack(corpus_db_path=db)
        default = cert_backtest.build_segment_context(conn, items, statpack)
        unbounded = cert_backtest.build_segment_context(conn, items, statpack, lookback_terms=0)
        narrowed = cert_backtest.build_segment_context(conn, items, statpack, lookback_terms=1)
    assert default["scotus/2"].base_rate == 0.0  # OT23's denial, pooled
    assert unbounded["scotus/2"].base_rate == 0.0
    assert narrowed["scotus/2"].base_rate is None  # OT23 is outside a 1-Term window


def test_cert_backtest_reports_per_band_segment_skill(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_segment_corpus(db)
    with corpus.connect(db) as conn:
        items = select_cert_backtest_set(conn)
        statpack = analytics.build_statpack(corpus_db_path=db)
        segments = cert_backtest.build_segment_context(conn, items, statpack)
        report = run_cert_backtest(
            [FixedBacktester("grant-0.9", Disposition.granted, 0.9)], items, segments=segments
        )
    (entry,) = report.entries
    (high,) = entry.segments  # only the paid high-band petitions band
    assert high.band == "high"
    assert high.events_scored == 2  # scotus/1 + scotus/900; the IFP row is excluded
    assert high.accuracy == 0.5  # grants scotus/1 (right), scotus/900 denied (wrong)
    assert high.mean_brier_score == pytest.approx(0.41)  # (0.01 + 0.81) / 2
    # Only scotus/1 had a prior-Term base rate (0.0); its skill vs that baseline
    # is 1 - 0.01/1.0 = 0.99, and the band means fold in only that item.
    assert high.segment_base_rate == 0.0
    assert high.mean_brier_skill == pytest.approx(0.99)


def test_replay_runs_the_stub_engine_over_redacted_snapshots(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    work_root = tmp_path / "replay"
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["scotus/304"]
    # The replay clock rides on the features (docket 22-845 -> OT2022): each
    # cell receives it as DECIDED_BEFORE so its retrieval is time-masked.
    assert items[0].features.year == 2022

    outcome = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=work_root,
        engine_override="stub",
        run_id="20260706T000000Z",
    )
    backtesters = outcome.backtesters
    unavailable = outcome.unavailable
    assert unavailable == []  # the stub is always available

    # One replayed backtester per enabled predictor, each covering the whole set.
    expected = {p.id for p in enabled_predictors(Path("config") / "predictors.yaml")}
    assert {b.id for b in backtesters} == expected
    report = run_cert_backtest(backtesters, items)
    assert report.events_scored == 1
    assert {e.predictor_id for e in report.entries} == expected
    # The stub's canned big_case_score survives the replay read-back into the report.
    for entry in report.entries:
        assert entry.big_case is not None and entry.big_case.scored == 1
        assert entry.big_case.mean == 0.5

    # The provisioned tree hides the outcome: the snapshot is redacted and the
    # event definition reads unresolved; nothing was written outside work_root.
    snapshot = next(work_root.rglob("record/snapshots/*.json")).read_text()
    assert "date_terminated" not in snapshot
    # Case-insensitively: the fixture writes "Petition DENIED.", so asserting on
    # "Denied" passed whether or not the order was still there.
    assert "denied" not in snapshot.lower()
    assert "granted" not in snapshot.lower()
    event_yaml = next(work_root.rglob("event.yaml")).read_text()
    assert "resolved: false" in event_yaml
    assert not fixture_corpus.data_root.exists()


class _ClockRecordingRunner:
    """Delegates to the stub but records both halves of each cell's clock."""

    def __init__(self, clocks: list[tuple[int | None, date | None]]) -> None:
        self._clocks = clocks
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        self._clocks.append((request.decided_before, request.replay_cutoff))
        return self._stub.run(request)


def _replay_clocks(
    fixture_corpus: FixtureCorpus, work_root: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[list[tuple[int | None, date | None]], Path, dict[str, date]]:
    """Replay the fixture set through a clock-recording runner; return the clocks."""
    clocks: list[tuple[int | None, date | None]] = []
    monkeypatch.setattr(
        cert_backtest, "get_runner", lambda backend="stub": _ClockRecordingRunner(clocks)
    )
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=work_root,
        run_id="20260706T000000Z",
    )
    assert clocks, "no cell ran"
    return clocks, work_root, outcome.clock_days


def test_a_dated_replay_cell_carries_both_halves_of_its_clock(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The Term is the case's own docket Term on every arm — self-excluding, and
    # what the prompt contract anchors on — and the cutoff day rides beside it,
    # never in place of it. The fixture petition shows no dated distribution
    # before its resolution, so the cutoff the real rule would derive is
    # supplied here.
    cut = date(2024, 5, 20)
    monkeypatch.setattr(cert_backtest, "replay_cutoff", lambda payload, resolved_at: cut)
    clocks, work_root, clock_days = _replay_clocks(fixture_corpus, tmp_path / "replay", monkeypatch)
    context = read_model(next(work_root.rglob("record/context.json")), PredictionContext)
    assert context.cutoff == cut
    assert set(clocks) == {(2022, cut)}
    # The same day reaches the offline reference baseline, so its row on the
    # board is masked as the engine rows were.
    assert clock_days == {"scotus/304": cut}
    # And the record's clock is the Term, which is what the statpack's per-Term
    # anchoring rule is read against; `cutoff` beside it carries the day.
    assert context.decided_before == "2022"


def test_a_blind_replay_cell_carries_the_term_half_only(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The blind arm is the one provisioning produced no cutoff for, so there is
    # no day to narrow with and the Term stands alone.
    monkeypatch.setattr(cert_backtest, "replay_cutoff", lambda payload, resolved_at: None)
    clocks, work_root, clock_days = _replay_clocks(fixture_corpus, tmp_path / "replay", monkeypatch)
    context = read_model(next(work_root.rglob("record/context.json")), PredictionContext)
    assert context.cutoff is None and context.snapshot_provenance == "blind"
    assert set(clocks) == {(2022, None)}
    assert clock_days == {}


def test_a_provisioned_dated_cell_is_not_among_its_own_priors(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Self-exclusion, end to end and unmocked: give the fixture petition a real
    distribution so provisioning derives a real cutoff, then retrieve at the
    clock the cell was handed and check its own row is not in the result.

    The structural reason is asserted separately over ``replay_cutoff`` itself
    (``test_a_replay_cutoff_never_falls_after_its_own_resolution``); this leg
    checks the two ends agree — that the clock provisioning writes is the clock
    ``retrieve_priors`` screens on, and that the screen is strict. The second
    retrieval loosens the Term by one so the day bar is doing the work alone:
    in the cell's real clock the two exclusions overlap, and a test that only
    ran the real one could not tell which had fired.
    """
    case_id = "scotus/304"
    with corpus.connect(fixture_corpus.db_path) as conn:
        found = corpus.latest_snapshot(conn, case_id)
        assert found is not None
        snapshot_date, payload = found
        entries = list(payload["docket_entries"])
        entries.insert(
            -1,
            {
                "id": 99,
                "date_filed": "2024-05-20",
                "description": "DISTRIBUTED for Conference of June 6, 2024.",
            },
        )
        corpus.upsert_snapshot(conn, case_id, snapshot_date, {**payload, "docket_entries": entries})

    clocks, _, clock_days = _replay_clocks(fixture_corpus, tmp_path / "replay", monkeypatch)
    # Derived by the real rule: the day after the last distribution preceding
    # the 2024-06-24 denial.
    assert clock_days == {case_id: date(2024, 5, 21)}
    terms = {term for term, day in clocks if day is not None}
    assert terms == {2022}  # the docket Term of 22-845, not a Term read off the day

    with corpus.connect(fixture_corpus.db_path) as conn:
        for term in (2022, 2023):
            priors = corpus.retrieve_priors(
                conn,
                corpus.PriorQuery(
                    court="scotus", decided_before=term, decided_before_day=date(2024, 5, 21)
                ),
                limit=1_000,
            )
            assert case_id not in {r.case_id for r in priors}, term
        # And the day is what excludes it at the loosened Term: without the day
        # that same Term admits it.
        loose = corpus.retrieve_priors(
            conn, corpus.PriorQuery(court="scotus", decided_before=2023), limit=1_000
        )
    assert case_id in {r.case_id for r in loose}


class _RecordingRunner:
    """Delegates to the stub but records which backend served which predictor."""

    def __init__(self, backend: str, calls: list[tuple[str, str]]) -> None:
        self._backend = backend
        self._calls = calls
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        self._calls.append((self._backend, request.actor_id))
        return self._stub.run(request)


def _fake_get_runner(calls: list[tuple[str, str]], *, unrouted: str | None = None) -> object:
    """A `get_runner` double that records routing; ``unrouted`` simulates an engine
    with no registered runner (raising ``KeyError`` as the real registry would)."""

    def factory(backend: str = "stub") -> _RecordingRunner:
        if backend == unrouted:
            raise KeyError(backend)
        return _RecordingRunner(backend, calls)

    return factory


def test_replay_routes_each_predictor_through_its_own_engine(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Without an override every predictor rides its own configured engine — the
    # apples-to-apples read — claude-code, codex, and gemini alike.
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(cert_backtest, "get_runner", _fake_get_runner(calls))
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    backtesters = outcome.backtesters
    unavailable = outcome.unavailable
    assert unavailable == []
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline", "gemini-baseline"}
    # No cell ever ran on an engine other than its predictor's own.
    routed = {actor: backend for backend, actor in calls}
    assert routed == {
        "claude-baseline": "claude-code",
        "codex-baseline": "codex",
        "gemini-baseline": "gemini",
    }
    # And each backtester records that routing, so the report can state it.
    assert {
        (b.id, b.engine) for b in backtesters if isinstance(b, cert_backtest.ReplayedBacktester)
    } == {
        ("claude-baseline", "claude-code"),
        ("codex-baseline", "codex"),
        ("gemini-baseline", "gemini"),
    }


def test_replay_drops_a_predictor_whose_engine_has_no_runner(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A predictor whose engine has no registered runner is absent from the result,
    # never mislabeled through another engine (here gemini stands in for any such
    # engine, its runner simulated away).
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(cert_backtest, "get_runner", _fake_get_runner(calls, unrouted="gemini"))
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    backtesters = outcome.backtesters
    unavailable = outcome.unavailable
    assert unavailable == []  # a no-runner engine is dropped up front, not "unavailable"
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline"}
    assert "gemini" not in {backend for backend, _ in calls}


def test_replay_opts_a_named_engine_out(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The explicit `--skip-engines` opt-out: a named engine's predictor is dropped
    # up front, its engine never touched — the two remaining engines stay a
    # like-for-like comparison. (Distinct from the missing-binary path below,
    # which is a run-time safety net, not a deliberate choice.)
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(cert_backtest, "get_runner", _fake_get_runner(calls))
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
        skip_engines=frozenset({"gemini"}),
    )
    backtesters = outcome.backtesters
    unavailable = outcome.unavailable
    assert unavailable == []
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline"}
    assert "gemini" not in {backend for backend, _ in calls}


class _MaybeUnavailableRunner:
    """Records routing but raises :class:`EngineUnavailable` for one backend."""

    def __init__(self, backend: str, calls: list[tuple[str, str]], missing: str) -> None:
        self._backend = backend
        self._calls = calls
        self._missing = missing
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        if self._backend == self._missing:
            raise EngineUnavailable(self._backend)  # the CLI binary is not installed
        self._calls.append((self._backend, request.actor_id))
        return self._stub.run(request)


def test_replay_drops_a_missing_binary_loudly_and_keeps_the_rest(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Config drift (an engine's CLI is absent) must not crash the whole run and
    # strand the spend already made on the other engines: the engine is dropped,
    # returned in `unavailable` for the caller to report loudly, and the rest of
    # the report is produced.
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _MaybeUnavailableRunner(backend, calls, "gemini"),
    )
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    backtesters = outcome.backtesters
    unavailable = outcome.unavailable
    assert unavailable == ["gemini-baseline"]
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline"}
    assert "gemini" not in {backend for backend, _ in calls}


class _MisplacingRunner:
    """A stub that writes one predictor's cell somewhere the runner will not look.

    Reproduces the incident the kickoff fix removes: an engine that followed the
    prompt template's repo-relative ``data/cases/...`` output path wrote its
    files into the checkout's ledger while the runner read the back-test work
    root. Whatever the kickoff now says, an engine can still put its files in
    the wrong place — which is what this exercises: the campaign has to survive
    it and account for it, not crash on the first read-back.

    ``elsewhere`` is where the misplaced cell lands; ``None`` writes nothing at
    all (the cell that produced no file anywhere).
    """

    def __init__(self, misplace: str, elsewhere: Path | None) -> None:
        self._misplace = misplace
        self._elsewhere = elsewhere
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        if request.actor_id != self._misplace:
            return self._stub.run(request)
        if self._elsewhere is None:
            return []
        return self._stub.run(replace(request, data_root=self._elsewhere))


def test_a_cell_written_to_the_wrong_root_is_a_loss_and_the_others_score(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The incident, end to end: one cell lands off the work root and is lost.

    The campaign must finish — the cells already paid for on the other engines
    are the whole reason — with the stray cell named on the report and the rest
    scored. The reason is the specific one, because "wrote outside the work
    root" and "produced nothing" call for different fixes.
    """
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _MisplacingRunner("codex-baseline", fixture_corpus.data_root),
    )
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert outcome.unavailable == []  # every engine was there; one cell was not
    assert outcome.lost_cells == [
        CertBacktestCellLoss(
            predictor_id="codex-baseline",
            case_id=items[0].features.case_id,
            reason="wrote-outside-work-root",
        )
    ]
    # The cells that landed where the runner reads are scored, and the predictor
    # that lost its only cell is off the board rather than on it at zero.
    assert {b.id for b in outcome.backtesters} == {"claude-baseline", "gemini-baseline"}
    report = run_cert_backtest(outcome.backtesters, items)
    assert {e.predictor_id for e in report.entries} == {"claude-baseline", "gemini-baseline"}
    assert all(e.events_scored == len(items) for e in report.entries)


def test_a_cell_that_produced_nothing_is_a_loss_too(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The plainer half of the same fault: the engine returned and wrote no file
    # anywhere. Distinguished from the misplaced write because the probe found
    # no cell under the ledger either.
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _MisplacingRunner("gemini-baseline", None),
    )
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert [(c.predictor_id, c.reason) for c in outcome.lost_cells] == [
        ("gemini-baseline", "missing")
    ]
    assert {b.id for b in outcome.backtesters} == {"claude-baseline", "codex-baseline"}


def test_a_malformed_cell_is_a_loss_rather_than_a_crash(tmp_path: Path) -> None:
    # A file that is there and is not a Prediction: the schema-invalid half,
    # which read_model raises as a ValueError rather than an OSError.
    cell = tmp_path / "prediction.json"
    cell.write_text('{"predicted_disposition": "not-a-disposition"}')
    lost = cert_backtest._read_replayed_cell(
        cell, None, predictor_id="claude-baseline", case_id="scotus/304"
    )
    assert isinstance(lost, CertBacktestCellLoss)
    assert lost.reason == "invalid"


class _FailingRunner:
    """A stub that raises one backend's engine failure and serves the rest.

    The engine ran and exited non-zero — the fault the campaign used to die of.
    ``failure`` is the exception that backend raises, so one double covers both
    an ordinary failure and a terminal quota.
    """

    def __init__(
        self,
        backend: str,
        failing: str,
        failure: EngineFailed,
        calls: list[tuple[str, str]],
    ) -> None:
        self._backend = backend
        self._failing = failing
        self._failure = failure
        self._calls = calls
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        self._calls.append((self._backend, request.actor_id))
        if self._backend == self._failing:
            raise self._failure
        return self._stub.run(request)


def _failing_get_runner(
    failing: str, failure: EngineFailed, calls: list[tuple[str, str]]
) -> object:
    """A `get_runner` double whose ``failing`` backend raises ``failure``."""

    def factory(backend: str = "stub") -> _FailingRunner:
        return _FailingRunner(backend, failing, failure, calls)

    return factory


def test_an_engine_failure_is_one_lost_cell_not_a_lost_campaign(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cell whose engine exited non-zero costs that cell and nothing else.

    The cells already paid for on the other engines are the whole reason: an
    exception escaping here discards them with the work root and lands no
    report at all, which is strictly worse than a report naming one loss.
    """
    calls: list[tuple[str, str]] = []
    failure = EngineFailed(
        "gemini exited 1 for cell gemini-baseline/evt-petition-disposition "
        + "after 3 attempts (transient failure, retry budget exhausted)"
    )
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert outcome.unavailable == []  # the binary was there; the call failed
    assert [(c.predictor_id, c.reason) for c in outcome.lost_cells] == [
        ("gemini-baseline", "engine-failed")
    ]
    assert {b.id for b in outcome.backtesters} == {"claude-baseline", "codex-baseline"}
    report = run_cert_backtest(outcome.backtesters, items)
    assert {e.predictor_id for e in report.entries} == {"claude-baseline", "codex-baseline"}


def test_a_terminal_quota_is_lost_under_its_own_reason(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Named apart from the plain failure because it says something different
    # about the run — and because it is the one that generalizes to the
    # engine's remaining cells.
    calls: list[tuple[str, str]] = []
    failure = EngineQuotaExhausted(
        "gemini exited 1 for cell gemini-baseline/evt-petition-disposition "
        + "(terminal quota: the engine's quota is exhausted and no retry can clear it)"
    )
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert [(c.predictor_id, c.reason) for c in outcome.lost_cells] == [
        ("gemini-baseline", "quota-exhausted")
    ]
    # The exhausted engine is not "unavailable": its CLI was there and answered.
    assert outcome.unavailable == []
    assert {b.id for b in outcome.backtesters} == {"claude-baseline", "codex-baseline"}


def _provisioned(
    work_root: Path, dockets: tuple[int, ...]
) -> list[cert_backtest._ProvisionedPetition]:
    """Cell contracts for SCOTUS petitions, as the provisioning phase hands them on."""
    return [
        cert_backtest._ProvisionedPetition(
            case_id=f"scotus/{docket}",
            cell=RunRequest(
                role=UsageRole.predictor,
                court_id="scotus",
                docket_id=docket,
                event_id="evt-petition-disposition",
                actor_id="",
                prompt=Path(),
                run_id="20260706T000000Z",
                data_root=work_root,
            ),
            stray_paths=None,
        )
        for docket in dockets
    ]


def test_a_spent_quota_skips_that_engines_later_cells_and_records_them(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Once the quota is known spent, the engine's later cells are not attempted.

    Two petitions through the engine lanes directly — the fixture corpus
    replays a single petition, and what is under test is precisely what carries
    *across* them, inside the one lane that owns the engine. Each skipped cell
    is still recorded as lost, so the report's counts say why the predictor is
    short rather than leaving the gap unexplained.
    """
    calls: list[tuple[str, str]] = []
    failure = EngineQuotaExhausted("gemini exited 1 for a cell (terminal quota: exhausted)")
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    pairs = cert_backtest._runners_by_predictor(Path("config"), None)
    engines = {predictor.id: str(predictor.engine) for predictor, _ in pairs}
    merged = cert_backtest._merged(
        cert_backtest._run_lanes(
            cert_backtest._engine_lanes(pairs, engines),
            _provisioned(tmp_path / "replay", (304, 305)),
            engines=engines,
            workers=0,
        )
    )
    losses, collected, unavailable = merged.losses, merged.collected, merged.unavailable
    # One attempt on gemini, ever: the second petition's cell was skipped rather
    # than paid for in backoff.
    assert [actor for backend, actor in calls if backend == "gemini"] == ["gemini-baseline"]
    # Both cells are on the report, under the reason that explains the gap.
    assert [(c.case_id, c.predictor_id, c.reason) for c in losses] == [
        ("scotus/304", "gemini-baseline", "quota-exhausted"),
        ("scotus/305", "gemini-baseline", "quota-exhausted"),
    ]
    # The other engines are untouched by one engine's quota, on both petitions.
    assert collected["claude-baseline"].keys() == {"scotus/304", "scotus/305"}
    assert collected["codex-baseline"].keys() == {"scotus/304", "scotus/305"}
    assert unavailable == set()  # a spent quota is never a missing binary


def test_the_cli_names_a_quota_drop_as_that(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # End to end: the campaign lands a report, and the predictor whose engine ran
    # out is dropped as that rather than as cells that came back unreadable.
    calls: list[tuple[str, str]] = []
    failure = EngineQuotaExhausted("gemini exited 1 for a cell (terminal quota: exhausted)")
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--engine", "auto", "--work-dir", str(tmp_path / "w")],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    assert [(c.predictor_id, c.reason) for c in report.provenance.lost_cells] == [
        ("gemini-baseline", "quota-exhausted")
    ]
    assert "gemini-baseline" in report.provenance.dropped_predictors
    assert "dropped predictor gemini-baseline: its engine's quota was exhausted" in result.stderr


def test_a_partly_lost_predictor_is_scored_over_what_came_back() -> None:
    """An entry short some cells is scored, and floored, over the ones it has.

    Lift against an always-deny floor computed over petitions the predictor
    never forecast would be arithmetic across two samples. The set here is two
    denials and a grant; a predictor holding only the grant is scored over that
    one petition, against the floor *that* petition implies (0.0), not the
    set's 2/3.
    """
    items = [
        _item("scotus/1", Disposition.denied),
        _item("scotus/2", Disposition.denied),
        _item("scotus/3", Disposition.granted),
    ]
    short = cert_backtest.ReplayedBacktester(
        id="claude-baseline",
        predictions={"scotus/3": BacktestPrediction(Disposition.granted, 0.9)},
        engine="stub",
    )
    report = run_cert_backtest([short], items)
    entry = report.entries[0]
    assert report.events_scored == 3  # the set is the set
    assert entry.events_scored == 1  # the entry is not
    assert entry.accuracy == 1.0
    assert entry.lift_over_always_denied == 1.0  # vs the 0.0 floor of its own petition
    assert report.always_denied_accuracy == pytest.approx(2 / 3)


def test_a_short_entry_never_outranks_one_that_scored_the_set() -> None:
    """The loss must not read as a reward on the rank key.

    Lift is a per-petition mean against a floor computed the same way, so
    dropping a petition the predictor would have got wrong both rescales and
    shifts it upward — here to a perfect +1.0 off one lucky petition, against
    an honest full-set entry's +1/3. Ranking the two on that number would put
    the predictor that lost a cell on top, so a short entry sorts below every
    full one whatever its lift.
    """
    items = [
        _item("scotus/1", Disposition.denied),
        _item("scotus/2", Disposition.denied),
        _item("scotus/3", Disposition.granted),
    ]
    lucky = cert_backtest.ReplayedBacktester(
        id="codex-baseline",
        predictions={"scotus/3": BacktestPrediction(Disposition.granted, 0.9)},
        engine="stub",
    )
    honest = cert_backtest.ReplayedBacktester(
        id="claude-baseline",
        predictions={
            item.features.case_id: BacktestPrediction(item.actual_disposition, 0.5)
            for item in items
        },
        engine="stub",
    )
    report = run_cert_backtest([lucky, honest], items)
    ranked = [(e.predictor_id, e.rank, e.events_scored) for e in report.entries]
    assert ranked == [("claude-baseline", 1, 3), ("codex-baseline", 2, 1)]
    # And the short entry's inflated number is still published — it is a
    # reading hazard to be labelled, not a figure to be hidden.
    assert report.entries[1].lift_over_always_denied == 1.0


def test_the_cli_report_carries_the_lost_cells(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The artifact is the durable channel: stderr expires with the runner, and a
    # board short one predictor's petitions must say so where a reader looks.
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _MisplacingRunner("codex-baseline", fixture_corpus.data_root),
    )
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--engine", "auto", "--work-dir", str(tmp_path / "w")],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    assert [(c.predictor_id, c.reason) for c in report.provenance.lost_cells] == [
        ("codex-baseline", "wrote-outside-work-root")
    ]
    # It lost its only cell, so it is dropped — as that, not as a missing runner.
    assert "codex-baseline" in report.provenance.dropped_predictors
    assert "every one of its cells was lost" in result.stderr
    assert "codex-baseline" not in {e.predictor_id for e in report.entries}


def test_replay_unknown_override_still_raises(fixture_corpus: FixtureCorpus) -> None:
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    with pytest.raises(KeyError):
        replay_predictors(
            items,
            corpus_db_path=fixture_corpus.db_path,
            config_root=Path("config"),
            work_root=Path("unused"),
            engine_override="not-a-backend",
            run_id="20260706T000000Z",
        )


def test_replayable_items_drops_snapshotless_petitions(fixture_corpus: FixtureCorpus) -> None:
    # A bulk-seeded row has no snapshot or petition event until its first fetch;
    # the pre-flight names it and keeps the report's set consistent.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/999",
                    court="scotus",
                    docket_number="23-999",
                    disposition=Disposition.denied,
                    date_decided=date(2024, 11, 1),
                )
            ],
        )
        items = select_cert_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["scotus/999", "scotus/304"]
    kept, skipped = replayable_items(fixture_corpus.db_path, items)
    assert [i.features.case_id for i in kept] == ["scotus/304"]
    assert skipped == ["scotus/999"]


def test_cli_auto_routes_and_skips_partial_coverage(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(cert_backtest, "get_runner", _fake_get_runner(calls))
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/999",
                    court="scotus",
                    docket_number="23-999",
                    disposition=Disposition.denied,
                    date_decided=date(2024, 11, 1),
                )
            ],
        )
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--engine", "auto", "--work-dir", str(tmp_path / "w")],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    # The snapshotless petition was dropped up front; every backtester —
    # offline baselines included — scored the same one-petition set.
    assert report.events_scored == 1
    assert "skipped 1 petition(s) without a replayable snapshot: scotus/999" in result.stderr
    ids = {e.predictor_id for e in report.entries}
    # Every enabled predictor replays through its own engine — gemini-baseline
    # included, now that the gemini runner is registered.
    assert {
        "constant-denied",
        "prior-vote",
        "claude-baseline",
        "codex-baseline",
        "gemini-baseline",
    } <= ids
    assert "skipped predictor" not in result.stderr


def test_cli_writes_valid_report_with_stub_replay(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        [
            "cert-backtest",
            "--out",
            str(out),
            "--engine",
            "stub",
            "--work-dir",
            str(tmp_path / "work"),
        ],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.stratum == "retrospective"
    assert report.events_scored == 1
    # Offline baselines plus every enabled predictor.
    ids = {e.predictor_id for e in report.entries}
    assert {"constant-denied", "prior-vote"} <= ids
    assert {p.id for p in enabled_predictors(Path("config") / "predictors.yaml")} <= ids
    assert "always-deny floor" in result.output


def test_cli_stub_report_self_identifies_as_stub(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # The provenance contract: a stub report must be legible as one from the
    # committed artifact alone. Predictor ids are identical under every backend,
    # so without this the same document reads as a real-engine board.
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        [
            "cert-backtest",
            "--out",
            str(out),
            "--engine",
            "stub",
            "--limit",
            "7",
            "--scope",
            "paid",
            "--spread",
            "--skip-engines",
            "gemini",
            "--work-dir",
            str(tmp_path / "work"),
        ],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    dispatch = report.provenance.dispatch
    # Every dispatch parameter that defines the population or the routing.
    assert dispatch.engine == "stub"
    assert dispatch.skip_engines == ["gemini"]
    assert dispatch.scope == "paid"
    assert dispatch.spread is True
    assert dispatch.limit == 7
    assert report.provenance.run_id is not None  # a replay ran, so it has a run
    # The frozen config that moves the population and the baselines under an
    # identical dispatch string rides along, or the block cannot decompose a
    # mixture of reports later.
    salience_cfg = load_salience_config(Path("config"))
    assert report.provenance.salience_floor == salience_cfg.floor
    assert report.provenance.base_rate_lookback_terms == salience_cfg.base_rate_lookback_terms
    replayed = {e.predictor_id: e for e in report.entries if e.engine is not None}
    assert replayed  # the enabled predictors were replayed
    for entry in replayed.values():
        assert entry.engine == "stub"  # what ran, not the predictor's own engine
        assert entry.model is None  # no model ran: the mark of a stub number
        # And the old null-heuristic really is broken, which is why this exists.
        assert entry.big_case is not None
    # The offline reference baselines ran no engine at all and say so.
    assert report.entries[0].predictor_id  # the board is non-empty
    baselines = [e for e in report.entries if e.predictor_id in {"constant-denied", "prior-vote"}]
    assert baselines and all(e.engine is None and e.model is None for e in baselines)
    assert "engine stub" in result.output


def test_cli_offline_report_records_the_dispatch_and_no_run(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # No --engine: only the offline baselines ran, so there is no run id and no
    # entry claims an engine — the reading that never overstates what produced it.
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app, ["cert-backtest", "--out", str(out), "--limit", "3", "--skip-engines", "gemini"]
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    assert report.provenance.run_id is None
    assert report.provenance.dispatch.engine == ""
    assert report.provenance.dispatch.limit == 3
    # Nothing was opted out of, because nothing ran: recording the opt-out would
    # name a choice that never applied.
    assert report.provenance.dispatch.skip_engines == []
    assert report.provenance.dropped_predictors == []
    assert all(e.engine is None and e.model is None for e in report.entries)
    assert "engine none (offline baselines only)" in result.output


def test_cli_rejects_an_unknown_engine(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    # A typo must never reach the artifact: the recorded engine is what tells a
    # real-engine board from a rehearsal, so an out-of-vocabulary value is
    # refused rather than written into a committed report.
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(tmp_path / "cert-backtest.json"), "--engine", "stbu"],
    )
    assert result.exit_code != 0
    assert "unknown backend 'stbu'" in result.output


def test_replay_records_the_backend_that_ran_each_predictor(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # Under an override every predictor runs on the named backend whatever its
    # registry entry says, and that discrepancy is the thing to record: the
    # entries are still named claude-/codex-/gemini-baseline.
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        engine_override="stub",
        run_id="20260706T000000Z",
    )
    backtesters = outcome.backtesters
    assert {b.id for b in backtesters} == {
        "claude-baseline",
        "codex-baseline",
        "gemini-baseline",
    }
    for backtester in backtesters:
        assert isinstance(backtester, cert_backtest.ReplayedBacktester)
        assert backtester.engine == "stub"
        assert backtester.model is None
    # The report carries the pair through onto every entry it scores.
    report = run_cert_backtest(backtesters, items)
    assert {(e.engine, e.model) for e in report.entries} == {("stub", None)}


def test_a_real_engine_entry_carries_its_engine_and_model(fixture_corpus: FixtureCorpus) -> None:
    # The other half of the wiring: an entry produced by a token-spending backend
    # names it and the model it was invoked with, so a real board is legible as
    # one. Built directly rather than by running an agent — the assertion is that
    # the pair reaches the entry, which no stub-routed test can make.
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    real = cert_backtest.ReplayedBacktester(
        id="claude-baseline",
        predictions={
            item.features.case_id: BacktestPrediction(Disposition.denied, 0.1) for item in items
        },
        engine="claude-code",
        model=DEFAULT_MODELS["claude-code"],
    )
    (entry,) = run_cert_backtest([real], items).entries
    assert entry.predictor_id == "claude-baseline"
    assert entry.engine == "claude-code"
    assert entry.model == DEFAULT_MODELS["claude-code"]


def test_replay_model_comes_from_the_shared_pricing_defaults() -> None:
    # The recorded model is the runner's own resolved model, which is read from
    # DEFAULT_MODELS — so a report cannot name a model the ledger would not price,
    # and a moved default moves this with it rather than leaving a stale string.
    for backend, expected in DEFAULT_MODELS.items():
        assert cert_backtest.replay_model(get_runner(backend)) == expected
    # The offline backends run no model at all; null is not "unknown" here.
    assert cert_backtest.replay_model(StubRunner()) is None


def test_cli_skip_engines_reports_the_opt_out_once(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # --skip-engines drops the engine from the replay and reports it once — not
    # also as a "no registered runner" skip (the reporting branches are guarded).
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        [
            "cert-backtest",
            "--out",
            str(out),
            "--engine",
            "stub",
            "--skip-engines",
            "gemini",
            "--work-dir",
            str(tmp_path / "work"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "opted out of engine(s): gemini" in result.stderr
    assert "skipped predictor gemini-baseline" not in result.stderr
    ids = {e.predictor_id for e in read_model(out, CertBacktest).entries}
    assert "gemini-baseline" not in ids
    assert {"claude-baseline", "codex-baseline"} <= ids  # the un-skipped engines still run


def test_cli_skip_engines_rejects_an_unknown_name(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    # A typo must fail loudly rather than silently run the engine it was meant to
    # skip (real spend) — the same contract --engine has for an unknown backend.
    result = runner.invoke(
        app,
        [
            "cert-backtest",
            "--out",
            str(tmp_path / "cert-backtest.json"),
            "--engine",
            "stub",
            "--skip-engines",
            "gemeni",  # typo
            "--work-dir",
            str(tmp_path / "work"),
        ],
    )
    assert result.exit_code != 0
    assert "unknown engine(s): gemeni" in result.output


def test_cli_scope_selected_runs(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    # --scope threads through to selection; the fixture's one petition is scored
    # or scoped out, but the command succeeds and writes a valid report either way.
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--scope", "selected", "--spread"],
    )
    assert result.exit_code == 0, result.output
    read_model(out, CertBacktest)  # a valid report was written


def test_cli_rejects_an_unknown_scope(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(tmp_path / "cert-backtest.json"), "--scope", "bogus"],
    )
    assert result.exit_code != 0
    assert "unknown scope 'bogus'" in result.output


def test_cli_absent_corpus_writes_empty_report(tmp_path: Path) -> None:
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out)],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.events_scored == 0


# --- replay truncation: the docket as it stood, not a docket with no history ------


def _live(*entries: tuple[str, str]) -> dict[str, Any]:
    return {
        "CaseNumber": "24-12 ",
        "ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries],
    }


_TRAJECTORY = _live(
    ("Jan 5 2025", "Petition for a writ of certiorari filed."),
    ("Feb 7 2025", "DISTRIBUTED for Conference of February 21, 2025."),
    ("Feb 24 2025", "DISTRIBUTED for Conference of March 7, 2025."),
    ("Mar 10 2025", "Petition DENIED."),
)


def test_the_cutoff_is_the_last_distribution_before_resolution() -> None:
    """A forward cell is queued by a distribution transition, so that is the moment
    a replay has to reproduce. The last one before resolution is the latest — and
    hardest — posture a forward cell would have seen."""
    assert replay_cutoff(_TRAJECTORY, date(2025, 3, 10)) == date(2025, 2, 25)


def test_the_cutoff_reads_entry_dates_not_the_conferences_they_name() -> None:
    """ "DISTRIBUTED for Conference of March 7" is *filed* in February, and February
    is when a forward cell would have run. Keying on the conference date would date
    the replay after the docket had already moved."""
    cutoff = replay_cutoff(_TRAJECTORY, date(2025, 3, 10))
    assert cutoff is not None and cutoff < date(2025, 3, 7)


def test_a_replay_cutoff_never_falls_after_its_own_resolution() -> None:
    """The structural guarantee behind a dated cell's self-exclusion.

    ``replay_cutoff`` takes the last distribution ``filed < resolved_at`` and
    returns ``filed + 1 day``, so the cutoff is at most the resolution date
    itself and never past it. The day screen is a strict ``<`` on the same
    quantity both ends read — ``corpus.resolution_date`` — so the replayed
    case's own row can never clear it, whatever its Term admits.

    Checked at the shape that stresses the bound: the plain trajectory, where
    the last distribution sits weeks before resolution; a distribution filed the
    very day before, where ``filed + 1`` lands exactly on it; and the rehearing
    family, where ``resolution_date`` falls back to the docket's termination and
    a later distribution survives the disposing order.
    """
    cases = [
        (_TRAJECTORY, date(2025, 3, 10)),
        (
            _live(
                ("Jan 5 2025", "Petition for a writ of certiorari filed."),
                ("Mar 9 2025", "DISTRIBUTED for Conference of March 21, 2025."),
            ),
            date(2025, 3, 10),
        ),
        (
            _live(
                ("Jan 5 2025", "Petition for a writ of certiorari filed."),
                ("Feb 7 2025", "DISTRIBUTED for Conference of February 21, 2025."),
                ("Mar 10 2025", "Petition DENIED."),
                ("May 2 2025", "DISTRIBUTED for Conference of May 15, 2025."),
            ),
            date(2025, 5, 30),
        ),
    ]
    for payload, resolved_at in cases:
        cutoff = replay_cutoff(payload, resolved_at)
        assert cutoff is not None and cutoff <= resolved_at, (cutoff, resolved_at)
    # The tight one, stated rather than left to the reader: filed the day before
    # resolution puts the cutoff exactly on it, which the strict `<` still bars.
    assert replay_cutoff(cases[1][0], cases[1][1]) == date(2025, 3, 10)


def test_no_dated_distribution_yields_no_cutoff() -> None:
    """Nothing to reproduce, so the caller drops the entries wholesale rather than
    inventing a moment."""
    assert replay_cutoff(_live(("Jan 5 2025", "Petition filed.")), date(2025, 3, 10)) is None
    assert replay_cutoff({}, date(2025, 3, 10)) is None


def test_truncation_keeps_the_pre_cutoff_docket_and_drops_the_disposition() -> None:
    kept, dropped = truncate_snapshot(_TRAJECTORY, date(2025, 2, 25))
    texts = [e["Text"] for e in kept["ProceedingsandOrder"]]
    assert texts == [
        "Petition for a writ of certiorari filed.",
        "DISTRIBUTED for Conference of February 21, 2025.",
        "DISTRIBUTED for Conference of March 7, 2025.",
    ]
    assert dropped == 1  # the denial, which is the whole point
    assert not any("DENIED" in t for t in texts)


def test_truncation_fails_closed_on_an_undated_entry() -> None:
    """An entry with no readable date could be the disposing order and nothing
    about it says otherwise. Dropping it costs a little context and cannot leak an
    outcome, which is the right way round."""
    payload = _live(("Feb 7 2025", "DISTRIBUTED for Conference of February 21, 2025."))
    payload["ProceedingsandOrder"] += [
        {"Text": "Petition DENIED."},  # no date at all
        {"Date": "not a date", "Text": "Petition DENIED."},
    ]
    kept, dropped = truncate_snapshot(payload, date(2025, 2, 25))
    assert [e["Text"] for e in kept["ProceedingsandOrder"]] == [
        "DISTRIBUTED for Conference of February 21, 2025."
    ]
    assert dropped == 2


def test_truncation_does_not_renumber_what_it_keeps() -> None:
    """Entry ids are positional and assigned on read, so removing the tail must
    leave a reference to entry *n* still meaning entry *n*."""
    full = ingest._live_entries(_TRAJECTORY)
    kept, _ = truncate_snapshot(_TRAJECTORY, date(2025, 2, 25))
    truncated = ingest._live_entries(kept)
    assert [e["id"] for e in truncated] == [1, 2, 3]
    assert [e["description"] for e in truncated] == [e["description"] for e in full[:3]]


def test_a_truncated_docket_still_discloses_its_own_band() -> None:
    """The reason truncation matters beyond leakage: a replay cell that can see its
    trajectory gets a real prediction-time band, so it is scored against the rate
    that posture implies instead of falling back to where the petition ended up."""
    kept, _ = truncate_snapshot(_TRAJECTORY, date(2025, 2, 25))
    context = cell_context.build(
        "scotus/305", date(2025, 2, 24), kept, "replay", provenance="truncated"
    )
    assert context.signals_observable is True
    assert context.distribution_count == 2  # one relist, as at the cutoff
    assert context.band == "elevated"
    # Wholesale deletion — the previous behaviour — disclosed nothing at all.
    blind, _ = truncate_snapshot(_TRAJECTORY, None)
    assert cell_context.build("scotus/305", date(2025, 2, 24), blind, "replay").band is None


def test_a_replay_cell_records_which_rule_bounded_it() -> None:
    """`cutoff` non-null implies `cut_kind` non-null, on every provisioner.

    The evaluate prompt's leakage clock keys on `cut_kind` — under `date` the
    cutoff is the clock, under `arrival-position` the boundary is tighter — so a
    cell carrying a cutoff with no kind gives the grader neither branch. The
    replay backtest population is the leakage-sensitive one, which is exactly
    where a null would have gone unnoticed.
    """
    kept, _ = truncate_snapshot(_TRAJECTORY, date(2025, 2, 25))
    context = cell_context.build(
        "scotus/305",
        date(2025, 2, 24),
        kept,
        "replay",
        provenance="truncated",
        cutoff=date(2025, 2, 25),
        boundary=arrival_cut.CutBoundary(kind="date"),
    )
    assert context.cutoff is not None
    assert context.cut_kind == "date"
    # The cert baseline's trigger is a conference, not a docket entry, so there
    # is no intra-day tail to exclude and no anchor to record.
    assert context.cut_anchor_index is None
    # The blind arm is the converse: proceedings removed wholesale and a null
    # cutoff, which is neither rule — it carries no kind (and the schema
    # refuses the kind-over-null-cutoff combination outright).
    blind, _ = truncate_snapshot(_TRAJECTORY, None)
    blind_context = cell_context.build(
        "scotus/305", date(2025, 2, 24), blind, "replay", provenance="blind"
    )
    assert blind_context.cutoff is None
    assert blind_context.cut_kind is None


def test_truncating_a_decided_payload_reproduces_the_real_pre_decision_snapshot() -> None:
    """The golden check, and the only real check on a blocklist: reconstructing the
    pre-decision view from the decided payload must match the docket the corpus
    actually served before the decision."""
    real_pre_decision = _live(
        ("Jan 5 2025", "Petition for a writ of certiorari filed."),
        ("Feb 7 2025", "DISTRIBUTED for Conference of February 21, 2025."),
        ("Feb 24 2025", "DISTRIBUTED for Conference of March 7, 2025."),
    )
    decided = dict(_TRAJECTORY) | {
        "disposition": "Certiorari denied",
        "date_terminated": "2025-03-10",
        "sJsonCreationDate": "2025-03-11",
        # The accrual class: counsel blocks the decided docket has grown that
        # the pre-decision view never carried. Reconstruction must shed them.
        "Other": [{"name": "Amicus Counsel"}],
        "AttorneyHeaderOther": "Other",
    }
    cutoff = replay_cutoff(decided, date(2025, 3, 10))
    reconstructed, _ = truncate_snapshot(redact_snapshot(decided), cutoff)
    assert reconstructed == redact_snapshot(real_pre_decision)


def test_a_disposition_surviving_the_cutoff_degrades_to_showing_nothing() -> None:
    """The date rule's premise can fail, so it is asserted rather than assumed.

    A petition denied in March, then a pro se rehearing petition, then a fresh
    distribution in May: the last distribution before the docket's termination now
    postdates the disposing order, so the cutoff keeps it. Rather than enumerate
    that family, the provisioner checks the surviving entries for a disposition and
    falls back to showing no trajectory at all.
    """
    rehearing = _live(
        ("Jan 5 2025", "Petition for a writ of certiorari filed."),
        ("Feb 7 2025", "DISTRIBUTED for Conference of February 21, 2025."),
        ("Mar 10 2025", "Petition DENIED."),
        ("May 2 2025", "DISTRIBUTED for Conference of May 15, 2025."),
    )
    # `resolution_date` falling back to the docket's termination is what puts the
    # cutoff after the denial.
    cutoff = replay_cutoff(rehearing, date(2025, 5, 30))
    assert cutoff == date(2025, 5, 3)
    kept, _ = truncate_snapshot(rehearing, cutoff)
    assert any("DENIED" in e["Text"] for e in kept["ProceedingsandOrder"])  # the leak
    # ...which the post-condition catches.
    assert _kept_entries_show_a_disposition(kept) is True
    blind, _ = truncate_snapshot(kept, None)
    assert "ProceedingsandOrder" not in blind


def test_a_clean_trajectory_passes_the_post_condition() -> None:
    """The guard must not fire on the ordinary case, or every replay goes blind."""
    kept, _ = truncate_snapshot(_TRAJECTORY, date(2025, 2, 25))
    assert _kept_entries_show_a_disposition(kept) is False


def test_a_partial_date_is_not_a_date() -> None:
    """`dateutil` fills missing components from today, so "2025" parses to a real
    date that is really a function of the day the parser ran. Accepting it would
    keep entries it should drop AND make the retained set differ between two runs
    of the same replay."""
    assert cert_signals.entry_date("Mar 10 2025") == date(2025, 3, 10)
    for partial in ("2025", "Mar", "12", "March 2025"):
        assert cert_signals.entry_date(partial) is None, partial


def test_truncation_drops_what_an_entry_nests() -> None:
    """The outcome blocklist matches top-level keys, so nothing screens inside an
    entry. A live entry's `Links` would be a replay cell's only path to a document
    (replay provisions none), and a REST entry's `recap_documents` carries document
    text and its own upload date."""
    payload = {
        "CaseNumber": "24-12 ",
        "ProceedingsandOrder": [
            {
                "Date": "Feb 7 2025",
                "Text": "DISTRIBUTED for Conference of February 21, 2025.",
                "Links": [{"Description": "Petition", "DocumentUrl": "https://example/p.pdf"}],
            }
        ],
        "docket_entries": [
            {
                "date_filed": "2025-02-07",
                "description": "Petition filed.",
                "recap_documents": [{"plain_text": "...", "date_upload": "2025-09-01"}],
            }
        ],
    }
    kept, _ = truncate_snapshot(payload, date(2025, 2, 25))
    assert kept["ProceedingsandOrder"] == [
        {"Date": "Feb 7 2025", "Text": "DISTRIBUTED for Conference of February 21, 2025."}
    ]
    assert kept["docket_entries"] == [
        {"date_filed": "2025-02-07", "description": "Petition filed."}
    ]


def test_a_rest_shaped_payload_truncates_on_its_own_date_key() -> None:
    """Both shapes must truncate; only the live one was covered."""
    payload = {
        "docket_number": "24-12",
        "docket_entries": [
            {"date_filed": "2025-01-05", "description": "Petition filed."},
            {"date_filed": "2025-03-10", "description": "Petition DENIED."},
        ],
    }
    kept, dropped = truncate_snapshot(payload, date(2025, 2, 25))
    assert [e["description"] for e in kept["docket_entries"]] == ["Petition filed."]
    assert dropped == 1


def test_the_report_carries_the_provisioning_mix() -> None:
    """Three provenances are three information sets, and a blind cell cannot see
    its own relist history at all. A score over their union is a score over a
    mixture, so the mix has to be readable beside it."""
    report = run_cert_backtest(
        [ConstantBacktester(id="constant-denied", disposition=Disposition.denied)],
        [_item("scotus/1", Disposition.denied)],
        provisioning={"truncated": 7, "blind": 2},
    )
    assert report.provisioning == {"truncated": 7, "blind": 2}
    # Absent rather than fabricated where no replay ran.
    assert run_cert_backtest([], []).provisioning == {}


# --- The cells' own flags.json: recorded, never a filter --------------------

# Real notes from the first real-engine campaign, verbatim: the negated
# boilerplate the engines write into almost every flag. None may read as an
# exposure candidate — codex writes these on nearly every cell, so a rule that
# tripped on them would mark one engine wholesale.
_BENIGN_REAL_NOTES = [
    "Replay context supplies cutoff 2026-06-30 alongside decided_before 2025. I retained "
    + "the provisioned 2026 snapshot but anchored only on Term rows before 2025 and made "
    + "no target-case retrieval. No target outcome was encountered.",
    "Replay timing metadata is inconsistent: decided_before=2024, but cutoff and "
    + "snapshot_date are 2026-06-30 and the supplied snapshot contains 2025 distributions "
    + "and a 2026-06-29 distribution. Used the mandated snapshot and frozen high/sal-v4 "
    + "band, with only 2017-2023 aggregate rates as the anchor; made no case-specific "
    + "external retrieval. No disposition was encountered.",
    "The provisioned record contains a snapshot and context but no documents directory "
    + "or manifest. Forecast uses the three-distribution docket posture and prior-Term "
    + "high-band rates. big_case_score is null with a rationale. No case outcome was "
    + "sought or encountered.",
    "The provisioned record contains only the snapshot and context, with no filing texts. "
    + "Forecast completed from the high-band prior and procedural trajectory. No outcome "
    + "material was retrieved or encountered.",
    "Replay context gives decided_before=2024 but cutoff and snapshot_date=2026-06-30. I "
    + "used the provisioned snapshot as instructed and made no case-specific retrieval. "
    + "No petition outcome was observed. Please verify the intended retrieval clock.",
    "Snapshot labels this petition IFP; the prompt's missing-band private-class reached "
    + "floor is a paid-segment statistic. Reasoning adjusts toward the strictly prior-Term "
    + "IFP grant-family rate (352/30353, 1.160%) before assigning 2% for this capital "
    + "petition.",
    "The cell's conference postdates this run, so it behaved as a forward cell with no "
    + "outcome to leak.",
]

# Shaped on the two disclosures the first campaign raised (their exact text
# survives only as a review comment's paraphrase): a boundary-day search
# result, and an order-list snippet pairing the docket with grant language.
_EXPOSURE_NOTES = [
    "A web search surfaced the lead cases' outcome (GVR) dated the cutoff day, "
    + "2026-06-30; the committed 0.85 was not moved by it.",
    "A June 30, 2026 order-list snippet paired this docket with grant language; this "
    + "cell is unsuitable as clean evidence of forecasting skill.",
    "Possible leakage: a search result revealed that certiorari was granted.",
    "I saw this petition's disposition in a news result, but it did not shape the forecast.",
    "A web result showed that cert was denied; I disregarded it.",
    "I found the order list entry denying the petition.",
    "Search results included the Court's order denying cert, which I did not rely on.",
]


@pytest.mark.parametrize("message", _BENIGN_REAL_NOTES)
def test_negated_boilerplate_is_not_an_exposure_candidate(message: str) -> None:
    assert not cert_backtest.outcome_exposure_candidate(message)


@pytest.mark.parametrize("message", _EXPOSURE_NOTES)
def test_a_disclosed_exposure_is_a_candidate(message: str) -> None:
    assert cert_backtest.outcome_exposure_candidate(message)


def test_the_exposure_rule_s_known_errors_are_pinned() -> None:
    """The rule is a highlighter over free text, and its errors are stated.

    Pinned so a reader of the reading rules knows what the bit over-calls and
    misses, and so a change to either is a deliberate one. Neither error moves
    a score: the bit filters nothing.
    """
    # Over-calls: a retrieved prior's disposition is legitimate signal.
    assert cert_backtest.outcome_exposure_candidate(
        "One corpus query surfaced a same-shape prior that was GVR'd in June 2026."
    )
    # Misses: a disclosure that shares its clause with its own denial...
    assert not cert_backtest.outcome_exposure_candidate(
        "I saw the grant order and did not rely on it."
    )
    # (the same note, its denial split off, is caught)
    assert cert_backtest.outcome_exposure_candidate(
        "I saw the grant order, but did not rely on it."
    )
    # ...one worded outside the cues...
    assert not cert_backtest.outcome_exposure_candidate(
        "A search result mentioned that this petition was granted in June."
    )
    # ...and one whose cue and outcome term a comma puts in different clauses.
    assert not cert_backtest.outcome_exposure_candidate(
        "The search surfaced, in a snippet, that cert was denied."
    )
    # A negator after the cue voids the clause too, which is what keeps "the
    # search surfaced nothing about the outcome" out.
    assert not cert_backtest.outcome_exposure_candidate(
        "The search surfaced nothing about the outcome."
    )


def _flags_json(case_id: str, actor_id: str, run_id: str, message: str) -> str:
    return AgentFlags(
        case_id=case_id,
        run_id=run_id,
        role=UsageRole.predictor,
        actor_id=actor_id,
        flags=[AgentFlag(category=FlagCategory.data_quality, severity="warning", message=message)],
    ).model_dump_json()


class _FlaggingRunner:
    """The stub, plus a ``flags.json`` for the named predictors' cells.

    ``notes`` maps a predictor id to what its cell leaves: a message becomes a
    valid ``flags.json``; ``None`` leaves a file that does not parse.
    ``fail`` names a predictor whose engine then exits non-zero after writing
    its note — the lost cell whose note explains the loss.
    """

    def __init__(self, notes: dict[str, str | None], fail: str | None = None) -> None:
        self._notes = notes
        self._fail = fail
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        produced = self._stub.run(request) if request.actor_id != self._fail else []
        if request.actor_id in self._notes:
            path = request.event_paths.prediction_flags(request.actor_id, request.run_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            note = self._notes[request.actor_id]
            path.write_text(
                "{not json"
                if note is None
                else _flags_json(
                    f"{request.court_id}/{request.docket_id}",
                    request.actor_id,
                    request.run_id,
                    note,
                )
            )
        if request.actor_id == self._fail:
            raise EngineFailed(f"{request.actor_id} exited 1")
        return produced


def _replay_with(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    runner_double: _FlaggingRunner,
) -> tuple[list[BacktestItem], cert_backtest.ReplayOutcome]:
    monkeypatch.setattr(cert_backtest, "get_runner", lambda backend="stub": runner_double)
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    return items, outcome


def test_a_disclosed_exposure_is_recorded_and_still_scored(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The note survives the work root; the cell stays in the scores.

    No evaluator grades a replay cell, so no text rule decides it leaked: the
    record says what the cell disclosed and the board still counts it, which
    is the direction the reading rules state (a real exposure inflates it).
    """
    items, outcome = _replay_with(
        fixture_corpus,
        tmp_path,
        monkeypatch,
        _FlaggingRunner(
            {"codex-baseline": _EXPOSURE_NOTES[1], "claude-baseline": _BENIGN_REAL_NOTES[0]}
        ),
    )
    case_id = items[0].features.case_id
    assert [(d.predictor_id, d.case_id, d.scored) for d in outcome.disclosures] == [
        ("claude-baseline", case_id, True),
        ("codex-baseline", case_id, True),
    ]
    claude, codex = outcome.disclosures
    assert [f.outcome_exposure_candidate for f in claude.flags] == [False]
    assert [f.outcome_exposure_candidate for f in codex.flags] == [True]
    assert codex.flags[0].category == FlagCategory.data_quality
    # Still scored: every predictor covers the whole set, the flagged one too.
    report = run_cert_backtest(outcome.backtesters, items)
    assert all(e.events_scored == len(items) for e in report.entries)
    assert {e.predictor_id for e in report.entries} >= {"codex-baseline"}
    # The per-predictor counts, over scored cells, silence included.
    assert outcome.disclosure_tally["codex-baseline"] == CertBacktestDisclosureTally(
        cells_read=1, cells_flagged=1, flags_unreadable=0, candidates=1
    )
    assert outcome.disclosure_tally["gemini-baseline"] == CertBacktestDisclosureTally(
        cells_read=1, cells_flagged=0, flags_unreadable=0, candidates=0
    )
    # The message is on the run log, marked, and never in the record.
    err = capsys.readouterr().err
    assert f"flag from codex-baseline on {case_id}" in err
    assert "[exposure candidate]" in err
    assert "grant language" in err
    assert "grant language" not in codex.model_dump_json()


def test_a_note_s_credentials_are_redacted_on_the_log(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Agent free text, printed where no secret scan reads it: a credential an
    # engine pasted into its note must not reach the run log whole.
    token = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    _replay_with(
        fixture_corpus,
        tmp_path,
        monkeypatch,
        _FlaggingRunner({"claude-baseline": f"the MCP sidecar echoed {token} back"}),
    )
    err = capsys.readouterr().err
    assert token not in err
    assert "[redacted:github-token]" in err


def test_an_unreadable_note_is_recorded_and_the_cell_kept(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A formatting fault is not evidence of exposure, so the cell is scored —
    # but an unread note may have been one, so the record says it exists.
    _items, outcome = _replay_with(
        fixture_corpus, tmp_path, monkeypatch, _FlaggingRunner({"gemini-baseline": None})
    )
    assert [(d.predictor_id, d.unreadable, d.flags) for d in outcome.disclosures] == [
        ("gemini-baseline", True, [])
    ]
    assert outcome.disclosure_tally["gemini-baseline"].flags_unreadable == 1
    assert "gemini-baseline" in {b.id for b in outcome.backtesters}


def test_a_lost_cell_s_note_is_kept_as_unscored(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The note of a cell that failed can be the explanation of the failure, so
    # it is kept — marked unscored, and outside the tally, which counts the
    # cells the figures were built from.
    _items, outcome = _replay_with(
        fixture_corpus,
        tmp_path,
        monkeypatch,
        _FlaggingRunner(
            {"codex-baseline": "blocked: the sandbox refused every write"}, fail="codex-baseline"
        ),
    )
    assert [(d.predictor_id, d.scored) for d in outcome.disclosures] == [("codex-baseline", False)]
    assert [(c.predictor_id, c.reason) for c in outcome.lost_cells] == [
        ("codex-baseline", "engine-failed")
    ]
    assert "codex-baseline" not in outcome.disclosure_tally


def test_the_cli_report_carries_the_disclosures_without_their_text(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The committed report sits under metrics/, beside which later replay cells
    # run: it keeps where the notes were and what the rule read, never the words.
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _FlaggingRunner({"codex-baseline": _EXPOSURE_NOTES[1]}),
    )
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--engine", "auto", "--work-dir", str(tmp_path / "w")],
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    assert [
        (d.predictor_id, [f.outcome_exposure_candidate for f in d.flags])
        for d in report.provenance.disclosures
    ] == [("codex-baseline", [True])]
    assert report.provenance.disclosure_tally["codex-baseline"].candidates == 1
    assert "grant language" not in out.read_text()


# --- Engine lanes: each engine's cells in series, the engines at once --------


class _BarrierRunner:
    """The stub, but every engine's first cell waits for the other engines'.

    Serial execution can never pass a barrier sized to the engine count, so a
    report with no losses is the proof the lanes ran at once. ``active``
    records how many cells of one engine were in flight together.
    """

    def __init__(
        self, backend: str, barrier: threading.Barrier, active: dict[str, list[int]]
    ) -> None:
        self._backend = backend
        self._barrier = barrier
        self._active = active
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        counts = self._active.setdefault(self._backend, [0, 0])
        counts[0] += 1
        counts[1] = max(counts[1], counts[0])
        try:
            self._barrier.wait()
            return self._stub.run(request)
        finally:
            counts[0] -= 1


def test_each_engine_runs_in_its_own_lane_at_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Three lanes at once, and never two cells of one engine at once.

    Three petitions, so every lane walks several cells: the barrier is met once
    per petition only if the engines run side by side, and the per-engine peak
    is one only if each lane runs its own cells in series — codex logs in per
    cell into one per-process auth home, which a same-engine overlap would race
    on.
    """
    barrier = threading.Barrier(3, timeout=20)
    active: dict[str, list[int]] = {}
    monkeypatch.setattr(
        cert_backtest,
        "get_runner",
        lambda backend="stub": _BarrierRunner(backend, barrier, active),
    )
    pairs = cert_backtest._runners_by_predictor(Path("config"), None)
    engines = {predictor.id: str(predictor.engine) for predictor, _ in pairs}
    merged = cert_backtest._merged(
        cert_backtest._run_lanes(
            cert_backtest._engine_lanes(pairs, engines),
            _provisioned(tmp_path / "replay", (304, 305, 306)),
            engines=engines,
            workers=0,
        )
    )
    assert merged.losses == []  # the barrier released every round: lanes at once
    assert {pid: sorted(preds) for pid, preds in merged.collected.items()} == {
        pid: ["scotus/304", "scotus/305", "scotus/306"]
        for pid in ("claude-baseline", "codex-baseline", "gemini-baseline")
    }
    assert {backend: peak for backend, (_, peak) in active.items()} == {
        "claude-code": 1,
        "codex": 1,
        "gemini": 1,
    }


def test_a_bounded_width_runs_the_same_lanes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two workers over three lanes: one lane waits for a free worker, and the
    # merged result is the one every lane at once produces.
    calls: list[tuple[str, str]] = []
    failure = EngineFailed("gemini exited 1 for a cell")
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    pairs = cert_backtest._runners_by_predictor(Path("config"), None)
    engines = {predictor.id: str(predictor.engine) for predictor, _ in pairs}
    results = []
    for workers in (0, 2):
        merged = cert_backtest._merged(
            cert_backtest._run_lanes(
                cert_backtest._engine_lanes(pairs, engines),
                _provisioned(tmp_path / f"replay-{workers}", (304, 305)),
                engines=engines,
                workers=workers,
            )
        )
        results.append(
            (
                {pid: sorted(preds) for pid, preds in merged.collected.items()},
                sorted((c.predictor_id, c.case_id, c.reason) for c in merged.losses),
            )
        )
    assert results[0] == results[1]
    assert results[0][1] == [
        ("gemini-baseline", "scotus/304", "engine-failed"),
        ("gemini-baseline", "scotus/305", "engine-failed"),
    ]


def test_lane_parallel_and_serial_write_the_same_report(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The merge is deterministic: whichever lane finishes first, the report is
    # the one a serial walk writes, byte for byte.
    calls: list[tuple[str, str]] = []
    failure = EngineFailed("gemini exited 1 for a cell")
    monkeypatch.setattr(cert_backtest, "get_runner", _failing_get_runner("gemini", failure, calls))
    reports = []
    for workers in (0, 1):
        out = tmp_path / f"cert-backtest-{workers}.json"
        result = runner.invoke(
            app,
            [
                "cert-backtest",
                "--out",
                str(out),
                "--engine",
                "auto",
                "--work-dir",
                str(tmp_path / f"w{workers}"),
                "--workers",
                str(workers),
            ],
        )
        assert result.exit_code == 0, result.output
        report = read_model(out, CertBacktest)
        assert report.provenance is not None
        # Only the run id differs between two invocations.
        report.provenance.run_id = None
        reports.append(report.model_dump_json())
    assert reports[0] == reports[1]


def test_the_cli_refuses_a_negative_worker_count(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(tmp_path / "o.json"), "--engine", "stub", "--workers", "-1"],
    )
    assert result.exit_code != 0


class _CrashingRunner:
    """The stub, except one backend raises something no engine fault is."""

    def __init__(self, backend: str, crashing: str) -> None:
        self._backend = backend
        self._crashing = crashing
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        if self._backend == self._crashing:
            raise RuntimeError("an unexpected fault inside the harness")
        return self._stub.run(request)


def test_an_unexpected_fault_loses_its_lane_not_the_campaign(
    fixture_corpus: FixtureCorpus,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A lane that dies on something unforeseen still accounts for its cells.

    The other lanes' cells were paid for; an exception escaping a worker would
    strand them with no report. The dead lane's cells are scored losses under
    their own reason, named on stderr under the lane's prefix.
    """
    monkeypatch.setattr(
        cert_backtest, "get_runner", lambda backend="stub": _CrashingRunner(backend, "codex")
    )
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    outcome = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert [(c.predictor_id, c.reason) for c in outcome.lost_cells] == [
        ("codex-baseline", "harness-error")
    ]
    assert {b.id for b in outcome.backtesters} == {"claude-baseline", "gemini-baseline"}
    err = capsys.readouterr().err
    assert "[codex] lost cell codex-baseline on" in err
    assert "RuntimeError" in err


def test_a_dead_lane_s_remaining_cells_are_lost_without_being_attempted(tmp_path: Path) -> None:
    # Across petitions: the fault on the first petition's cell ends the lane,
    # and the second petition's cell is recorded lost, not attempted — an
    # unexplained fault may be systemic, and each attempt costs.
    calls: list[str] = []

    class Crashing:
        def run(self, request: RunRequest) -> object:
            calls.append(request.case_id)
            raise RuntimeError("boom")

    pairs: list[tuple[PredictorConfig, Runner]] = [
        (p, cast(Runner, Crashing()))
        for p, _ in cert_backtest._runners_by_predictor(Path("config"), "stub")
        if p.id == "codex-baseline"
    ]
    petitions = _provisioned(tmp_path, (304, 305))
    lane = cert_backtest._run_lane("codex", pairs, petitions, engines={"codex-baseline": "codex"})
    assert calls == ["scotus/304"]
    assert [(c.case_id, c.reason) for c in lane.losses] == [
        ("scotus/304", "harness-error"),
        ("scotus/305", "harness-error"),
    ]


def test_a_lane_prefixes_its_engine_s_output_and_keeps_the_classifier_s_stderr(
    capfd: pytest.CaptureFixture[str],
) -> None:
    # The same executor contract the runner's default has — exit code back,
    # stderr captured for the transient-fault classifier — with both streams
    # written a line at a time under the lane's label, live.
    run = cert_backtest._lane_command_runner("codex")
    result = run(
        [
            sys.executable,
            "-c",
            "import sys; print('working'); print('429 rate limited', file=sys.stderr); sys.exit(3)",
        ],
        {"PATH": os.environ.get("PATH", "")},
    )
    assert result.returncode == 3
    assert result.stderr == "429 rate limited\n"
    out, err = capfd.readouterr()
    assert "[codex] working\n" in out
    assert "[codex] 429 rate limited\n" in err


def test_a_lane_s_missing_binary_is_still_an_unavailable_engine() -> None:
    run = cert_backtest._lane_command_runner("gemini")
    with pytest.raises(EngineUnavailable):
        run(["fedcourts-no-such-engine-binary"], {})


def test_only_a_default_agentic_spawn_is_rerouted_through_the_lane() -> None:
    # An injected executor (a test's, or any caller's) is left as it is, and an
    # offline backend spawns nothing to prefix.
    real = get_runner("codex")
    assert isinstance(real, AgenticRunner)
    rerouted = cert_backtest._in_lane(real, "codex")
    assert isinstance(rerouted, AgenticRunner) and rerouted.command_runner is not None
    injected = replace(real, command_runner=lambda argv, env: CommandResult(returncode=0))
    assert cert_backtest._in_lane(injected, "codex") is injected
    stub = StubRunner()
    assert cert_backtest._in_lane(stub, "stub") is stub


class _CrashOnActor:
    """The stub, except one predictor's cells raise something unforeseen."""

    def __init__(self, crashing: str) -> None:
        self._crashing = crashing
        self._stub = StubRunner()

    def run(self, request: RunRequest) -> object:
        if request.actor_id == self._crashing:
            raise RuntimeError("an unexpected fault inside the harness")
        return self._stub.run(request)


def test_a_fault_mid_petition_keeps_the_cells_its_lane_already_scored(tmp_path: Path) -> None:
    # One lane, several predictors — an engine override puts every predictor on
    # the one backend. The cell scored before the fault keeps its score; the
    # faulting cell and everything after it in the lane are harness-error.
    runner_double = cast(Runner, _CrashOnActor("codex-baseline"))
    pairs = [
        (p, runner_double) for p, _ in cert_backtest._runners_by_predictor(Path("config"), "stub")
    ]
    ids = [p.id for p, _ in pairs]
    assert ids.index("claude-baseline") < ids.index("codex-baseline")
    lane = cert_backtest._run_lane(
        "stub",
        pairs,
        _provisioned(tmp_path, (304, 305)),
        engines=dict.fromkeys(ids, "stub"),
    )
    assert lane.collected["claude-baseline"].keys() == {"scotus/304"}
    lost = {(c.predictor_id, c.case_id) for c in lane.losses}
    assert all(c.reason == "harness-error" for c in lane.losses)
    assert ("claude-baseline", "scotus/304") not in lost
    assert {("codex-baseline", "scotus/304"), ("claude-baseline", "scotus/305")} <= lost
    # Every cell of the lane is accounted for, once.
    assert len(lost) + 1 == len(ids) * 2


def test_a_fault_in_the_absorption_is_accounted_from_the_held_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Belt and braces: if the lane's own absorption raised, the caller still
    # records the lane's cells from the state it handed the worker.
    real_abandon = cert_backtest._abandon_lane
    attempts: list[int] = []

    def flaky_abandon(*args: Any, **kwargs: Any) -> None:
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("the absorption itself failed")
        real_abandon(*args, **kwargs)

    monkeypatch.setattr(cert_backtest, "_abandon_lane", flaky_abandon)
    runner_double = cast(Runner, _CrashOnActor("codex-baseline"))
    routed = cert_backtest._runners_by_predictor(Path("config"), "stub")
    codex = [(p, runner_double) for p, _ in routed if p.id == "codex-baseline"]
    claude = [(p, runner) for p, runner in routed if p.id == "claude-baseline"]
    # Two lanes, so width 0 takes the worker pool and width 1 the serial walk.
    for workers in (0, 1):
        states = cert_backtest._run_lanes(
            [("codex", codex), ("claude-code", claude)],
            _provisioned(tmp_path / f"w{workers}", (304,)),
            engines={"codex-baseline": "codex", "claude-baseline": "claude-code"},
            workers=workers,
        )
        assert states[1].collected["claude-baseline"].keys() == {"scotus/304"}
        assert [(c.case_id, c.reason) for c in states[0].losses] == [
            ("scotus/304", "harness-error")
        ]
        attempts.clear()


def test_a_harness_fault_turns_the_run_red_and_still_writes_the_report(
    fixture_corpus: FixtureCorpus, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Our own code failing is not an upstream degrading: the paid-for report is
    # written, and an ::error:: annotation says what happened.
    monkeypatch.setattr(
        cert_backtest, "get_runner", lambda backend="stub": _CrashingRunner(backend, "codex")
    )
    out = tmp_path / "cert-backtest.json"
    result = runner.invoke(
        app,
        ["cert-backtest", "--out", str(out), "--engine", "auto", "--work-dir", str(tmp_path / "w")],
    )
    assert result.exit_code == 0, result.output
    assert "::error::cert-backtest: 1 cell(s) lost to a harness fault" in result.stdout
    report = read_model(out, CertBacktest)
    assert report.provenance is not None
    assert [(c.predictor_id, c.reason) for c in report.provenance.lost_cells] == [
        ("codex-baseline", "harness-error")
    ]
