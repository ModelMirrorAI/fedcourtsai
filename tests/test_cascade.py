"""The local cascade drives predict → evaluate → validate end to end, offline.

Exercises :func:`fedcourtsai.pipeline.cascade.run_cascade` over the synthetic
fixture corpus with the offline ``stub`` engine — the acceptance path: valid
artifacts produced end to end with no network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from fedcourtsai import corpus, fixture
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import CascadeError, CascadeReport, run_cascade
from fedcourtsai.schemas import Evaluation, Outcome, PredictableEvent, Prediction
from fedcourtsai.serialize import read_model

CONFIG_ROOT = Path("config")
RUN = "20260628T120000Z"

# A resolved fixture case (granted) and an open one, both in court ca9.
RESOLVED_COURT, RESOLVED_DOCKET = "ca9", 101
RESOLVED_EVENT = "evt-appeal-disposition"
OPEN_COURT, OPEN_DOCKET = "ca9", 103


@pytest.fixture
def corpus_db(tmp_path: Path) -> Path:
    """A freshly built synthetic fixture corpus."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    fixture.build_fixture_corpus(db)
    return db


def _run(
    corpus_db: Path, data_root: Path, court: str, docket: int, **kwargs: object
) -> CascadeReport:
    return run_cascade(
        corpus_db_path=corpus_db,
        data_root=data_root,
        config_root=CONFIG_ROOT,
        court=court,
        docket=docket,
        run_id=RUN,
        **kwargs,  # type: ignore[arg-type]
    )


def test_resolved_case_runs_the_full_cascade(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET)

    assert report.valid, report.problems
    assert report.engine == "stub"
    assert report.events == (RESOLVED_EVENT,)
    # The two enabled predictors each wrote a prediction pair.
    assert len(report.predictions) == 4
    # One ground-truth outcome materialized from the resolved corpus row.
    assert len(report.outcomes) == 1
    # Two evaluators each scored both predictors → 2 x 2 evaluation pairs.
    assert len(report.evaluations) == 8

    events = CasePaths(data_root, RESOLVED_COURT, RESOLVED_DOCKET).event(RESOLVED_EVENT)
    # The git event definition + ground truth the agents read were materialized.
    assert read_model(events.event_file, PredictableEvent).resolved is True
    outcome = read_model(events.outcome, Outcome)
    assert outcome.actual_disposition == "granted"
    # And a real prediction/evaluation pair validates against its schema.
    prediction = read_model(events.prediction("claude-baseline", RUN), Prediction)
    assert prediction.event_id == RESOLVED_EVENT
    evaluation = read_model(events.evaluation("claude-judge", "claude-baseline", RUN), Evaluation)
    # Stub predicted denied; the outcome is granted → scored wrong.
    assert evaluation.correct == 0


def test_snapshot_is_provisioned_to_the_record_path(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET)

    assert report.snapshot is not None
    assert report.snapshot.is_file()
    # record/ is the gitignored provisioning location, never the committed ledger.
    assert "record" in report.snapshot.parts


def test_open_case_predicts_but_evaluates_nothing(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, OPEN_COURT, OPEN_DOCKET)

    # An unresolved case has no outcome, so predictions are produced but there is
    # nothing to score — and the ledger is still valid.
    assert report.valid, report.problems
    assert len(report.predictions) == 4
    assert report.outcomes == ()
    assert report.evaluations == ()


def test_event_filter_selects_one_event(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET, event=RESOLVED_EVENT)
    assert report.events == (RESOLVED_EVENT,)


def test_unknown_event_is_rejected(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with pytest.raises(CascadeError, match="is not defined for this case"):
        _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET, event="evt-motion-nope")


def test_unknown_case_is_rejected(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with pytest.raises(CascadeError, match="not in the corpus"):
        _run(corpus_db, data_root, "ca9", 99999999)


def test_missing_corpus_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(CascadeError, match="no corpus"):
        run_cascade(
            corpus_db_path=tmp_path / "corpus" / "corpus.db",
            data_root=tmp_path / "data",
            config_root=CONFIG_ROOT,
            court=RESOLVED_COURT,
            docket=RESOLVED_DOCKET,
            run_id=RUN,
        )


def test_unknown_engine_is_rejected(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with pytest.raises(KeyError, match="unknown runner backend"):
        _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET, engine="gpt")


def test_cascade_is_deterministic(corpus_db: Path, tmp_path: Path) -> None:
    # Same inputs (incl. run id + output root) → byte-identical prediction artifact.
    data_root = tmp_path / "data"
    prediction = (
        CasePaths(data_root, RESOLVED_COURT, RESOLVED_DOCKET)
        .event(RESOLVED_EVENT)
        .prediction("claude-baseline", RUN)
    )
    _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET)
    first = prediction.read_bytes()
    _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET)
    assert prediction.read_bytes() == first
