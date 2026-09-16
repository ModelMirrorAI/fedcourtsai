"""The local cascade drives predict → evaluate → validate end to end, offline.

Exercises :func:`fedcourtsai.pipeline.cascade.run_cascade` over the synthetic
fixture corpus with the offline ``stub`` engine — the acceptance path: valid
artifacts produced end to end with no network.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus, fixture
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import (
    CascadeError,
    CascadeReport,
    _event_definition,
    _outcome_for_resolved,
    run_cascade,
)
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import (
    Disposition,
    Evaluation,
    EventKind,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
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


def test_event_definition_carries_the_moment_stamp() -> None:
    # The cascade writes its own event.yaml; a dropped moment reads as the
    # stage's first at the metrics join, silently re-pooling a later-moment
    # cell — same contract as the resolution and materialize writers.
    event = corpus.CorpusEvent(
        event_id="evt-order-cvsg-disposition",
        case_id="scotus/305",
        court="scotus",
        kind=EventKind.order,
        stage=Stage.cert,
        moment=Moment.cvsg,
        title="CVSG disposition",
    )
    definition = _event_definition(event)
    assert definition.stage == Stage.cert
    assert definition.moment == Moment.cvsg


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


def _store_document(corpus_db: Path, case_id: str, kind: str, entry_date: str) -> None:
    """Give a fixture case one stored filed document, dated on the docket."""
    with corpus.connect(corpus_db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind=kind,
                    url=f"https://example.invalid/{kind}.pdf",
                    entry_date=entry_date,
                    fetched_at=date(2026, 1, 1),
                    text=f"{kind} text",
                )
            ],
        )
        conn.commit()


def test_cascade_provisions_the_context_and_documents_a_production_cell_gets(
    corpus_db: Path, tmp_path: Path
) -> None:
    """The record a cell reads, not just its snapshot.

    ``run-predict``'s provisioning step writes three things — the dated snapshot,
    ``record/context.json``, and ``record/documents/`` with its manifest — and a
    cascade that wrote only the first hands its agent no frozen mode, band or
    cutoff and no filed text. The integration suite's engine-smoke leg drives a
    real cell through this seam, so what it certifies is only the production
    posture if all three land.
    """
    _store_document(corpus_db, f"{OPEN_COURT}/{OPEN_DOCKET}", "petition", "2020-01-01")
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, OPEN_COURT, OPEN_DOCKET)
    assert report.valid, report.problems

    case_paths = CasePaths(data_root, OPEN_COURT, OPEN_DOCKET)
    assert report.context == case_paths.cell_context
    assert report.context.is_file()
    context = PredictionContext.model_validate_json(report.context.read_text())
    # The snapshot the context names is the one on disk — the pointer the prompt
    # contract tells the cell to follow.
    assert report.snapshot == case_paths.snapshot(context.snapshot_date.isoformat())
    assert report.snapshot.is_file()
    # The document text and the manifest that describes it, the cell's
    # fetch-free filed inputs.
    assert report.documents == (case_paths.document("petition"),)
    assert case_paths.document("petition").is_file()
    manifest = json.loads(case_paths.documents_manifest.read_text())
    assert [row["kind"] for row in manifest] == ["petition"]
    assert manifest[0]["empty_text"] is False


def test_an_open_event_is_provisioned_forward_and_a_resolved_one_replay(
    corpus_db: Path, tmp_path: Path
) -> None:
    """Mode is a fact about the event, not the cell's guess.

    An unprovisioned cell defaults to ``forward``, so a cascade over a decided
    case would silently run a replay while claiming a live posture — and the
    prompt's retrieval etiquette keys on exactly this field. Both modes are placed
    at the moment their event declares; only the mode differs.
    """
    forward = _run(corpus_db, tmp_path / "open", OPEN_COURT, OPEN_DOCKET)
    assert forward.context is not None
    assert PredictionContext.model_validate_json(forward.context.read_text()).mode == "forward"

    # A resolved event whose ground truth cannot be built runs the predict half
    # alone, so the record the run ends on is that cell's own.
    case = fixture.add_merits_fixture(corpus_db)
    with corpus.connect(corpus_db) as conn:
        conn.execute(
            "UPDATE cases SET merits_judgment = 'not-a-judgment' WHERE case_id = ?",
            (case.case_id,),
        )
        conn.commit()
    replay = _run(
        corpus_db, tmp_path / "resolved", "scotus", case.docket, event="evt-order-judgment"
    )
    assert replay.outcomes == ()
    assert replay.context is not None
    context = PredictionContext.model_validate_json(replay.context.read_text())
    assert context.mode == "replay"
    # And it is placed at its moment like the forward cell beside it. The cascade
    # is the only provisioner a local replay cell has, so leaving it uncut would
    # hand it the disposing order and every merits brief under a context saying
    # `replay` — the shape of a replay cell and none of its conditioning.
    assert context.cutoff is not None
    assert context.snapshot_provenance in {"dated", "truncated"}


def test_the_evaluate_half_is_reprovisioned_from_the_latest_snapshot(
    corpus_db: Path, tmp_path: Path
) -> None:
    """A judge's record is not a forecaster's.

    ``run-evaluate`` provisions ``provision-snapshot`` with no ``--event`` — the
    latest stored payload, no moment cut — because the event it grades has already
    resolved. The cascade's predict cells are placed at the moment they forecast
    from, so the record has to be rewritten between the two halves or the judge
    reads the forecaster's cut.
    """
    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, RESOLVED_COURT, RESOLVED_DOCKET, event=RESOLVED_EVENT)

    assert report.evaluations
    assert report.context is not None
    context = PredictionContext.model_validate_json(report.context.read_text())
    assert context.mode == "forward"
    assert context.cutoff is None
    assert context.snapshot_provenance == "as-stored"
    # Which is exactly why the report carries the placements as well: the record
    # on disk is the judge's, and reading it alone would report the forecaster's
    # posture as the judge's. The predict cell's own row is still there.
    assert [p.role for p in report.placements] == ["predict", "evaluate"]
    predict_row = report.placements[0]
    assert predict_row.event_id == RESOLVED_EVENT
    assert predict_row.mode == "replay"


def test_a_forward_moment_cell_is_placed_at_its_cutoff(corpus_db: Path, tmp_path: Path) -> None:
    """The cut the engine smoke could not see: a moment cell reads its own moment.

    The fixture's CVSG docket declares a later cert moment, so a cell for it must
    be conditioned on the docket as at that moment rather than on the latest poll:
    a CVSG cell handed the latest snapshot reads the Solicitor General's brief the
    moment it forecasts from does not have. Flipped open here because the cut is
    the forward path's.
    """
    cvsg = fixture.add_cvsg_fixture(corpus_db)
    with corpus.connect(corpus_db) as conn:
        conn.execute(
            "UPDATE events SET resolved = 0 WHERE case_id = ? AND event_id = ?",
            (cvsg.case_id, "evt-order-cvsg-disposition"),
        )
        conn.commit()

    data_root = tmp_path / "data"
    report = _run(corpus_db, data_root, "scotus", cvsg.docket, event="evt-order-cvsg-disposition")

    assert report.context is not None
    context = PredictionContext.model_validate_json(report.context.read_text())
    assert context.mode == "forward"
    # The day after the CVSG opened the moment, exclusive — the shape every
    # reconstruction moment takes.
    assert context.cutoff is not None
    assert context.snapshot_provenance in {"dated", "truncated"}
    # And the file on disk is the one the context names, dated by the cut rather
    # than by the poll it was reconstructed from.
    assert report.snapshot == CasePaths(data_root, "scotus", cvsg.docket).snapshot(
        context.snapshot_date.isoformat()
    )
    assert report.snapshot.is_file()


def test_provisioning_replaces_the_previous_cell_s_documents(
    corpus_db: Path, tmp_path: Path
) -> None:
    """A record holds one cell's inputs, so a dropped document must not linger.

    Two targets of one case declare two information sets. The cascade provisions
    per cell, and without clearing, a document the second cell's tighter cut
    excluded would still be sitting in ``record/documents/`` for it to read.
    """
    case_paths = CasePaths(tmp_path / "data", OPEN_COURT, OPEN_DOCKET)
    stale = case_paths.document("merits-brief-petitioner")
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("a brief from a wider provisioning\n")
    # And a snapshot from an earlier placement, which is the half that is itself
    # an information set: `runner._input_snapshot` and `stamp-cell` resolve the
    # cell's snapshot by the name `context.json` gives, so a second dated file
    # beside it is a docket the cell was never placed at.
    stale_snapshot = case_paths.snapshot("2099-12-31")
    stale_snapshot.parent.mkdir(parents=True, exist_ok=True)
    stale_snapshot.write_text("{}\n")

    _store_document(corpus_db, f"{OPEN_COURT}/{OPEN_DOCKET}", "petition", "2020-01-01")
    report = _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET)

    assert report.valid, report.problems
    assert not stale.exists()
    assert not stale_snapshot.exists()
    assert list(case_paths.snapshots_dir.iterdir()) == [report.snapshot]
    assert case_paths.document("petition").is_file()


def test_provisioning_clears_a_staged_opinion(corpus_db: Path, tmp_path: Path) -> None:
    """A predict cell must never find a majority opinion in its record.

    An opinion postdates every predict moment by construction, so the guarantee
    that a forecaster cannot read one is that the predict lane stages none — which
    holds only if provisioning also removes a body some earlier command left in
    the same tree. `record/opinion/` is the one record subtree that can hold the
    outcome itself, so it is cleared with the rest.
    """
    case_paths = CasePaths(tmp_path / "data", OPEN_COURT, OPEN_DOCKET)
    case_paths.opinion_text.parent.mkdir(parents=True, exist_ok=True)
    case_paths.opinion_text.write_text("the Court's opinion\n")
    case_paths.opinion_manifest.write_text("{}\n")

    report = _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET)

    assert report.valid, report.problems
    assert not case_paths.opinion_text.exists()
    assert not case_paths.opinion_manifest.exists()


def test_require_record_refuses_a_case_with_no_snapshot(corpus_db: Path, tmp_path: Path) -> None:
    """The smoke's gate: an unprovisioned cell must fail before any token is spent."""
    with corpus.connect(corpus_db) as conn:
        conn.execute("DELETE FROM snapshots WHERE case_id = ?", (f"{OPEN_COURT}/{OPEN_DOCKET}",))
        conn.commit()

    with pytest.raises(CascadeError, match="would run unprovisioned"):
        _run(corpus_db, tmp_path / "data", OPEN_COURT, OPEN_DOCKET, require_record=True)

    # Without the flag the cascade still runs on the empty record: the refusal
    # belongs to the smoke, not to the local iteration loop.
    report = _run(corpus_db, tmp_path / "unguarded", OPEN_COURT, OPEN_DOCKET)
    assert report.snapshot is None
    assert report.context is None
