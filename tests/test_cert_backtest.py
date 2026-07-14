"""Cert back-test: selection, redaction, scoring (lift + calibration), and replay."""

from __future__ import annotations

from datetime import date
from pathlib import Path

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
    redact_snapshot,
    replay_predictors,
    replayable_items,
    run_cert_backtest,
    select_cert_backtest_set,
)
from fedcourtsai.cli import app
from fedcourtsai.pipeline.runner import RunRequest, StubRunner
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
    assert set(redacted) == {"id", "case_name", "docket_number", "date_filed"}


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

    backtesters = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=work_root,
        engine_override="stub",
        run_id="20260706T000000Z",
    )

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
    assert "date_terminated" not in snapshot and "Denied" not in snapshot
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
    backtesters = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
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
    backtesters = cert_backtest.replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=tmp_path / "replay",
        run_id="20260706T000000Z",
    )
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
