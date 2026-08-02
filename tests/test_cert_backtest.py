"""Cert back-test: selection, redaction, scoring (lift + calibration), and replay."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

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
    replay_cutoff,
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
    truncate_snapshot,
)
from fedcourtsai.cli import app
from fedcourtsai.pipeline import cell_context, cert_signals, ingest
from fedcourtsai.pipeline.runner import EngineUnavailable, RunRequest, StubRunner
from fedcourtsai.registry import enabled_predictors
from fedcourtsai.schemas import CertBacktest, Disposition
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

    backtesters, unavailable, _ = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=work_root,
        engine_override="stub",
        run_id="20260706T000000Z",
    )
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
    backtesters, unavailable, _ = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert unavailable == []
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline", "gemini-baseline"}
    # No cell ever ran on an engine other than its predictor's own.
    routed = {actor: backend for backend, actor in calls}
    assert routed == {
        "claude-baseline": "claude-code",
        "codex-baseline": "codex",
        "gemini-baseline": "gemini",
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
    backtesters, unavailable, _ = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
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
    backtesters, unavailable, _ = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
        skip_engines=frozenset({"gemini"}),
    )
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
    backtesters, unavailable, _ = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
    assert unavailable == ["gemini-baseline"]
    assert {b.id for b in backtesters} == {"claude-baseline", "codex-baseline"}
    assert "gemini" not in {backend for backend, _ in calls}


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
