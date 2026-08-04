"""The local cascade drives predict → evaluate → validate end to end, offline.

Exercises :func:`fedcourtsai.pipeline.cascade.run_cascade` over the synthetic
fixture corpus with the offline ``stub`` engine — the acceptance path: valid
artifacts produced end to end with no network.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus, fixture
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import (
    CascadeError,
    CascadeReport,
    _outcome_for_resolved,
    run_cascade,
)
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import (
    Disposition,
    Evaluation,
    EventKind,
    Outcome,
    PredictableEvent,
    Prediction,
    Stage,
)
from fedcourtsai.serialize import read_model

CONFIG_ROOT = Path("config")
RUN = "20260628T120000Z"

# Cascade fan-out is driven by the enabled registry, so derive the expected
# artifact counts from it — the assertions then hold as engines are added/removed.
_N_PRED = len(enabled_predictors(CONFIG_ROOT / "predictors.yaml"))
_N_EVAL = len(enabled_evaluators(CONFIG_ROOT / "evaluators.yaml"))

# A predict cell writes three documents: prediction.json, the predictor's
# reasoning.md, and its predicted_reasoning.md forecast of the court's reasoning.
_DOCS_PER_PREDICTION = 3
# An evaluate cell writes an evaluation.json + evaluation.md pair per predictor.
_DOCS_PER_EVALUATION = 2

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
    # Each enabled predictor wrote its three prediction documents.
    assert len(report.predictions) == _N_PRED * _DOCS_PER_PREDICTION
    # One ground-truth outcome materialized from the resolved corpus row.
    assert len(report.outcomes) == 1
    # Each evaluator scored every predictor → evaluators x predictors evaluation pairs.
    assert len(report.evaluations) == _N_EVAL * _N_PRED * _DOCS_PER_EVALUATION

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


def test_cascade_writes_both_prose_documents_beside_the_prediction(
    corpus_db: Path, tmp_path: Path
) -> None:
    # The end-to-end acceptance for the prose split: a cell's rationale and its
    # forecast of the court's reasoning both land, and `prediction.json` names each.
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET)
    assert report.valid, report.problems

    events = CasePaths(data_root, RESOLVED_COURT, RESOLVED_DOCKET).event(RESOLVED_EVENT)
    prediction = read_model(events.prediction("claude-baseline", RUN), Prediction)
    assert prediction.reasoning_doc == "reasoning.md"
    assert prediction.predicted_reasoning_doc == "predicted_reasoning.md"
    assert events.reasoning("claude-baseline", RUN).is_file()
    assert events.predicted_reasoning("claude-baseline", RUN).is_file()
    assert set(report.predictions) >= {
        events.prediction("claude-baseline", RUN),
        events.reasoning("claude-baseline", RUN),
        events.predicted_reasoning("claude-baseline", RUN),
    }


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
    assert len(report.predictions) == _N_PRED * _DOCS_PER_PREDICTION
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


def test_predictor_filter_narrows_the_fanout_to_one_cell(corpus_db: Path, tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, OPEN_COURT, OPEN_DOCKET, predictor="claude-baseline")

    assert report.valid, report.problems
    # One predictor's documents, not the whole registry's.
    assert len(report.predictions) == _DOCS_PER_PREDICTION
    assert all("claude-baseline" in p.parts for p in report.predictions)


def test_unknown_predictor_is_rejected_naming_the_enabled_ids(
    corpus_db: Path, tmp_path: Path
) -> None:
    with pytest.raises(CascadeError, match=r"not enabled \(have: .*claude-baseline"):
        _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET, predictor="nope-baseline")


def test_explicit_backend_override_beats_the_ambient_setting(
    corpus_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The engine-smoke split: the ambient setting says `service` for the
    # spawned agent's benefit, while the cascade's own provisioning reads run
    # on the explicit override.
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "service")
    report = _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET, backend="local")
    assert report.valid, report.problems


def test_ambient_service_backend_without_override_is_rejected(
    corpus_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "service")
    with pytest.raises(CascadeError, match="local or ranged"):
        _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET)


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


def test_interim_outcome_carries_no_cert_signals_block() -> None:
    """An application docket's outcome drops the cert `signals` block.

    The discriminating input: a row that *would* emit a block — a parsed
    `distribution_count` and a CVSG date — on an application-form docket
    number. `resolution_signals` returns None for an unparsed count on its own,
    so only a row carrying real cert signals reaches the interim guard, and
    only this shape tells the guard apart from the sentinel path. Mirrors
    `pipeline.outcome._build_outcome`, whose interim recording drops the block
    for the same reason: distribution count and CVSG are observations nobody
    makes on an application.
    """

    def _row(docket_number: str) -> corpus.CorpusRow:
        return corpus.CorpusRow(
            case_id="scotus/306",
            court="scotus",
            docket_number=docket_number,
            disposition=Disposition.granted,
            date_decided=date(2026, 7, 14),
            distribution_count=2,
            cvsg_date=date(2026, 5, 1),
        )

    def _event(event_id: str, stage: Stage) -> corpus.CorpusEvent:
        return corpus.CorpusEvent(
            event_id=event_id,
            case_id="scotus/306",
            court="scotus",
            kind=EventKind.motion if stage == Stage.interim else EventKind.petition,
            stage=stage,
            resolved=True,
        )

    interim = _outcome_for_resolved(_row("26A11"), _event("evt-motion-disposition", Stage.interim))
    assert interim is not None and interim.signals is None

    # The cert docket keeps the block, so the guard is a stage rule and not a
    # blanket suppression.
    cert = _outcome_for_resolved(_row("24-1234"), _event("evt-petition-disposition", Stage.cert))
    assert cert is not None and cert.signals is not None
    assert cert.signals.distribution_count == 2


def test_a_corrupt_stored_judgment_degrades_to_no_outcome(corpus_db: Path, tmp_path: Path) -> None:
    """The merits column is blob-tolerant TEXT, so its readers re-validate.

    An out-of-vocabulary stored value must land on the unrecorded path — the
    same contract the statpack's reader keeps — rather than crashing the whole
    cascade run on an enum conversion.
    """
    case = fixture.add_merits_fixture(corpus_db)
    with corpus.connect(corpus_db) as conn:
        conn.execute(
            "UPDATE cases SET merits_judgment = 'not-a-judgment' WHERE case_id = ?",
            (case.case_id,),
        )
        conn.commit()

    report = _run(corpus_db, tmp_path / "data", "scotus", case.docket, event="evt-order-judgment")

    assert report.valid, report.problems
    assert not report.outcomes  # no ground truth written from a value we cannot read
    assert not report.evaluations  # and so nothing to score
