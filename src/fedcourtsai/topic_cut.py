"""Every forecast cut by its case's topic, across the cert, interim and merits moments.

``fedcourts topic-cut`` reads this. It joins each committed forecast to its
case's topic label and reports, per topic and per forecast moment (the
``stage@moment`` key every board aggregates on), how many forecasts there are,
how many are scored, and each predictor's record under the board's own process
scope and strata (:func:`fedcourtsai.leaderboard.aggregate_stratum`).

**The join key depends on the forecast's stage.** A cert or merits forecast
takes the petition's questions-presented label (``qp-topic-v0``,
``data/qp-topics/qp-topics.json``); an interim forecast takes its
application's label (``qp-topic-v1``, ``data/qp-topics/qp-topics-applications.json``).
Both are keyed by ``case_id``. A forecast whose case carries no label — the
frame is not yet fully labeled, the case is outside the labeling frame, or its
frame's artifact is missing or below the gate — is reported in the
:data:`UNLABELED` bucket beside every topic, never dropped, so each moment's
topic rows sum to its whole forecast population.

**Descriptive only.** Nothing is scored on topic and no board conditions on it:
there is no rank, no paired figure and no topic baseline here, only the
board's own per-stratum record re-read over each topic's cells. Every cell
carries its frame's scope string, because a per-topic figure lifted out of the
report must keep the coverage caveat with it: labels are agreement with a
reference block rather than accuracy, the labeled subset was batched rather
than drawn at random from the forecast population, and the application frame's
coverage is a different number from the petition frame's (``docs/qp-topic.md``).

Read-only over the committed ledger and the labels artifacts; it reads no
corpus and writes nothing itself.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .integrity import FORWARD, PROCEDURAL, RETROSPECTIVE, StratifiedCell
from .leaderboard import (
    CellFacts,
    CellSkill,
    aggregate_stratum,
    stage_moment_key,
)
from .paths import CasePaths
from .pipeline import qp_topics
from .schemas import (
    Evaluation,
    PredictableEvent,
    QpTopicApplicationLabels,
    QpTopicLabels,
    Stage,
    TopicCut,
    TopicCutCell,
    TopicCutFrame,
    TopicCutRecord,
)
from .serialize import read_model
from .store import EvaluationKey, iter_predicted_events, normalized_moment, normalized_stage

#: The bucket a forecast whose case carries no topic label is reported in.
UNLABELED = "unlabeled"

TopicFrame = Literal["petitions", "applications"]


def frame_for(stage: Stage | None) -> TopicFrame | None:
    """Which labels frame a forecast of ``stage`` joins: petitions or applications.

    Cert and merits forecasts are forecasts of a petition, so they take its
    questions-presented label; an interim forecast is a forecast of an
    application. A stage-less forecast has no frame and is always unlabeled.
    """
    # Compared by value: the record models store the stage as its string.
    if stage in (Stage.cert, Stage.merits):
        return "petitions"
    if stage == Stage.interim:
        return "applications"
    return None


@dataclass(frozen=True)
class _FrameLabels:
    """One frame's labels, and the scope string every cell it backs carries."""

    frame: TopicFrame
    labels: Mapping[str, str]
    record: TopicCutFrame


def _scope(
    frame: TopicFrame,
    artifact: QpTopicLabels | QpTopicApplicationLabels | None,
    why_absent: str,
) -> str:
    if artifact is None:
        return (
            f"No {frame} topic labels are read ({why_absent}), so every forecast joined to "
            "this frame is unlabeled; no topic share can be stated from it."
        )
    agreement = artifact.agreement
    rate = "n/a" if agreement.overall_rate is None else f"{agreement.overall_rate:.1%}"
    floor = "n/a" if agreement.floor is None else f"{agreement.floor:.1%}"
    newest = artifact.batches[-1] if artifact.batches else None
    frame_rows = (
        f"{newest.frame_rows} rows in the labeling frame at the newest batch's vintage"
        if newest is not None and newest.frame_rows is not None
        else "a labeling frame the newest batch did not count"
    )
    vocabulary = "qp-topic-v1 application" if frame == "applications" else "qp-topic-v0 petition"
    source = (
        "read from the stored application text where provisioned and from the caption, court "
        "below and pre-decision docket entries otherwise, so `unclassifiable` measures thin "
        "dockets as much as subject"
        if frame == "applications"
        else "read from the questions presented alone"
    )
    return (
        f"{vocabulary} labels: {artifact.cases} labeled case(s) of {frame_rows}, "
        f"{source}. Labels are agreement with the frame's reference block "
        f"({agreement.overall_agree}/{agreement.overall_n}, {rate}, against a "
        f"{floor} constant-labeler floor), not accuracy. The labeled subset was batched "
        "from committed state, with the reference block in every batch, not drawn at random "
        "from the forecast population, so a topic's share of forecasts is a share of the "
        "labeled forecasts, read beside the unlabeled row. Descriptive only: nothing is "
        "scored on topic."
    )


