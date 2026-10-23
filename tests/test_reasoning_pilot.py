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
    write_sample,
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
OLDER = "20260901T000000Z"
NEWEST = "20260902T000000Z"
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
        created_at=datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC),
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
        for run_id in (OLDER, NEWEST):
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
    prediction_run_id: str = NEWEST,
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
            prediction_run_id=prediction_run_id,
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
    # One document per (event, predictor): the run an evaluate cell stages.
    assert len(population) == 6
    assert {d.run_id for d in population} == {NEWEST}


def test_a_cell_whose_staged_run_is_unusable_is_left_out_not_replaced(tmp_path: Path) -> None:
    """An older run never stands in: the judge would be shown the newer one."""
    data = tmp_path / "data"
    _ledger(data, 1, CERT, predictors=("claude-baseline", "codex-baseline"))
    ep = CasePaths(data, "scotus", 1).event(CERT)
    ep.predicted_reasoning("claude-baseline", NEWEST).unlink()
    replay = _prediction("scotus/1", CERT, "codex-baseline", "20260903T000000Z", mode="replay")
    write_json(ep.prediction("codex-baseline", replay.run_id), replay)
    ep.predicted_reasoning("codex-baseline", replay.run_id).write_text("replay\n")
    assert pilot_population(data) == []


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
    out = tmp_path / "sample"
    write_sample(pilot_population(data), out, packet=True)
    sheet = json.loads((out / "packet" / "labels.json").read_text())
    key = json.loads((out / "key.json").read_text())
    assert [entry["doc"] for entry in sheet] == ["D01", "D02", "D03"]
    assert all("predictor_id" not in entry and entry["grade"] is None for entry in sheet)
    assert {entry["predictor_id"] for entry in key} == set(PREDICTORS)
    assert not (out / "packet" / "key.json").exists()
    for entry in key:
        text = (out / "packet" / "documents" / f"{entry['doc']}.md").read_text()
        assert text.startswith(entry["predictor_id"])
    sampled = json.loads((out / "sample.json").read_text())
    assert {entry["run_id"] for entry in sampled} == {NEWEST}
    assert parse_cases((out / "body.md").read_text())[0].docket == 1


