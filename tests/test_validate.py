"""Corpus-integrity + referential validation: the checks, the library, and the CLI."""

from datetime import date, datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    CorpusValidation,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    Outcome,
    Prediction,
    SeedProgress,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.validate import (
    CHECK_EVALUATION_TARGETS,
    CHECK_LEDGER_REFERENCES,
    CHECK_REQUIRED_COLUMNS,
    CHECK_ROW_COUNT_MONOTONIC,
    CHECK_SEED_CURSOR,
    CHECK_SNAPSHOT_NOT_FUTURE,
    run_corpus_validation,
)

runner = CliRunner()

TODAY = date(2026, 6, 27)


def _verdict_by_check(verdict: CorpusValidation) -> dict[str, bool]:
    return {c.name: c.passed for c in verdict.checks}


def _seed_corpus(db: Path) -> None:
    """A small, clean corpus: one case, one event, one (past-dated) snapshot."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="ca9/1", court="ca9", disposition=Disposition.granted)],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id="evt-motion-stay",
                    case_id="ca9/1",
                    court="ca9",
                    kind=EventKind.motion,
                )
            ],
        )
        corpus.upsert_snapshot(conn, "ca9/1", date(2026, 1, 1), {"docket": "ca9/1"})


def _write_outcome(data_root: Path, court: str, docket: int, event: str) -> Path:
    ep = CasePaths(data_root, court, docket).event(event)
    outcome = Outcome(
        case_id=f"{court}/{docket}",
        event_id=event,
        resolved_at=date(2026, 1, 2),
        actual_disposition=Disposition.granted,
        actual_granted=1,
    )
    write_json(ep.outcome, outcome)
    return ep.outcome


def _write_prediction(data_root: Path, court: str, docket: int, event: str, predictor: str) -> None:
    ep = CasePaths(data_root, court, docket).event(event)
    prediction = Prediction(
        case_id=f"{court}/{docket}",
        event_id=event,
        predictor_id=predictor,
        engine=Engine.claude_code,
        run_id="2026-01-01T00-00-00Z",
        created_at=datetime(2026, 1, 1),
        input_snapshot="record/snapshots/2026-01-01.json",
        granted=1,
        probability=0.9,
        predicted_disposition=Disposition.granted,
    )
    write_json(ep.prediction(predictor, "2026-01-01T00-00-00Z"), prediction)


def _write_evaluation(
    data_root: Path, court: str, docket: int, event: str, predictor: str, evaluator: str
) -> None:
    ep = CasePaths(data_root, court, docket).event(event)
    evaluation = Evaluation(
        case_id=f"{court}/{docket}",
        event_id=event,
        predictor_id=predictor,
        evaluator_id=evaluator,
        run_id="2026-02-01T00-00-00Z",
        created_at=datetime(2026, 2, 1),
        correct=1,
    )
    write_json(ep.evaluation(evaluator, predictor, "2026-02-01T00-00-00Z"), evaluation)


def _run(db: Path, data_root: Path, **kw: object) -> CorpusValidation:
    return run_corpus_validation(
        corpus_db_path=db,
        data_root=data_root,
        seed_cursor=kw.get("seed_cursor"),  # type: ignore[arg-type]
        today=kw.get("today", TODAY),  # type: ignore[arg-type]
        baseline_count=kw.get("baseline_count"),  # type: ignore[arg-type]
    )


# --- clean corpus -------------------------------------------------------------


def test_clean_corpus_passes(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    _write_prediction(data_root, "ca9", 1, "evt-motion-stay", "p1")
    _write_evaluation(data_root, "ca9", 1, "evt-motion-stay", "p1", "e1")

    verdict = _run(db, data_root, baseline_count=1)
    assert verdict.ok
    assert not verdict.skipped
    assert verdict.corpus_rows == 1
    assert verdict.corpus_events == 1
    assert all(c.passed for c in verdict.checks)


# --- absent corpus ------------------------------------------------------------


def test_absent_corpus_is_skipped(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"  # never created
    verdict = _run(db, tmp_path / "data")
    assert verdict.skipped
    assert verdict.ok
    assert verdict.checks == []


# --- B: append-only row count -------------------------------------------------


def test_non_monotonic_row_count_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # one row
    verdict = _run(db, tmp_path / "data", baseline_count=5)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_ROW_COUNT_MONOTONIC] is False


def test_no_baseline_is_a_pass(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    verdict = _run(db, tmp_path / "data")  # no baseline
    assert _verdict_by_check(verdict)[CHECK_ROW_COUNT_MONOTONIC] is True


# --- B: future-dated snapshot -------------------------------------------------


def test_future_dated_snapshot_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/1", date(2099, 1, 1), {"docket": "ca9/1"})
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_SNAPSHOT_NOT_FUTURE] is False


# --- B: required columns ------------------------------------------------------


def test_empty_court_fails_required_columns(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET court = '' WHERE case_id = 'ca9/1'")
        conn.commit()
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_REQUIRED_COLUMNS] is False


# --- C: orphan ledger references ----------------------------------------------


def test_orphan_outcome_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    # An outcome for an event the corpus does not define.
    _write_outcome(data_root, "ca9", 1, "evt-motion-ghost")
    verdict = _run(db, data_root)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_LEDGER_REFERENCES] is False


def test_orphan_case_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 999, "evt-motion-stay")  # case not in corpus
    verdict = _run(db, data_root)
    assert _verdict_by_check(verdict)[CHECK_LEDGER_REFERENCES] is False


# --- C: evaluation targets a prediction ---------------------------------------


def test_evaluation_without_prediction_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    data_root = tmp_path / "data"
    _seed_corpus(db)
    _write_outcome(data_root, "ca9", 1, "evt-motion-stay")
    # An evaluation of p1, but no prediction by p1 for this event.
    _write_evaluation(data_root, "ca9", 1, "evt-motion-stay", "p1", "e1")
    verdict = _run(db, data_root)
    assert not verdict.ok
    assert _verdict_by_check(verdict)[CHECK_EVALUATION_TARGETS] is False


# --- C: seed cursor reconciliation --------------------------------------------


def test_seed_cursor_desync_fails(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)  # only ca9 has rows
    cursor = SeedProgress.model_validate({"courts": {"ca9": {"offset": 1}, "ca1": {"offset": 100}}})
    verdict = _run(db, tmp_path / "data", seed_cursor=cursor)
    assert not verdict.ok
    cursor_check = next(c for c in verdict.checks if c.name == CHECK_SEED_CURSOR)
    assert not cursor_check.passed
    assert any("ca1" in p for p in cursor_check.problems)


def test_seed_cursor_reconciles(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seed_corpus(db)
    cursor = SeedProgress.model_validate({"courts": {"ca9": {"offset": 1}}})
    verdict = _run(db, tmp_path / "data", seed_cursor=cursor)
    assert _verdict_by_check(verdict)[CHECK_SEED_CURSOR] is True


# --- corpus that does not open ------------------------------------------------


def test_unopenable_corpus_fails_not_crashes(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    db.write_text("this is not a sqlite database")
    verdict = _run(db, tmp_path / "data")
    assert not verdict.ok
    assert not verdict.skipped
    assert [c.name for c in verdict.checks] == ["corpus_opens"]


# --- CLI ----------------------------------------------------------------------


def _cli_env(tmp_path: Path, corpus_root: Path) -> dict[str, str]:
    """A CLI env whose seed cursor points at a fresh (empty) tmp path.

    Without this the cursor falls back to the repo's real ``config/seed-progress.yaml``
    (its path is CWD-relative), which would desync against the tiny test corpus.
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    cursor = tmp_path / "seed-progress.yaml"  # never created -> empty cursor
    (config_root / "tracking.yaml").write_text(f"seed:\n  cursor: {cursor}\n")
    return {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
    }


def test_cli_writes_verdict_and_summary(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    _seed_corpus(db)
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out), "--today", TODAY.isoformat()],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 0, result.output
    assert "corpus-validation: OK" in result.output
    verdict = read_model(out, CorpusValidation)
    assert verdict.ok


def test_cli_absent_corpus_exits_zero(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"  # no corpus.db
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out)],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 0, result.output
    assert "skipped" in result.output
    assert read_model(out, CorpusValidation).skipped


def test_cli_failed_verdict_exits_nonzero(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    _seed_corpus(db)
    out = tmp_path / "verdict.json"
    result = runner.invoke(
        app,
        ["validate-corpus", "--out", str(out), "--baseline-count", "100"],
        env=_cli_env(tmp_path, corpus_root),
    )
    assert result.exit_code == 1, result.output
    assert "corpus-validation: FAIL" in result.output
    # The verdict is still written even though the check failed (loud-not-fatal).
    assert not read_model(out, CorpusValidation).ok
