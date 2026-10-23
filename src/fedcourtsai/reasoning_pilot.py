"""The pilot of the ``predicted_reasoning_quality`` grade: its sample and its report.

The design is ``docs/outcome-decomposition.md``, *Grading the forecast
document, design*. The grade is not registered, so nothing here reads or
writes the ledger's evaluations: the sample names already-resolved cells for a
pilot evaluate round, and the report reads that round's evaluations from a
directory outside ``data/`` (laid out like ``data/``), beside the maintainer's
reference labels.

The report fixes in advance what it carries, so it cannot be chosen after the
grades are read: per stage, and never pooled across stages, each judge's grades
beside the labels, the leave-one-out inter-evaluator agreement with the cell as
the unit, the predictor-tracking check, each judge's own-family grades beside
its others', and every judge's and predictor's null count. A cell some judges
grade and others leave null is a split on the mask: it enters no mean and no
coefficient and is counted on its own.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .leaderboard import kendall_tau_b
from .pipeline.moments import event_stage
from .schemas import Engine, Evaluation, PredictableEvent, Prediction, Stage
from .serialize import read_model
from .voids import is_voided

PILOT_STAGES: tuple[Stage, ...] = (Stage.cert, Stage.interim)
"""The stages the pilot's agreement figures read; merits replay is calibration only."""

LABEL_TOLERANCE = 0.2
"""How near a judge's grade must sit to a label to count as within it."""

DEFAULT_TARGET = 60
DEFAULT_SEED = "predicted-reasoning-pilot"

Cell = tuple[str, str, str]
"""A graded document: (case_id, event_id, predictor_id)."""


@dataclass(frozen=True)
class PilotDocument:
    """One committed forecast document the pilot may grade."""

    case_id: str
    event_id: str
    stage: Stage
    predictor_id: str
    run_id: str
    engine: Engine
    path: Path

    @property
    def cell(self) -> Cell:
        return (self.case_id, self.event_id, self.predictor_id)


def _event_dirs(data_root: Path) -> Iterable[Path]:
    yield from sorted((data_root / "cases").glob("*/*/events/*"))


def _case_id(event_dir: Path) -> str:
    return f"{event_dir.parent.parent.parent.name}/{event_dir.parent.parent.name}"


def _stage_of(event_dir: Path) -> Stage | None:
    recorded = None
    if event_dir.joinpath("event.yaml").exists():
        recorded = read_model(event_dir / "event.yaml", PredictableEvent).stage
    return event_stage(recorded, event_dir.name)


def pilot_population(data_root: Path) -> list[PilotDocument]:
    """Every resolved, forward cert or interim forecast document on the ledger.

    One document per (event, predictor): a predictor's newest run that names a
    forecast document present on disk. Replay predictions are left out, since a
    replay document can carry its outcome, and so are voided events.
    """
    documents: list[PilotDocument] = []
    for event_dir in _event_dirs(data_root):
        if not event_dir.joinpath("outcome.json").exists():
            continue
        stage = _stage_of(event_dir)
        if stage not in PILOT_STAGES:
            continue
        case_id = _case_id(event_dir)
        if is_voided(case_id, event_dir.name):
            continue
        for predictor_dir in sorted(event_dir.joinpath("predictions").glob("*")):
            for run_dir in sorted(predictor_dir.glob("*"), reverse=True):
                prediction_path = run_dir / "prediction.json"
                if not prediction_path.exists():
                    continue
                prediction = read_model(prediction_path, Prediction)
                doc = prediction.predicted_reasoning_doc
                if doc is None or not run_dir.joinpath(doc).exists():
                    continue
                if prediction.context is None or prediction.context.mode != "forward":
                    continue
                documents.append(
                    PilotDocument(
                        case_id=case_id,
                        event_id=event_dir.name,
                        stage=stage,
                        predictor_id=prediction.predictor_id,
                        run_id=prediction.run_id,
                        engine=prediction.engine,
                        path=run_dir / doc,
                    )
                )
                break
    return documents


def _order_key(seed: str, case_id: str, event_id: str) -> str:
    return hashlib.sha256(f"{seed}\0{case_id}\0{event_id}".encode()).hexdigest()


