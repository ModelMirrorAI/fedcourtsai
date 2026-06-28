"""Back-testing harness: selection, scoring, the reference baselines, and the CLI."""

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.backtest import (
    BacktestFeatures,
    BacktestItem,
    BacktestPrediction,
    ConstantBacktester,
    PriorVoteBacktester,
    default_backtesters,
    run_backtest,
    select_backtest_set,
)
from fedcourtsai.cli import app
from fedcourtsai.schemas import Backtest, Disposition
from fedcourtsai.serialize import read_model
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _row(case_id: str, disposition: Disposition | None, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "disposition": disposition,
        "date_filed": date(2025, 1, 1),
        "date_decided": date(2026, 1, 1) if disposition else None,
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _seed(db: Path, rows: list[corpus.CorpusRow]) -> None:
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


# --- selection ----------------------------------------------------------------


def test_select_keeps_only_machine_readable_resolved(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca9/1", Disposition.granted),
            _row("ca9/2", Disposition.denied),
            _row("ca9/3", None),  # unresolved
            _row("ca9/4", Disposition.other),  # decided but unclassified
        ],
    )
    with corpus.connect(db) as conn:
        items = select_backtest_set(conn)
    assert [i.features.case_id for i in items] == ["ca9/1", "ca9/2"]
    assert items[0].actual_disposition == Disposition.granted


def test_select_features_hide_the_outcome(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(db, [_row("ca9/1", Disposition.granted, opinion_text="grant", summary="won")])
    with corpus.connect(db) as conn:
        item = select_backtest_set(conn)[0]
    # Features carry no field that reveals the disposition (no opinion/summary/date_decided).
    assert set(vars(item.features)) == {
        "case_id",
        "court",
        "topic",
        "judges",
        "citations",
        "date_filed",
    }


def test_select_court_and_limit_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca1/1", Disposition.granted, court="ca1"),
            _row("ca9/1", Disposition.granted),
            _row("ca9/2", Disposition.denied),
        ],
    )
    with corpus.connect(db) as conn:
        assert [i.features.case_id for i in select_backtest_set(conn, court="ca9")] == [
            "ca9/1",
            "ca9/2",
        ]
        assert len(select_backtest_set(conn, limit=1)) == 1


# --- reference baselines ------------------------------------------------------


def _features(case_id: str = "ca9/1", **kw: object) -> BacktestFeatures:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "topic": None,
        "judges": (),
        "citations": (),
        "date_filed": date(2025, 1, 1),
    }
    base.update(kw)
    return BacktestFeatures(**base)  # type: ignore[arg-type]


def test_constant_backtester_is_constant() -> None:
    bt = ConstantBacktester(id="constant-denied", disposition=Disposition.denied)
    pred = bt.predict(_features())
    assert pred == BacktestPrediction(Disposition.denied, 0.0)
    granted = ConstantBacktester(id="c", disposition=Disposition.granted).predict(_features())
    assert granted.probability_granted == 1.0


def test_prior_vote_majority_and_granted_share(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed(
        db,
        [
            _row("ca9/10", Disposition.granted, judges=["smith"]),
            _row("ca9/11", Disposition.granted, judges=["smith"]),
            _row("ca9/12", Disposition.denied, judges=["smith"]),
        ],
    )
    with corpus.connect(db) as conn:
        bt = PriorVoteBacktester(conn)
        pred = bt.predict(_features("ca9/99", judges=("smith",)))
    # 2 granted / 1 denied among the priors -> majority granted, P(granted)=2/3.
    assert pred.predicted_disposition == Disposition.granted
    assert pred.probability_granted == 2 / 3


def test_prior_vote_excludes_the_case_under_test(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    # The only resolved case is the one being predicted; leave-one-out leaves no prior.
    _seed(db, [_row("ca9/1", Disposition.granted, judges=["smith"])])
    with corpus.connect(db) as conn:
        pred = PriorVoteBacktester(conn).predict(_features("ca9/1", judges=("smith",)))
    assert pred == BacktestPrediction(Disposition.denied, 0.0)


# --- scoring ------------------------------------------------------------------


def _item(case_id: str, actual: Disposition) -> BacktestItem:
    return BacktestItem(_features(case_id), actual)


def test_run_backtest_scores_and_ranks() -> None:
    items = [
        _item("ca9/1", Disposition.denied),
        _item("ca9/2", Disposition.denied),
        _item("ca9/3", Disposition.granted),
    ]
    always_denied = ConstantBacktester(id="denied", disposition=Disposition.denied)
    always_granted = ConstantBacktester(id="granted", disposition=Disposition.granted)
    report = run_backtest([always_granted, always_denied], items)
    assert report.predictors_evaluated == 2
    assert report.events_scored == 3
    # always-denied gets 2/3 dispositions right; always-granted 1/3 -> denied ranks first.
    assert [e.predictor_id for e in report.entries] == ["denied", "granted"]
    denied = report.entries[0]
    assert denied.rank == 1
    assert denied.accuracy == 2 / 3
    assert denied.granted_accuracy == 2 / 3
    # Brier: denied predicts P=0; two actual-denied (0) + one actual-granted (1) -> 1/3.
    assert denied.mean_brier_score == 1 / 3


def test_run_backtest_empty_is_zero_count() -> None:
    report = run_backtest([], [])
    assert report.predictors_evaluated == 0
    assert report.events_scored == 0
    assert report.entries == []


def test_default_backtesters_are_the_reference_baselines(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        ids = [bt.id for bt in default_backtesters(conn)]
    assert ids == ["constant-denied", "prior-vote"]


# --- CLI ----------------------------------------------------------------------


def test_cli_writes_valid_report(fixture_corpus: FixtureCorpus, tmp_path: Path) -> None:
    out = tmp_path / "backtest.json"
    result = runner.invoke(app, ["backtest", "--out", str(out)])
    assert result.exit_code == 0, result.output
    report = read_model(out, Backtest)
    # Every machine-readable resolved fixture case is a back-test trial (the
    # fixture carries no `other`-disposition rows, so resolved == scored).
    expected = sum(1 for c in fixture.FIXTURE_CASES if c.disposition is not None)
    assert report.events_scored == expected
    assert report.predictors_evaluated == 2
    assert {e.predictor_id for e in report.entries} == {"constant-denied", "prior-vote"}
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    runner.invoke(app, ["backtest", "--out", str(out)])
    assert out.read_text() == first


def test_cli_missing_corpus_writes_empty_report(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"  # no corpus.db created
    out = tmp_path / "backtest.json"
    result = runner.invoke(
        app,
        ["backtest", "--out", str(out)],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_root)},
    )
    assert result.exit_code == 0, result.output
    report = read_model(out, Backtest)
    assert report.predictors_evaluated == 0
    assert report.events_scored == 0
    assert report.entries == []