def test_a_sample_is_never_written_over_another(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    out = tmp_path / "sample"
    write_sample(pilot_population(data), out, packet=True)
    with pytest.raises(ValueError, match="already holds files"):
        write_sample(pilot_population(data), out, packet=True)


def _labels(out: Path, grades: dict[str, float]) -> Path:
    key = {e["doc"]: e["predictor_id"] for e in json.loads((out / "key.json").read_text())}
    path = out / "packet" / "labels.json"
    sheet = json.loads(path.read_text())
    for entry in sheet:
        entry["grade"] = grades.get(key[entry["doc"]])
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
    # Docket 2: one cell split on the mask, one null by every judge, one unread.
    _grade(pilot, 2, CERT, "claude-judge", "claude-baseline", 0.5)
    _grade(pilot, 2, CERT, "codex-judge", "claude-baseline", None)
    for judge in JUDGES:
        _grade(pilot, 2, CERT, judge, "codex-baseline", None)
    # A re-grade: the newer run is the judge's read.
    _grade(pilot, 1, CERT, "claude-judge", "claude-baseline", 0.0, run_id="20261002T000000Z")
    # Set aside: a grade of another run, and a grade of a cell outside the sample.
    _grade(
        pilot,
        1,
        CERT,
        "codex-judge",
        "gemini-baseline",
        0.0,
        run_id="20261003T000000Z",
        prediction_run_id=OLDER,
    )
    _grade(pilot, 9, CERT, "codex-judge", "gemini-baseline", 0.0)

    out = tmp_path / "sample"
    write_sample(pilot_population(data), out, packet=True)
    labels = _labels(out, {"claude-baseline": 0.0, "gemini-baseline": 1.0})
    report = pilot_report(pilot, out, labels=labels)

    assert (report.off_sample, report.off_run, report.superseded) == (1, 1, 1)
    assert not report.labels_hash_verified and report.key_sha256 is not None
    (stage,) = report.stages
    assert stage.stage is Stage.cert
    assert (stage.sampled, stage.cells, stage.cases, stage.unread) == (6, 5, 2, 1)
    assert (stage.graded_by_all, stage.null_by_all, stage.split_on_mask) == (3, 1, 1)
    assert stage.missing_judge == 1
    claude = next(j for j in stage.judges if j.evaluator_id == "claude-judge")
    assert claude.mean == pytest.approx((0.0 + 0.5 + 1.0) / 3)
    assert claude.mean_n == 3
    assert (claude.graded, claude.null) == (4, 1)
    assert claude.claim_status == {"borne-out": 4}
    nulls = {p.predictor_id: (p.cells, p.graded, p.null) for p in stage.predictor_nulls}
    assert nulls["codex-baseline"] == (2, 3, 3)
    # Four labels: three on cells some judge read, one on the unread cell.
    # The split cell's label is listed but enters no agreement figure.
    assert len(stage.labels) == 3
    assert len(report.unmatched_labels) == 1
    panel = next(a for a in stage.label_agreement if a.evaluator_id == "panel")
    assert panel.n == 2 and panel.tau_b == pytest.approx(1.0)
    # Leave-one-out over the three clean cells; within one predictor there is
    # a single cell, so no within-predictor coefficient is defined.
    loo = next(a for a in stage.leave_one_out if a.evaluator_id == "claude-judge")
    assert (loo.units, loo.cases) == (3, 1)
    assert loo.tau_b == pytest.approx(1.0)
    assert loo.within_predictor_tau_b is None
    assert [(w.units, w.tau_b) for w in loo.within_predictor] == [(1, None)] * 3
    family = next(f for f in stage.family if f.evaluator_id == "gemini-judge")
    assert (family.own_n, family.own_mean) == (1, 0.75)
    assert family.other_n == 2


def test_an_expected_labels_hash_needs_its_sheet(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="needs the label sheet"):
        pilot_report(tmp_path, tmp_path, expect_labels_sha256="0" * 64)


def test_a_label_sheet_changed_after_its_hash_was_recorded_is_refused(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _ledger(data, 1, CERT)
    out = tmp_path / "sample"
    write_sample(pilot_population(data), out, packet=True)
    labels = _labels(out, {"claude-baseline": 0.5})
    recorded = pilot_report(tmp_path, out, labels=labels).labels_sha256
    assert recorded is not None
    report = pilot_report(tmp_path, out, labels=labels, expect_labels_sha256=recorded)
    assert report.labels_hash_verified
    _labels(out, {"claude-baseline": 0.75})
    with pytest.raises(ValueError, match="changed after its hash was recorded"):
        pilot_report(tmp_path, out, labels=labels, expect_labels_sha256=recorded)


def test_a_round_id_reads_only_that_rounds_evaluations(tmp_path: Path) -> None:
    """A cell artifact carries its event's committed evaluations beside the round's."""
    data = tmp_path / "data"
    pilot = tmp_path / "pilot"
    _ledger(data, 1, CERT, predictors=("claude-baseline",))
    _grade(pilot, 1, CERT, "claude-judge", "claude-baseline", 0.75, run_id="20261005T000000Z")
    # Another judge's committed, ungraded evaluation from an earlier round, and
    # a newer null from another round by the pilot's own judge, which would
    # supersede the round's grade were the reads not restricted to the round.
    _grade(pilot, 1, CERT, "codex-judge", "claude-baseline", None, run_id="20260910T000000Z")
    _grade(pilot, 1, CERT, "claude-judge", "claude-baseline", None, run_id="20261009T000000Z")
    out = tmp_path / "sample"
    write_sample(pilot_population(data), out)
    report = pilot_report(pilot, out, round_id="20261005T000000Z")
    assert report.other_round == 2 and report.round_id == "20261005T000000Z"
    (stage,) = report.stages
    assert [(j.evaluator_id, j.graded, j.null) for j in stage.judges] == [("claude-judge", 1, 0)]