def pilot_sample(
    population: Sequence[PilotDocument], *, target: int = DEFAULT_TARGET, seed: str = DEFAULT_SEED
) -> list[PilotDocument]:
    """About ``target`` documents, split evenly across cert and interim, by whole events.

    An evaluate cell grades every predictor of its event, so the sample takes
    events whole, in an order fixed by ``seed``, until each stage holds its half
    of the target; a stage that runs short leaves its remainder to the other.
    The same population and seed always give the same sample.
    """
    by_event: dict[tuple[str, str], list[PilotDocument]] = defaultdict(list)
    for document in population:
        by_event[(document.case_id, document.event_id)].append(document)
    ordered = {
        stage: sorted(
            (key for key, docs in by_event.items() if docs[0].stage is stage),
            key=lambda key: _order_key(seed, *key),
        )
        for stage in PILOT_STAGES
    }
    available = {stage: sum(len(by_event[key]) for key in keys) for stage, keys in ordered.items()}
    quota = {stage: target // len(PILOT_STAGES) for stage in PILOT_STAGES}
    for stage in PILOT_STAGES:
        spare = quota[stage] - available[stage]
        if spare > 0:
            quota[stage] = available[stage]
            for other in PILOT_STAGES:
                if other is not stage:
                    quota[other] += spare
    chosen: list[PilotDocument] = []
    for stage in PILOT_STAGES:
        taken = 0
        for key in ordered[stage]:
            if taken >= quota[stage]:
                break
            chosen.extend(sorted(by_event[key], key=lambda d: d.predictor_id))
            taken += len(by_event[key])
    return chosen


def matrix_body(sample: Sequence[PilotDocument]) -> str:
    """The evaluate matrix's ``--body-file`` text for the sample: one entry per case."""
    events: dict[str, set[str]] = defaultdict(set)
    for document in sample:
        events[document.case_id].add(document.event_id)
    entries = [
        {
            "court": case_id.split("/")[0],
            "docket": int(case_id.split("/")[1]),
            "events": sorted(ids),
        }
        for case_id, ids in sorted(events.items())
    ]
    return "```json\n" + json.dumps(entries, indent=2) + "\n```\n"


class PacketEntry(BaseModel):
    """One document in the maintainer's blind labeling packet."""

    model_config = ConfigDict(extra="forbid")

    doc: str = Field(description="The document's alias in the packet, e.g. `D07`")
    case_id: str
    event_id: str
    stage: Stage
    grade: float | None = Field(default=None, ge=0.0, le=1.0)
    note: str | None = None


class PacketKeyEntry(BaseModel):
    """What one packet alias stands for. Kept out of the labeler's sight."""

    model_config = ConfigDict(extra="forbid")

    doc: str
    case_id: str
    event_id: str
    predictor_id: str
    run_id: str


def write_packet(sample: Sequence[PilotDocument], out: Path, *, seed: str = DEFAULT_SEED) -> None:
    """Write the blind labeling packet: aliased documents, a label sheet, and the key.

    ``out/documents/Dnn.md`` copies each document under an alias assigned in a
    seeded order, so a predictor's documents do not sit together;
    ``out/labels.json`` is the sheet the maintainer fills in; ``out/key.json``
    maps each alias back to its cell for the report, and is not opened while
    labeling.
    """
    order = sorted(
        sample,
        key=lambda d: hashlib.sha256(f"{seed}\0{'\0'.join(d.cell)}".encode()).hexdigest(),
    )
    width = max(2, len(str(len(order))))
    documents = out / "documents"
    documents.mkdir(parents=True, exist_ok=True)
    sheet: list[PacketEntry] = []
    key: list[PacketKeyEntry] = []
    for index, document in enumerate(order, start=1):
        alias = f"D{index:0{width}d}"
        documents.joinpath(f"{alias}.md").write_text(document.path.read_text())
        sheet.append(
            PacketEntry(
                doc=alias,
                case_id=document.case_id,
                event_id=document.event_id,
                stage=document.stage,
            )
        )
        key.append(
            PacketKeyEntry(
                doc=alias,
                case_id=document.case_id,
                event_id=document.event_id,
                predictor_id=document.predictor_id,
                run_id=document.run_id,
            )
        )
    out.joinpath("labels.json").write_text(
        json.dumps([entry.model_dump(mode="json") for entry in sheet], indent=2) + "\n"
    )
    out.joinpath("key.json").write_text(
        json.dumps([entry.model_dump(mode="json") for entry in key], indent=2) + "\n"
    )


# --- the report ---------------------------------------------------------------


class _Report(BaseModel):
    model_config = ConfigDict(extra="forbid")


class JudgeGrades(_Report):
    """One judge's grades on a stage."""

    evaluator_id: str
    graded: int
    null: int
    mean: float | None
    mean_central_claims: float | None = Field(
        description="Mean length of the judge's central-claims list over its graded cells"
    )
    claim_status: dict[str, int] = Field(
        description="Central claims the judge listed beside a grade, by status"
    )


class PredictorNulls(_Report):
    """How many of a predictor's cells each stage graded and left null, over all judges."""

    predictor_id: str
    graded: int
    null: int


class LabelRow(_Report):
    """One labeled document: the maintainer's grade beside each judge's."""

    doc: str
    case_id: str
    event_id: str
    predictor_id: str
    label: float
    judges: dict[str, float | None]


class LabelAgreement(_Report):
    """One judge's (or the panel mean's) grades against the labels."""

    evaluator_id: str = Field(description="A judge id, or `panel` for the panel mean")
    n: int
    within_tolerance: float | None = Field(
        description=f"Share of labeled documents graded within {LABEL_TOLERANCE} of the label"
    )
    tau_b: float | None


class LeaveOneOut(_Report):
    """A judge's grades against the mean of the others' on the cells they share."""

    evaluator_id: str
    units: int = Field(description="Cells entering the coefficient")
    cases: int = Field(description="Distinct cases among those cells")
    tau_b: float | None = Field(description="Null where undefined, never read as agreement")
    within_predictor_tau_b: float | None = Field(
        description="The same coefficient within each predictor's cells, averaged over the "
        "predictors where it is defined"
    )
    within_predictor_defined: int = Field(
        description="Predictors whose within-predictor coefficient is defined"
    )


class FamilyGrades(_Report):
    """A judge's mean grade of its own engine family's documents and of the others'."""

    evaluator_id: str
    engine: Engine
    own_n: int
    own_mean: float | None
    other_n: int
    other_mean: float | None


class StageReport(_Report):
    """Everything the pilot reports for one stage."""

    stage: Stage
    cells: int = Field(description="Cells at least one judge returned an evaluation for")
    cases: int
    graded_by_all: int = Field(description="Cells every judge on the cell graded")
    null_by_all: int = Field(description="Cells every judge on the cell left null")
    split_on_mask: int = Field(
        description="Cells some judges graded and others left null; in no mean or coefficient"
    )
    judges: list[JudgeGrades]
    predictor_nulls: list[PredictorNulls]
    labels: list[LabelRow]
    label_agreement: list[LabelAgreement]
    leave_one_out: list[LeaveOneOut]
    family: list[FamilyGrades]


class PilotReport(_Report):
    """The pilot report: one round of the draft prompt section, per stage."""

    pilot_root: str
    prompt_sha256: str | None = Field(
        description="sha256 of the draft prompt section the round ran, as supplied"
    )
    labels_sha256: str | None = Field(description="sha256 of the label sheet's bytes")
    unmatched_labels: list[str] = Field(
        description="Labeled aliases whose cell no judge graded in this round"
    )
    stages: list[StageReport]


@dataclass(frozen=True)
class _Read:
    evaluator_id: str
    engine: Engine
    grade: float | None
    claims: tuple[str, ...]


def _pilot_reads(pilot_root: Path) -> dict[Cell, dict[str, _Read]]:
    """Each judge's newest read of each cell under ``pilot_root``."""
    newest: dict[tuple[Cell, str], tuple[str, _Read]] = {}
    for path in sorted(
        (pilot_root / "cases").glob("*/*/events/*/evaluations/*/*/*/evaluation.json")
    ):
        evaluation = read_model(path, Evaluation)
        cell = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id)
        review = evaluation.predicted_reasoning_review
        read = _Read(
            evaluator_id=evaluation.evaluator_id,
            engine=evaluation.engine,
            grade=evaluation.predicted_reasoning_quality,
            claims=tuple(c.status for c in review.central_claims) if review else (),
        )
        key = (cell, evaluation.evaluator_id)
        if key not in newest or evaluation.run_id > newest[key][0]:
            newest[key] = (evaluation.run_id, read)
    reads: dict[Cell, dict[str, _Read]] = defaultdict(dict)
    for (cell, evaluator_id), (_, read) in newest.items():
        reads[cell][evaluator_id] = read
    return reads


