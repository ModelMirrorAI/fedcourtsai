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
grade and others leave null is a split on the mask: it enters no grade mean
and no coefficient and is counted on its own.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .blinding import latest_prediction_dirs
from .ids import parse_run_id
from .leaderboard import kendall_tau_b
from .paths import EventPaths
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
    """Every resolved, forward cert or interim forecast document an evaluate round would grade.

    One document per (event, predictor), and it is the run an evaluate cell
    stages for that predictor (:func:`fedcourtsai.blinding.latest_prediction_dirs`,
    down to its tiebreak), so the document sampled is the document graded. Where
    that run is a replay, or names no forecast document present on disk, the
    cell is left out rather than replaced by an older run, which no judge would
    be shown. Replay is left out because a replay document can carry its
    outcome; voided events are left out too.
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
        for run_dir in latest_prediction_dirs(EventPaths(event_dir)).values():
            prediction = read_model(run_dir / "prediction.json", Prediction)
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
            (key for key, docs in by_event.items() if docs[0].stage == stage),
            key=lambda key: _order_key(seed, *key),
        )
        for stage in PILOT_STAGES
    }
    available = {stage: sum(len(by_event[key]) for key in keys) for stage, keys in ordered.items()}
    share, remainder = divmod(target, len(PILOT_STAGES))
    quota = {stage: share + (index < remainder) for index, stage in enumerate(PILOT_STAGES)}
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


class SampleEntry(BaseModel):
    """One sampled cell: the document the round grades, named by its run."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    event_id: str
    stage: Stage
    predictor_id: str
    run_id: str = Field(description="The prediction run the round must grade")
    engine: Engine = Field(description="The predictor's engine, its family")

    @property
    def cell(self) -> Cell:
        return (self.case_id, self.event_id, self.predictor_id)


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


SAMPLE_FILE = "sample.json"
BODY_FILE = "body.md"
KEY_FILE = "key.json"
PACKET_DIR = "packet"
LABELS_FILE = "labels.json"


def _dump(path: Path, entries: Sequence[BaseModel]) -> None:
    path.write_text(json.dumps([e.model_dump(mode="json") for e in entries], indent=2) + "\n")


def write_sample(
    sample: Sequence[PilotDocument], out: Path, *, packet: bool = False, seed: str = DEFAULT_SEED
) -> None:
    """Write the sample into ``out``, which must be new or empty.

    ``body.md`` is the case list an evaluate round takes as ``--body-file``;
    ``sample.json`` names every sampled cell with the run the round must grade,
    and is what the report reads its population from. With ``packet``, also
    the blind labeling packet: ``packet/documents/Dnn.md`` copies each document
    under an alias assigned in a seeded order, so a predictor's documents do
    not sit together; ``packet/labels.json`` is the sheet the maintainer fills
    in, naming case and event but not the predictor; and ``key.json``, beside
    the packet rather than in it, maps each alias back to its cell. A directory
    already holding files is refused, so a re-run never overwrites a filled-in
    sheet or leaves an earlier sample's documents behind.
    """
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"{out} already holds files; write a sample into a new directory")
    out.mkdir(parents=True, exist_ok=True)
    out.joinpath(BODY_FILE).write_text(matrix_body(sample))
    _dump(
        out / SAMPLE_FILE,
        [
            SampleEntry(
                case_id=d.case_id,
                event_id=d.event_id,
                stage=d.stage,
                predictor_id=d.predictor_id,
                run_id=d.run_id,
                engine=d.engine,
            )
            for d in sample
        ],
    )
    if not packet:
        return
    order = sorted(
        sample,
        key=lambda d: hashlib.sha256(f"{seed}\0{'\0'.join(d.cell)}".encode()).hexdigest(),
    )
    width = max(2, len(str(len(order))))
    documents = out / PACKET_DIR / "documents"
    documents.mkdir(parents=True)
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
    _dump(out / PACKET_DIR / LABELS_FILE, sheet)
    _dump(out / KEY_FILE, key)


# --- the report ---------------------------------------------------------------


class _Report(BaseModel):
    model_config = ConfigDict(extra="forbid")


