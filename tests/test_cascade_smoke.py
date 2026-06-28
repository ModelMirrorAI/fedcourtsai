"""Gate smoke: the offline stub cascade over the fixture corpus is validatable.

Drives provision → predict → evaluate → ``validate`` against the deterministic
fixture corpus with no model and no network, so a broken predict/evaluate cell —
an artifact that stops validating, a corpus read seam that stops resolving — fails
here in seconds in ``pytest`` instead of in a labelled CI run. The per-stage suites
prove each stage in isolation (``test_runner`` the stub, ``test_fixture`` the
corpus, ``test_validate`` the gate); this proves they *compose* end to end.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.corpus import corpus_db_path
from fedcourtsai.fixture import build_fixture_corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import run_stub_cascade
from fedcourtsai.schemas import Disposition, Evaluation, Outcome, Prediction
from fedcourtsai.serialize import read_model

RUN = "20260628T120000Z"
EVENT = "evt-appeal-disposition"  # the appeal-disposition event every fixture ca* case carries


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Build the fixture corpus under ``tmp_path`` and return ``(corpus_db, data_root)``."""
    db = build_fixture_corpus(corpus_db_path(tmp_path / "corpus"))
    return db, tmp_path / "data"


def test_open_case_predicts_with_nothing_to_evaluate(tmp_path: Path) -> None:
    # ca9/103 is open (no disposition): the cascade provisions, predicts, and has
    # no outcome to score — the evaluate half is correctly a no-op.
    db, data_root = _fixture(tmp_path)

    report = run_stub_cascade(db, data_root, "ca9", 103, RUN)

    assert report.predictions and not report.outcomes and not report.evaluations
    assert all(p.is_file() for p in report.predictions)
    prediction = read_model(
        CasePaths(data_root, "ca9", 103).event(EVENT).prediction("stub-baseline", RUN), Prediction
    )
    assert prediction.case_id == "ca9/103"
    assert prediction.predicted_disposition == Disposition.denied


def test_resolved_case_runs_the_full_cascade(tmp_path: Path) -> None:
    # ca9/102 is resolved denied: predict, rebuild the corpus outcome, evaluate.
    db, data_root = _fixture(tmp_path)

    report = run_stub_cascade(db, data_root, "ca9", 102, RUN)

    assert report.predictions and report.outcomes and report.evaluations
    event = CasePaths(data_root, "ca9", 102).event(EVENT)
    outcome = read_model(event.outcome, Outcome)
    assert outcome.actual_disposition == Disposition.denied
    # The stub predicts denied; the realized outcome is denied → scored correct.
    evaluation = read_model(report.evaluations[0], Evaluation)
    assert evaluation.predictor_id == "stub-baseline"
    assert evaluation.correct == 1


def test_cascade_artifacts_pass_validate(tmp_path: Path) -> None:
    # The smoke's contract: a cascade over open + resolved cases passes the same
    # `fedcourts validate` the PR gate runs (schema + git-only references).
    db, data_root = _fixture(tmp_path)
    run_stub_cascade(db, data_root, "ca9", 103, RUN)  # open → predict only
    run_stub_cascade(db, data_root, "ca9", 102, RUN)  # resolved → predict + evaluate

    result = CliRunner().invoke(app, ["validate", str(data_root)])

    assert result.exit_code == 0, result.output
    assert "valid" in result.output
