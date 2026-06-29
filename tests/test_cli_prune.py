from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app

runner = CliRunner()


def _predictions_dir(data_root: Path, court: str, docket: int, event: str) -> Path:
    base = data_root / "cases" / court / str(docket) / "events" / event
    (base / "event.yaml").parent.mkdir(parents=True)
    (base / "event.yaml").write_text("kind: petition\n")
    pred = base / "predictions" / "claude-baseline" / "20260629T090631Z"
    pred.mkdir(parents=True)
    (pred / "prediction.json").write_text("{}\n")
    return base / "predictions"


@pytest.fixture
def roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """A corpus with one historical-mandatory and one modern SCOTUS row, plus a ledger.

    Both cases carry merged predictions; only the pre-1925 (bare docket number ``801``)
    case is out of scope and should be pruned.
    """
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="scotus/801", court="scotus", docket_number="801"),
                corpus.CorpusRow(
                    case_id="scotus/845",
                    court="scotus",
                    docket_number="22-845",
                    date_filed=date(2024, 1, 8),
                ),
            ],
        )
    _predictions_dir(data_root, "scotus", 801, "evt-petition-disposition")
    _predictions_dir(data_root, "scotus", 845, "evt-petition-disposition")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    return corpus_root, data_root


def test_prune_dry_run_lists_only_historical(roots: tuple[Path, Path]) -> None:
    _, data_root = roots
    result = runner.invoke(app, ["prune-historical-predictions"])
    assert result.exit_code == 0, result.output
    assert "scotus/801" in result.stdout
    assert "scotus/845" not in result.stdout  # modern case stays in scope
    assert "--apply" in result.stdout
    # Dry run touches nothing.
    assert (data_root / "cases/scotus/801/events/evt-petition-disposition/predictions").exists()


def test_prune_apply_removes_only_historical(roots: tuple[Path, Path]) -> None:
    _, data_root = roots
    result = runner.invoke(app, ["prune-historical-predictions", "--apply"])
    assert result.exit_code == 0, result.output
    historical = data_root / "cases/scotus/801/events/evt-petition-disposition"
    modern = data_root / "cases/scotus/845/events/evt-petition-disposition"
    # The out-of-scope predictions are gone; the event.yaml stays.
    assert not (historical / "predictions").exists()
    assert (historical / "event.yaml").exists()
    # The in-scope modern case is untouched.
    assert (modern / "predictions").exists()


def test_prune_no_targets_is_clean(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    data_root = tmp_path / "data"
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/845",
                    court="scotus",
                    docket_number="22-845",
                    date_filed=date(2024, 1, 8),
                )
            ],
        )
    _predictions_dir(data_root, "scotus", 845, "evt-petition-disposition")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    result = runner.invoke(app, ["prune-historical-predictions", "--apply"])
    assert result.exit_code == 0, result.output
    assert "No out-of-scope" in result.stdout
    assert (data_root / "cases/scotus/845/events/evt-petition-disposition/predictions").exists()


def test_prune_missing_corpus_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    result = runner.invoke(app, ["prune-historical-predictions"])
    assert result.exit_code == 1
    assert "No corpus" in result.stderr