class JudgeGrades(_Report):
    """One judge's reads on a stage."""

    evaluator_id: str
    graded: int = Field(description="Sampled cells the judge graded, split cells included")
    null: int = Field(description="Sampled cells the judge left null")
    mean: float | None = Field(description="Mean grade over the cells every judge graded")
    mean_n: int = Field(description="Cells the mean is over")
    mean_central_claims: float | None = Field(
        description="Mean length of the judge's central-claims list over every cell it "
        "graded, split cells included: a count of what the judge listed, not a grade"
    )
    claim_status: dict[str, int] = Field(
        description="Central claims the judge listed beside a grade, by status"
    )


class PredictorNulls(_Report):
    """A predictor's judge reads on a stage: one per judge per cell, graded or null."""

    predictor_id: str
    cells: int
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
    n: int = Field(description="Labeled cells every judge graded")
    within_tolerance: float | None = Field(
        description=f"Share of labeled documents graded within {LABEL_TOLERANCE} of the label"
    )
    tau_b: float | None


class WithinPredictor(_Report):
    """The leave-one-out coefficient within one predictor's cells."""

    predictor_id: str
    units: int
    tau_b: float | None


class LeaveOneOut(_Report):
    """A judge's grades against the mean of the others' on the cells they share."""

    evaluator_id: str
    units: int = Field(description="Cells entering the coefficient")
    cases: int = Field(description="Distinct cases among those cells")
    tau_b: float | None = Field(description="Null where undefined, never read as agreement")
    within_predictor_tau_b: float | None = Field(
        description="The same coefficient within each predictor's cells, averaged unweighted "
        "over the predictors where it is defined; `within_predictor` lists each"
    )
    within_predictor: list[WithinPredictor]


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
    sampled: int = Field(description="Cells the sample names on this stage")
    cells: int = Field(description="Sampled cells at least one judge read")
    cases: int = Field(description="Distinct cases among those cells")
    unread: int = Field(description="Sampled cells no judge read")
    missing_judge: int = Field(
        description="Read cells some judge seen on this stage returned no read for; their "
        "figures stand on a smaller panel"
    )
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
    """The pilot report over one round of the draft prompt section, per stage."""

    pilot_root: str
    prompt_sha256: str | None = Field(
        description="sha256 of the draft prompt section the round ran, as the operator "
        "supplied it; the evaluations do not record it"
    )
    sample_sha256: str = Field(description="sha256 of the sample file's bytes")
    labels_sha256: str | None = Field(description="sha256 of the label sheet's bytes")
    key_sha256: str | None = Field(description="sha256 of the packet key's bytes")
    labels_hash_verified: bool = Field(
        description="Whether the label sheet was checked against a hash recorded before the "
        "round's grades were read"
    )
    off_sample: int = Field(
        description="Evaluations under the root of a cell the sample does not name; read by nothing"
    )
    off_run: int = Field(
        description="Evaluations of a sampled cell that graded another prediction run than "
        "the one sampled; read by nothing"
    )
    superseded: int = Field(
        description="Older evaluations of a judge's cell, set aside for its newest run"
    )
    round_id: str | None = Field(
        description="The evaluate run the report was restricted to, if any"
    )
    other_round: int = Field(
        description="Evaluations of another evaluate run than `round_id`; read by nothing"
    )
    misplaced: int = Field(
        description="Files named evaluation.json outside the "
        "`evaluations/<evaluator>/<predictor>/<run>/` layout, such as one a judge left under "
        "its blinded alias; read by nothing, so its cell counts as missing that judge"
    )
    unmatched_labels: list[str] = Field(
        description="Labeled aliases whose cell no judge read in this round"
    )
    stages: list[StageReport]


@dataclass(frozen=True)
class _Read:
    evaluator_id: str
    engine: Engine
    grade: float | None
    claims: tuple[str, ...]


@dataclass
class _Reads:
    reads: dict[Cell, dict[str, _Read]]
    off_sample: int
    off_run: int
    superseded: int
    other_round: int
    misplaced: int


def _is_run_dir(name: str) -> bool:
    try:
        parse_run_id(name)
    except ValueError:
        return False
    return True


