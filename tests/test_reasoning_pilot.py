"""The ``predicted_reasoning_quality`` pilot: its sample, packet and report.

``docs/outcome-decomposition.md``, *The pilot, and what it reports*, fixes what
the pilot samples and what its report carries; these tests hold the code to it
over a small ledger built in a temporary directory.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from fedcourtsai.matrix import parse_cases
from fedcourtsai.paths import CasePaths
from fedcourtsai.reasoning_pilot import (
    matrix_body,
    pilot_population,
    pilot_report,
    pilot_sample,
    write_packet,
)
from fedcourtsai.schemas import (
    CentralClaim,
    Engine,
    Evaluation,
    PredictedReasoningReview,
    Prediction,
    PredictionContext,
    Stage,
)
from fedcourtsai.serialize import write_json

CERT = "evt-petition-disposition"
INTERIM = "evt-motion-disposition"
PREDICTORS = {
    "claude-baseline": Engine.claude_code,
    "codex-baseline": Engine.codex,
    "gemini-baseline": Engine.gemini,
}
JUDGES = {
    "claude-judge": Engine.claude_code,
    "codex-judge": Engine.codex,
    "gemini-judge": Engine.gemini,
}


def _prediction(
    case_id: str,
    event_id: str,
    predictor_id: str,
    run_id: str,
    *,
    mode: str = "forward",
    doc: str | None = "predicted_reasoning.md",
) -> Prediction:
    return Prediction(
        case_id=case_id,
        event_id=event_id,
        predictor_id=predictor_id,
        engine=PREDICTORS[predictor_id],
        run_id=run_id,
        created_at=datetime(2026, 9, 1, tzinfo=UTC),
        input_snapshot="2026-09-01.json",
        granted=0,
        probability=0.2,
        predicted_disposition="denied",
        predicted_reasoning_doc=doc,
        context=PredictionContext(
            mode=mode,
            snapshot_date=date(2026, 9, 1),
            signals_observable=True,
            response_requested=False,
            referred_to_court=False,
            amicus_briefs=0,
        ),
    )


def _ledger(
    data_root: Path,
    docket: int,
    event_id: str,
    *,
    resolved: bool = True,
    mode: str = "forward",
    predictors: tuple[str, ...] = tuple(PREDICTORS),
) -> None:
    ep = CasePaths(data_root, "scotus", docket).event(event_id)
    ep.base.mkdir(parents=True, exist_ok=True)
    if resolved:
        ep.outcome.write_text("{}")
    for predictor_id in predictors:
        for run_id in ("20260901T000000Z", "20260902T000000Z"):
            write_json(
                ep.prediction(predictor_id, run_id),
                _prediction(f"scotus/{docket}", event_id, predictor_id, run_id, mode=mode),
            )
            ep.predicted_reasoning(predictor_id, run_id).write_text(
                f"{predictor_id} forecast, run {run_id}\n"
            )


def _grade(
    pilot_root: Path,
    docket: int,
    event_id: str,
    evaluator_id: str,
    predictor_id: str,
    grade: float | None,
    *,
    run_id: str = "20261001T000000Z",
) -> None:
    review = (
        PredictedReasoningReview(central_claims=[CentralClaim(claim="Denied.", status="borne-out")])
        if grade is not None
        else PredictedReasoningReview(not_gradeable="The record carries no order.")
    )
    ep = CasePaths(pilot_root, "scotus", docket).event(event_id)
    write_json(
        ep.evaluation(evaluator_id, predictor_id, run_id),
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            predictor_id=predictor_id,
            evaluator_id=evaluator_id,
            engine=JUDGES[evaluator_id],
            run_id=run_id,
            created_at=datetime(2026, 10, 1, tzinfo=UTC),
            correct=True,
            predicted_reasoning_quality=grade,
            predicted_reasoning_review=review,
        ),
    )


def test_the_population_is_resolved_forward_cert_and_interim_documents(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    _ledger(data, 2, INTERIM)
    _ledger(data, 3, CERT, resolved=False)
    _ledger(data, 4, CERT, mode="replay")
    _ledger(data, 5, "evt-merits-judgment")
    population = pilot_population(data)
    assert {(d.case_id, d.stage) for d in population} == {
        ("scotus/1", Stage.cert),
        ("scotus/2", Stage.interim),
    }
    # One document per (event, predictor): the predictor's newest run.
    assert len(population) == 6
    assert {d.run_id for d in population} == {"20260902T000000Z"}


def test_a_prediction_naming_no_document_is_not_in_the_population(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT, predictors=("claude-baseline",))
    ep = CasePaths(data, "scotus", 1).event(CERT)
    ep.predicted_reasoning("claude-baseline", "20260902T000000Z").unlink()
    (document,) = pilot_population(data)
    # The newest run lacks its document, so the run before it stands in.
    assert document.run_id == "20260901T000000Z"


def test_the_sample_takes_whole_events_split_across_stages_and_is_seeded(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data"
    for docket in range(1, 11):
        _ledger(data, docket, CERT)
    for docket in range(11, 13):
        _ledger(data, docket, INTERIM)
    population = pilot_population(data)
    sample = pilot_sample(population, target=12)
    by_stage = {stage: [d for d in sample if d.stage is stage] for stage in Stage}
    # Interim holds only six documents, so cert takes the rest of the target.
    assert len(by_stage[Stage.interim]) == 6
    assert len(by_stage[Stage.cert]) == 6
    events = {(d.case_id, d.event_id) for d in sample}
    assert len(sample) == 3 * len(events)
    assert pilot_sample(population, target=12) == sample
    assert pilot_sample(population, target=12, seed="another") != sample


def test_the_matrix_body_parses_as_an_evaluate_case_list(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    _ledger(data, 2, INTERIM)
    cases = parse_cases(matrix_body(pilot_population(data)))
    assert [(c.court, c.docket, c.events) for c in cases] == [
        ("scotus", 1, (CERT,)),
        ("scotus", 2, (INTERIM,)),
    ]


def test_the_packet_hides_the_predictor_and_keeps_the_key_apart(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    packet = tmp_path / "packet"
    write_packet(pilot_population(data), packet)
    sheet = json.loads((packet / "labels.json").read_text())
    key = json.loads((packet / "key.json").read_text())
    assert [entry["doc"] for entry in sheet] == ["D01", "D02", "D03"]
    assert all("predictor_id" not in entry and entry["grade"] is None for entry in sheet)
    assert {entry["predictor_id"] for entry in key} == set(PREDICTORS)
    for entry in key:
        text = (packet / "documents" / f"{entry['doc']}.md").read_text()
        assert text.startswith(entry["predictor_id"])


def _labels(packet: Path, grades: dict[str, float]) -> Path:
    key = {e["doc"]: e["predictor_id"] for e in json.loads((packet / "key.json").read_text())}
    sheet = json.loads((packet / "labels.json").read_text())
    for entry in sheet:
        entry["grade"] = grades.get(key[entry["doc"]])
    path = packet / "labels.json"
    path.write_text(json.dumps(sheet))
    return path


def test_the_report_reads_agreement_nulls_splits_and_labels(tmp_path: Path) -> None:
    data = tmp_path / "data"
    pilot = tmp_path / "pilot"
    for docket in (1, 2):
        _ledger(data, docket, CERT)
    grades = {
        "claude-baseline": (0.25, 0.25, 0.5),
        "codex-baseline": (0.5, 0.75, 0.75),
        "gemini-baseline": (1.0, 1.0, 0.75),
    }
    for predictor_id, row in grades.items():
        for judge, grade in zip(JUDGES, row, strict=True):
            _grade(pilot, 1, CERT, judge, predictor_id, grade)
    # Docket 2: one cell split on the mask, one null by every judge.
    _grade(pilot, 2, CERT, "claude-judge", "claude-baseline", 0.5)
    _grade(pilot, 2, CERT, "codex-judge", "claude-baseline", None)
    for judge in JUDGES:
        _grade(pilot, 2, CERT, judge, "codex-baseline", None)
    # A re-grade: the newer run is the judge's read.
    _grade(pilot, 1, CERT, "claude-judge", "claude-baseline", 0.0, run_id="20261002T000000Z")

    packet = tmp_path / "packet"
    write_packet(pilot_population(data), packet)
    labels = _labels(packet, {"claude-baseline": 0.0, "gemini-baseline": 1.0})
    report = pilot_report(pilot, data, labels=labels, key=packet / "key.json")

    (stage,) = report.stages
    assert stage.stage is Stage.cert
    assert (stage.cells, stage.cases) == (5, 2)
    assert (stage.graded_by_all, stage.null_by_all, stage.split_on_mask) == (3, 1, 1)
    claude = next(j for j in stage.judges if j.evaluator_id == "claude-judge")
    assert claude.mean == pytest.approx((0.0 + 0.5 + 1.0) / 3)
    assert (claude.graded, claude.null) == (4, 1)
    assert claude.claim_status == {"borne-out": 4}
    nulls = {p.predictor_id: (p.graded, p.null) for p in stage.predictor_nulls}
    assert nulls["codex-baseline"] == (3, 3)
    # Four labels: three on cells some judge read, one on a cell no judge did.
    # The split cell's label is listed but enters no agreement figure.
    assert len(stage.labels) == 3
    assert len(report.unmatched_labels) == 1
    panel = next(a for a in stage.label_agreement if a.evaluator_id == "panel")
    assert panel.n == 2 and panel.tau_b == pytest.approx(1.0)
    assert report.labels_sha256 is not None
    # Leave-one-out over the three clean cells; within one predictor there is
    # a single cell, so no within-predictor coefficient is defined.
    loo = next(a for a in stage.leave_one_out if a.evaluator_id == "claude-judge")
    assert (loo.units, loo.cases) == (3, 1)
    assert loo.tau_b == pytest.approx(1.0)
    assert loo.within_predictor_tau_b is None and loo.within_predictor_defined == 0
    family = next(f for f in stage.family if f.evaluator_id == "gemini-judge")
    assert (family.own_n, family.own_mean) == (1, 0.75)
    assert family.other_n == 2


def test_labels_and_key_travel_together(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="travel together"):
        pilot_report(tmp_path, tmp_path, labels=tmp_path / "labels.json")


def test_a_label_sheet_changed_after_its_hash_was_recorded_is_refused(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    packet = tmp_path / "packet"
    write_packet(pilot_population(data), packet)
    labels = _labels(packet, {"claude-baseline": 0.5})
    recorded = pilot_report(tmp_path, data, labels=labels, key=packet / "key.json").labels_sha256
    assert recorded is not None
    pilot_report(
        tmp_path, data, labels=labels, key=packet / "key.json", expect_labels_sha256=recorded
    )
    _labels(packet, {"claude-baseline": 0.75})
    with pytest.raises(ValueError, match="changed after its hash was recorded"):
        pilot_report(
            tmp_path, data, labels=labels, key=packet / "key.json", expect_labels_sha256=recorded
        )