def _predictor_engines(data_root: Path, cells: Iterable[Cell]) -> dict[Cell, Engine]:
    engines: dict[Cell, Engine] = {}
    for case_id, event_id, predictor_id in cells:
        court, docket = case_id.split("/")
        runs = sorted(
            (data_root / "cases" / court / docket / "events" / event_id / "predictions")
            .joinpath(predictor_id)
            .glob("*/prediction.json")
        )
        if runs:
            engines[(case_id, event_id, predictor_id)] = read_model(runs[-1], Prediction).engine
    return engines


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _loo_points(
    cells: Iterable[Mapping[str, float]], evaluator_id: str
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for grades in cells:
        if evaluator_id not in grades:
            continue
        others = [g for e, g in grades.items() if e != evaluator_id]
        if others:
            points.append((grades[evaluator_id], sum(others) / len(others)))
    return points


Panel = Mapping[str, _Read]
Grades = dict[str, float]


def _partition(reads: Mapping[Cell, Panel]) -> tuple[dict[Cell, Grades], int, int]:
    """The cells every judge graded, with the counts left null by all and split."""
    clean: dict[Cell, Grades] = {}
    null_by_all = split = 0
    for cell, panel in reads.items():
        grades = [r.grade for r in panel.values()]
        if all(g is None for g in grades):
            null_by_all += 1
        elif any(g is None for g in grades):
            split += 1
        else:
            clean[cell] = {e: r.grade for e, r in panel.items() if r.grade is not None}
    return clean, null_by_all, split


def _judge_grades(
    evaluator_id: str, reads: Mapping[Cell, Panel], clean: Mapping[Cell, Grades]
) -> JudgeGrades:
    mine = [panel[evaluator_id] for panel in reads.values() if evaluator_id in panel]
    graded = [r for r in mine if r.grade is not None]
    statuses: dict[str, int] = defaultdict(int)
    for r in graded:
        for status in r.claims:
            statuses[status] += 1
    return JudgeGrades(
        evaluator_id=evaluator_id,
        graded=len(graded),
        null=len(mine) - len(graded),
        mean=_mean([g[evaluator_id] for g in clean.values() if evaluator_id in g]),
        mean_central_claims=_mean([float(len(r.claims)) for r in graded]),
        claim_status=dict(sorted(statuses.items())),
    )


def _predictor_nulls(reads: Mapping[Cell, Panel]) -> list[PredictorNulls]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for (_, _, predictor_id), panel in reads.items():
        for r in panel.values():
            counts[predictor_id][0 if r.grade is not None else 1] += 1
    return [
        PredictorNulls(predictor_id=p, graded=graded, null=null)
        for p, (graded, null) in sorted(counts.items())
    ]


def _label_agreement(
    evaluator_id: str, rows: Sequence[LabelRow], clean: Mapping[Cell, Grades]
) -> LabelAgreement:
    """``evaluator_id`` against the labels, on the labeled cells every judge graded."""
    pairs: list[tuple[float, float]] = []
    for row in rows:
        grades = clean.get((row.case_id, row.event_id, row.predictor_id))
        if grades is None:
            continue
        if evaluator_id == "panel":
            pairs.append((sum(grades.values()) / len(grades), row.label))
        elif evaluator_id in grades:
            pairs.append((grades[evaluator_id], row.label))
    return LabelAgreement(
        evaluator_id=evaluator_id,
        n=len(pairs),
        within_tolerance=_mean(
            [1.0 if abs(g - lab) <= LABEL_TOLERANCE + 1e-9 else 0.0 for g, lab in pairs]
        ),
        tau_b=kendall_tau_b(pairs),
    )


def _leave_one_out(evaluator_id: str, clean: Mapping[Cell, Grades]) -> LeaveOneOut:
    shared = [cell for cell, grades in clean.items() if evaluator_id in grades and len(grades) > 1]
    by_predictor: dict[str, list[Grades]] = defaultdict(list)
    for (_, _, predictor_id), grades in clean.items():
        by_predictor[predictor_id].append(grades)
    within = [kendall_tau_b(_loo_points(cells, evaluator_id)) for cells in by_predictor.values()]
    defined = [t for t in within if t is not None]
    return LeaveOneOut(
        evaluator_id=evaluator_id,
        units=len(shared),
        cases=len({cell[0] for cell in shared}),
        tau_b=kendall_tau_b(_loo_points(clean.values(), evaluator_id)),
        within_predictor_tau_b=_mean(defined),
        within_predictor_defined=len(defined),
    )


def _family_grades(
    evaluator_id: str,
    reads: Mapping[Cell, Panel],
    clean: Mapping[Cell, Grades],
    engines: Mapping[Cell, Engine],
) -> FamilyGrades | None:
    own: list[float] = []
    other: list[float] = []
    engine: Engine | None = None
    for cell, panel in reads.items():
        if evaluator_id not in panel or cell not in clean or cell not in engines:
            continue
        engine = panel[evaluator_id].engine
        (own if engines[cell] is engine else other).append(clean[cell][evaluator_id])
    if engine is None:
        return None
    return FamilyGrades(
        evaluator_id=evaluator_id,
        engine=engine,
        own_n=len(own),
        own_mean=_mean(own),
        other_n=len(other),
        other_mean=_mean(other),
    )


def _stage_report(
    stage: Stage,
    reads: Mapping[Cell, Panel],
    engines: Mapping[Cell, Engine],
    labels: Mapping[Cell, tuple[str, float]],
) -> StageReport:
    evaluators = sorted({e for panel in reads.values() for e in panel})
    clean, null_by_all, split = _partition(reads)
    rows = [
        LabelRow(
            doc=alias,
            case_id=cell[0],
            event_id=cell[1],
            predictor_id=cell[2],
            label=label,
            judges={e: r.grade for e, r in sorted(reads[cell].items())},
        )
        for cell, (alias, label) in sorted(labels.items(), key=lambda item: item[1][0])
        if cell in reads
    ]
    family = [_family_grades(e, reads, clean, engines) for e in evaluators]
    return StageReport(
        stage=stage,
        cells=len(reads),
        cases=len({cell[0] for cell in reads}),
        graded_by_all=len(clean),
        null_by_all=null_by_all,
        split_on_mask=split,
        judges=[_judge_grades(e, reads, clean) for e in evaluators],
        predictor_nulls=_predictor_nulls(reads),
        labels=rows,
        label_agreement=[_label_agreement(e, rows, clean) for e in [*evaluators, "panel"]],
        leave_one_out=[_leave_one_out(e, clean) for e in evaluators],
        family=[f for f in family if f is not None],
    )


def pilot_report(
    pilot_root: Path,
    data_root: Path,
    *,
    labels: Path | None = None,
    key: Path | None = None,
    prompt_sha256: str | None = None,
    expect_labels_sha256: str | None = None,
) -> PilotReport:
    """The report over one pilot round's evaluations under ``pilot_root``.

    ``data_root`` is the ledger the round graded, read for each event's stage
    and each predictor's engine. ``labels`` is the filled-in packet sheet and
    ``key`` the packet's alias key; an unfilled label (a null grade) is not a
    label. Stages read separately, in the order cert, interim, merits; a stage
    no judge graded is left out.

    The labels' hash is committed before the panel's grades are read, so a
    sheet changed after the grades were seen shows: with
    ``expect_labels_sha256`` (the hash recorded beforehand) a sheet whose bytes
    hash otherwise is refused.
    """
    if (labels is None) != (key is None):
        raise ValueError("labels and key travel together: pass both or neither")
    reads = _pilot_reads(pilot_root)
    engines = _predictor_engines(data_root, reads)
    labelled: dict[Cell, tuple[str, float]] = {}
    labels_sha256: str | None = None
    unmatched: list[str] = []
    if labels is not None and key is not None:
        raw = labels.read_bytes()
        labels_sha256 = hashlib.sha256(raw).hexdigest()
        if expect_labels_sha256 is not None and labels_sha256 != expect_labels_sha256.lower():
            raise ValueError(
                f"the label sheet hashes to {labels_sha256}, not the recorded "
                f"{expect_labels_sha256}: it changed after its hash was recorded"
            )
        sheet = [PacketEntry.model_validate(entry) for entry in json.loads(raw)]
        cells = {
            entry.doc: (entry.case_id, entry.event_id, entry.predictor_id)
            for entry in (
                PacketKeyEntry.model_validate(item) for item in json.loads(key.read_text())
            )
        }
        for entry in sheet:
            if entry.grade is None:
                continue
            if entry.doc not in cells:
                raise ValueError(f"label {entry.doc} has no entry in the key")
            cell = cells[entry.doc]
            if cell not in reads:
                unmatched.append(entry.doc)
            labelled[cell] = (entry.doc, entry.grade)

    by_stage: dict[Stage, dict[Cell, dict[str, _Read]]] = defaultdict(dict)
    for cell, panel in reads.items():
        court, docket = cell[0].split("/")
        stage = _stage_of(data_root / "cases" / court / docket / "events" / cell[1])
        if stage is None:
            stage = event_stage(None, cell[1])
        if stage is not None:
            by_stage[stage][cell] = panel
    stages = [
        _stage_report(
            stage,
            by_stage[stage],
            engines,
            {c: v for c, v in labelled.items() if c in by_stage[stage]},
        )
        for stage in (Stage.cert, Stage.interim, Stage.merits)
        if stage in by_stage
    ]
    return PilotReport(
        pilot_root=str(pilot_root),
        prompt_sha256=prompt_sha256,
        labels_sha256=labels_sha256,
        unmatched_labels=sorted(unmatched),
        stages=stages,
    )
