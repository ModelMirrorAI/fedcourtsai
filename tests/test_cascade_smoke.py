"""Gate smoke: the offline stub cascade over the fixture corpus is validatable.

Drives provision → predict → evaluate → ``validate`` against the deterministic
fixture corpus with no model and no network, so a broken predict/evaluate cell —
an artifact that stops validating, a corpus read seam that stops resolving — fails
here in seconds in ``pytest`` instead of in a labelled CI run.

:mod:`tests.test_cascade` exercises ``run_cascade``'s behaviours case by case;
this is the one compose check the documented gate points at: an open *and* a
resolved case run into a single ledger that passes the same ``fedcourts validate``
the PR gate runs.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from fedcourtsai.pipeline.cascade import CascadeReport, run_cascade

CONFIG_ROOT = Path("config")
RUN = "20260628T120000Z"


def test_stub_cascade_smoke(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    data_root = tmp_path / "data"

    def _run(court: str, docket: int) -> CascadeReport:
        return run_cascade(
            corpus_db_path=db,
            data_root=data_root,
            config_root=CONFIG_ROOT,
            court=court,
            docket=docket,
            run_id=RUN,
        )

    # ca9/101 is resolved → predict + materialize outcome + evaluate;
    # ca9/103 is open → predict only, nothing to score.
    resolved = _run("ca9", 101)
    open_case = _run("ca9", 103)

    assert resolved.valid, resolved.problems
    assert resolved.predictions and resolved.outcomes and resolved.evaluations
    assert open_case.valid, open_case.problems
    assert open_case.predictions and not open_case.outcomes and not open_case.evaluations

    # The compose check: both cases in one ledger pass the gate's own validate CLI.
    result = CliRunner().invoke(app, ["validate", str(data_root)])

    assert result.exit_code == 0, result.output
    assert "valid" in result.output
