"""Cert back-test: selection, redaction, scoring (lift + calibration), and replay."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cert_backtest, corpus
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
