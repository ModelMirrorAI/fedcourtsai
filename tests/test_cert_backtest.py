"""Cert back-test: selection, redaction, scoring (lift + calibration), and replay."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.backtest import (
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    ConstantBacktester,
)
from fedcourtsai.cert_backtest import (
    redact_snapshot,
    replay_predictors,
    run_cert_backtest,
    select_cert_backtest_set,
)
from fedcourtsai.cli import app
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
            citations=(),
            date_filed=None,
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


def test_replay_runs_the_stub_engine_over_redacted_snapshots(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    work_root = tmp_path / "replay"
    with corpus.connect(fixture_corpus.db_path) as conn:
        items = select_cert_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["scotus/304"]

    backtesters = replay_predictors(
        items,
        corpus_db_path=fixture_corpus.db_path,
        config_root=Path("config"),
        work_root=work_root,
        engine="stub",
        run_id="20260706T000000Z",
    )

    # One replayed backtester per enabled predictor, each covering the whole set.
    expected = {p.id for p in enabled_predictors(Path("config") / "predictors.yaml")}
    assert {b.id for b in backtesters} == expected
    report = run_cert_backtest(backtesters, items)
    assert report.events_scored == 1
    assert {e.predictor_id for e in report.entries} == expected

    # The provisioned tree hides the outcome: the snapshot is redacted and the
    # event definition reads unresolved; nothing was written outside work_root.
    snapshot = next(work_root.rglob("record/snapshots/*.json")).read_text()
    assert "date_terminated" not in snapshot and "Denied" not in snapshot
    event_yaml = next(work_root.rglob("event.yaml")).read_text()
    assert "resolved: false" in event_yaml
    assert not fixture_corpus.data_root.exists()


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