def _pilot_reads(
    pilot_root: Path, sample: Mapping[Cell, SampleEntry], *, round_id: str | None
) -> _Reads:
    """Each judge's newest read of each sampled cell, of the sampled run, under ``pilot_root``.

    With ``round_id``, only evaluations of that evaluate run are read: a cell's
    artifact carries its event's committed evaluations beside the round's own,
    and a judge whose pilot cell produced nothing must not be read through its
    committed, ungraded one.
    """
    newest: dict[tuple[Cell, str], tuple[str, _Read]] = {}
    off_sample = off_run = superseded = other_round = misplaced = 0
    for path in sorted(
        (pilot_root / "cases").glob("*/*/events/*/evaluations/*/*/*/evaluation.json")
    ):
        if not _is_run_dir(path.parent.name) or _is_run_dir(path.parent.parent.name):
            misplaced += 1
            continue
        try:
            evaluation = read_model(path, Evaluation)
        except ValueError:
            # Not the validation message: it quotes the agent-written values,
            # and the report's errors reach a public run log.
            raise ValueError(f"{path} does not validate as an evaluation") from None
        if round_id is not None and evaluation.run_id != round_id:
            other_round += 1
            continue
        cell = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id)
        if cell not in sample:
            off_sample += 1
            continue
        if evaluation.prediction_run_id != sample[cell].run_id:
            off_run += 1
            continue
        review = evaluation.predicted_reasoning_review
        read = _Read(
            evaluator_id=evaluation.evaluator_id,
            engine=evaluation.engine,
            grade=evaluation.predicted_reasoning_quality,
            claims=tuple(c.status for c in review.central_claims) if review else (),
        )
        key = (cell, evaluation.evaluator_id)
        if key in newest:
            superseded += 1
            if evaluation.run_id < newest[key][0]:
                continue
        newest[key] = (evaluation.run_id, read)
    reads: dict[Cell, dict[str, _Read]] = defaultdict(dict)
    for (cell, evaluator_id), (_, read) in newest.items():
        reads[cell][evaluator_id] = read
    return _Reads(dict(reads), off_sample, off_run, superseded, other_round, misplaced)


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
    clean_grades = [g[evaluator_id] for g in clean.values() if evaluator_id in g]
    return JudgeGrades(
        evaluator_id=evaluator_id,
        graded=len(graded),
        null=len(mine) - len(graded),
        mean=_mean(clean_grades),
        mean_n=len(clean_grades),
        mean_central_claims=_mean([float(len(r.claims)) for r in graded]),
        claim_status=dict(sorted(statuses.items())),
    )


