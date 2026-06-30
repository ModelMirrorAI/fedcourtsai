"""The ``local-cascade`` CLI command runs the offline cascade and reports it."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.registry import enabled_evaluators, enabled_predictors

from .conftest import FixtureCorpus

RESOLVED = ["--court", "ca9", "--docket", "101"]

# Fan-out (and thus the reported file counts) is driven by the enabled registry.
_N_PRED = len(enabled_predictors(Path("config") / "predictors.yaml"))
_N_EVAL = len(enabled_evaluators(Path("config") / "evaluators.yaml"))


def test_local_cascade_stub_reports_a_valid_run(fixture_corpus: FixtureCorpus) -> None:
    result = CliRunner().invoke(app, ["local-cascade", *RESOLVED, "--run-id", "20260628T120000Z"])

    assert result.exit_code == 0, result.output
    assert "local-cascade ca9/101 via stub" in result.output
    assert "validate:    OK" in result.output
    assert f"predictions: {_N_PRED * 2} file(s)" in result.output
    assert f"evaluations: {_N_EVAL * _N_PRED * 2} file(s)" in result.output


def test_local_cascade_writes_validatable_artifacts(fixture_corpus: FixtureCorpus) -> None:
    CliRunner().invoke(app, ["local-cascade", *RESOLVED])
    # The same git ledger the cascade produced passes the standalone `validate` gate.
    result = CliRunner().invoke(app, ["validate", str(fixture_corpus.data_root)])
    assert result.exit_code == 0, result.output
    assert "valid" in result.output


def test_local_cascade_rejects_unknown_engine(fixture_corpus: FixtureCorpus) -> None:
    result = CliRunner().invoke(app, ["local-cascade", *RESOLVED, "--engine", "gpt"])
    assert result.exit_code == 2
    assert "unknown runner backend" in result.output


def test_local_cascade_rejects_unknown_case(fixture_corpus: FixtureCorpus) -> None:
    result = CliRunner().invoke(app, ["local-cascade", "--court", "ca9", "--docket", "99999999"])
    assert result.exit_code == 2
    assert "not in the corpus" in result.output