def _frame(data_root: Path, frame: TopicFrame) -> _FrameLabels:
    path = (
        qp_topics.application_labels_path(data_root)
        if frame == "applications"
        else qp_topics.labels_path(data_root)
    )
    artifact: QpTopicLabels | QpTopicApplicationLabels | None = None
    why_absent = "no labels artifact is committed"
    if path.is_file():
        read: QpTopicLabels | QpTopicApplicationLabels = (
            read_model(path, QpTopicApplicationLabels)
            if frame == "applications"
            else read_model(path, QpTopicLabels)
        )
        # Re-read rather than assumed from the file's existence, as the docket
        # pack does: the artifact records the flag either way.
        if read.agreement.gate_passed:
            artifact = read
        else:
            why_absent = "its labels artifact records a run below the publication gate"
    labels = {e.case_id: e.label for e in artifact.entries} if artifact is not None else {}
    return _FrameLabels(
        frame=frame,
        labels=labels,
        record=TopicCutFrame(
            frame=frame,
            vocabulary="qp-topic-v1" if frame == "applications" else "qp-topic-v0",
            labeler=artifact.labeler if artifact is not None else None,
            labeled_cases=artifact.cases if artifact is not None else 0,
            agreement_agree=artifact.agreement.overall_agree if artifact is not None else None,
            agreement_n=artifact.agreement.overall_n if artifact is not None else None,
            scope=_scope(frame, artifact, why_absent),
        ),
    )


@dataclass
class _Tally:
    """One (moment, topic) cell's forecast count, filled before the scored cells join it."""

    events: set[tuple[str, str]]
    cells: int


def _forecasts(
    data_root: Path, frames: dict[TopicFrame, _FrameLabels]
) -> dict[tuple[str, str], _Tally]:
    """Every committed forecast's (moment, topic) key, counted by event and by predictor.

    A forecast cell is one predictor's prediction of one event, however many
    runs it holds; the count is of committed forecasts whatever their process
    version, scored or not.
    """
    tallies: dict[tuple[str, str], _Tally] = defaultdict(lambda: _Tally(set(), 0))
    for ref in iter_predicted_events(data_root):
        court, docket = ref.case_id.split("/", 1)
        event_dir = CasePaths(data_root, court, int(docket)).base / "events" / ref.event_id
        event_file = event_dir / "event.yaml"
        if not event_file.is_file():
            continue
        event = read_model(event_file, PredictableEvent)
        stage = normalized_stage(event.kind, event.stage)
        key = stage_moment_key(stage, normalized_moment(stage, event.moment))
        topic = _topic(ref.case_id, stage, frames)
        tally = tallies[(key, topic)]
        tally.events.add((ref.case_id, ref.event_id))
        predictors = event_dir / "predictions"
        tally.cells += sum(1 for p in predictors.iterdir() if p.is_dir())
    return tallies


def _topic(case_id: str, stage: Stage | None, frames: dict[TopicFrame, _FrameLabels]) -> str:
    frame = frame_for(stage)
    if frame is None:
        return UNLABELED
    return frames[frame].labels.get(case_id, UNLABELED)


def build_topic_cut(
    data_root: Path,
    cells: list[StratifiedCell],
    *,
    process_scope: Literal["frozen", "all"],
    skills: dict[EvaluationKey, CellSkill],
    facts: dict[EvaluationKey, CellFacts] | None = None,
    vote_scores: dict[EvaluationKey, float] | None = None,
) -> TopicCut:
    """The per-topic, per-moment forecast cut over ``cells`` (one stratify pass).

    ``cells`` and the per-cell maps are the caller's, built exactly as the
    leaderboard builds them for ``process_scope``; this joins topics onto them
    and re-reads each predictor's record per (moment, topic, stratum). The
    forecast counts read the ledger directly and are scope-free: they count
    every committed forecast, so the scored count beside them says how much of
    the population the scoped record covers.
    """
    frames: dict[TopicFrame, _FrameLabels] = {
        "petitions": _frame(data_root, "petitions"),
        "applications": _frame(data_root, "applications"),
    }
    tallies = _forecasts(data_root, frames)
    scored: dict[tuple[str, str], dict[str, dict[str, list[Evaluation]]]] = defaultdict(
        lambda: defaultdict(lambda: {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []})
    )
    for evaluation, stratum, stage, moment in cells:
        key = (stage_moment_key(stage, moment), _topic(evaluation.case_id, stage, frames))
        scored[key][evaluation.predictor_id][stratum].append(evaluation)
    out: list[TopicCutCell] = []
    for key in sorted(set(tallies) | set(scored)):
        moment_key, topic = key
        tally = tallies.get(key, _Tally(set(), 0))
        predictors = scored.get(key, {})
        frame = frame_for(_stage_of(moment_key))
        records = [
            TopicCutRecord(
                predictor_id=predictor_id,
                events_scored=len(
                    {(ev.case_id, ev.event_id) for evs in strata.values() for ev in evs}
                ),
                forward=aggregate_stratum(strata[FORWARD], skills, facts, vote_scores=vote_scores),
                retrospective=aggregate_stratum(
                    strata[RETROSPECTIVE], skills, facts, vote_scores=vote_scores
                ),
                procedural=aggregate_stratum(
                    strata[PROCEDURAL], skills, facts, vote_scores=vote_scores
                ),
            )
            for predictor_id, strata in sorted(predictors.items())
        ]
        out.append(
            TopicCutCell(
                moment=moment_key,
                frame=frame,
                topic=topic,
                forecast_events=len(tally.events),
                forecast_cells=tally.cells,
                events_scored=len(
                    {
                        (ev.case_id, ev.event_id)
                        for strata in predictors.values()
                        for evs in strata.values()
                        for ev in evs
                    }
                ),
                scope=frames[frame].record.scope
                if frame is not None
                else "A forecast with no stage joins no topic frame, so it is unlabeled.",
                records=records,
            )
        )
    return TopicCut(
        process_scope=process_scope,
        frames=[frames["petitions"].record, frames["applications"].record],
        cells=out,
    )


def _stage_of(moment_key: str) -> Stage | None:
    head = moment_key.split("@", 1)[0]
    return Stage(head) if head in Stage.__members__.values() else None