def _predictor_nulls(reads: Mapping[Cell, Panel]) -> list[PredictorNulls]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for (_, _, predictor_id), panel in reads.items():
        counts[predictor_id][0] += 1
        for r in panel.values():
            counts[predictor_id][1 if r.grade is not None else 2] += 1
    return [
        PredictorNulls(predictor_id=p, cells=cells, graded=graded, null=null)
        for p, (cells, graded, null) in sorted(counts.items())
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
    within = []
    for predictor_id, cells in sorted(by_predictor.items()):
        points = _loo_points(cells, evaluator_id)
        within.append(
            WithinPredictor(
                predictor_id=predictor_id, units=len(points), tau_b=kendall_tau_b(points)
            )
        )
    return LeaveOneOut(
        evaluator_id=evaluator_id,
        units=len(shared),
        cases=len({cell[0] for cell in shared}),
        tau_b=kendall_tau_b(_loo_points(clean.values(), evaluator_id)),
        within_predictor_tau_b=_mean([w.tau_b for w in within if w.tau_b is not None]),
        within_predictor=within,
    )


def _family_grades(
    evaluator_id: str,
    reads: Mapping[Cell, Panel],
    clean: Mapping[Cell, Grades],
    sample: Mapping[Cell, SampleEntry],
) -> FamilyGrades | None:
    own: list[float] = []
    other: list[float] = []
    engine: Engine | None = None
    for cell, panel in reads.items():
        if evaluator_id not in panel or cell not in clean:
            continue
        engine = panel[evaluator_id].engine
        (own if sample[cell].engine == engine else other).append(clean[cell][evaluator_id])
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
    sample: Mapping[Cell, SampleEntry],
    reads: Mapping[Cell, Panel],
    labels: Mapping[Cell, tuple[str, float]],
) -> StageReport:
    sampled = [cell for cell, entry in sample.items() if entry.stage == stage]
    reads = {cell: reads[cell] for cell in sampled if cell in reads}
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
    family = [_family_grades(e, reads, clean, sample) for e in evaluators]
    return StageReport(
        stage=stage,
        sampled=len(sampled),
        cells=len(reads),
        cases=len({cell[0] for cell in reads}),
        unread=len(sampled) - len(reads),
        missing_judge=sum(1 for panel in reads.values() if len(panel) < len(evaluators)),
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


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pilot_report(
    pilot_root: Path,
    sample_dir: Path,
    *,
    labels: Path | None = None,
    prompt_sha256: str | None = None,
    expect_labels_sha256: str | None = None,
    round_id: str | None = None,
) -> PilotReport:
    """The report over one pilot round's evaluations under ``pilot_root``.

    ``pilot_root`` holds **one round**, laid out like ``data/``: a judge's newest
    run per cell is its read, and older runs are counted as superseded rather
    than averaged in, so two rounds under one root would not mix silently but
    would not both be read either. ``sample_dir`` is what
    :func:`write_sample` wrote; only the cells its ``sample.json`` names are
    read, and only where the evaluation graded the sampled prediction run, so
    every figure is over the documents the sample chose. ``labels`` is the
    filled-in packet sheet, read through the ``key.json`` beside it; an
    unfilled label (a null grade) is not a label. Stages read separately, in
    the order cert, interim, merits; a stage the sample does not name is left
    out. With ``round_id`` only that evaluate run's evaluations are read, the
    rest counted as another round's.

    The labels' hash is recorded before the panel's grades are read, so a sheet
    changed after the grades were seen shows: with ``expect_labels_sha256``
    the sheet must hash to it, and ``labels_hash_verified`` says whether it was
    checked.
    """
    if expect_labels_sha256 is not None and labels is None:
        raise ValueError("an expected labels hash needs the label sheet it was recorded for")
    sample_raw = sample_dir.joinpath(SAMPLE_FILE).read_bytes()
    sample = {
        entry.cell: entry
        for entry in (SampleEntry.model_validate(item) for item in json.loads(sample_raw))
    }
    found = _pilot_reads(pilot_root, sample, round_id=round_id)
    labelled: dict[Cell, tuple[str, float]] = {}
    labels_sha256 = key_sha256 = None
    unmatched: list[str] = []
    if labels is not None:
        raw = labels.read_bytes()
        labels_sha256 = _sha256(raw)
        if expect_labels_sha256 is not None and labels_sha256 != expect_labels_sha256.lower():
            raise ValueError(
                f"the label sheet hashes to {labels_sha256}, not the recorded "
                f"{expect_labels_sha256}: it changed after its hash was recorded"
            )
        key_raw = sample_dir.joinpath(KEY_FILE).read_bytes()
        key_sha256 = _sha256(key_raw)
        cells = {
            entry.doc: (entry.case_id, entry.event_id, entry.predictor_id)
            for entry in (PacketKeyEntry.model_validate(item) for item in json.loads(key_raw))
        }
        for entry in (PacketEntry.model_validate(item) for item in json.loads(raw)):
            if entry.grade is None:
                continue
            if entry.doc not in cells:
                raise ValueError(f"label {entry.doc} has no entry in the key")
            cell = cells[entry.doc]
            if cell not in found.reads:
                unmatched.append(entry.doc)
            labelled[cell] = (entry.doc, entry.grade)

    stages = {entry.stage for entry in sample.values()}
    return PilotReport(
        pilot_root=str(pilot_root),
        prompt_sha256=prompt_sha256,
        sample_sha256=_sha256(sample_raw),
        labels_sha256=labels_sha256,
        key_sha256=key_sha256,
        labels_hash_verified=expect_labels_sha256 is not None,
        off_sample=found.off_sample,
        off_run=found.off_run,
        superseded=found.superseded,
        round_id=round_id,
        other_round=found.other_round,
        misplaced=found.misplaced,
        unmatched_labels=sorted(unmatched),
        stages=[
            _stage_report(stage, sample, found.reads, labelled)
            for stage in (Stage.cert, Stage.interim, Stage.merits)
            if stage in stages
        ],
    )
