"""Engine-runner seam: produce a predict/evaluate cell's artifacts behind an interface.

The live ``run-predict`` / ``run-evaluate`` workflows hand one matrix cell to a
coding agent (``claude-code-action`` or the Codex equivalent), which reasons over
the snapshot and writes the cell's artifacts at the canonical paths. That agent
call costs tokens and only runs inside Actions, so the cell *mechanics* — where
output lands, that it is schema-valid, that ``validate`` accepts it — cannot be
exercised in pytest or locally.

This module is the seam that makes those mechanics testable, mirroring the
:mod:`fedcourtsai.backtest` ``Backtester`` seam (where ``ConstantBacktester`` /
``PriorVoteBacktester`` are offline reference engines). A :class:`Runner` takes
the cell inputs — court, docket, event, the acting predictor/evaluator id, the
run id, the role, the prompt template, and the output root — and is responsible
for writing that cell's artifacts at the paths :mod:`fedcourtsai.ids` /
:mod:`fedcourtsai.paths` resolve. The agentic engines target the same seam in the
workflow; the offline :class:`StubRunner` here writes deterministic, schema-valid
canned artifacts with no model call and no network, so its output is byte-stable
and identical in *shape* to what the workflow produces.

Wiring the live workflow onto this seam is out of scope: the workflow keeps
invoking the real engine. The seam exists so the cell's input/output contract has
a fast, offline reference implementation under test.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from ..ids import case_id as make_case_id
from ..ids import parse_run_id
from ..paths import CasePaths, EventPaths
from ..schemas import Disposition, Engine, Evaluation, Outcome, Prediction, UsageRole
from ..serialize import read_model, write_json
from .evaluate import brier_score, is_correct, vote_accuracy

# Canned values the stub reports. Deterministic by construction — no clock, no
# randomness — so the same request always produces byte-identical artifacts. The
# disposition is the trivial floor (`denied`/0.0), the same baseline
# `ConstantBacktester` uses, so the stub commits to nothing it could be "right"
# about by luck.
_STUB_DISPOSITION = Disposition.denied
_STUB_PROBABILITY = 0.0
_STUB_GRANTED = 0
_STUB_REASONING_QUALITY = 0.5


@dataclass(frozen=True)
class RunRequest:
    """The inputs one predict/evaluate cell receives, role-tagged.

    These are exactly what the workflow passes a cell: the case (``court_id`` /
    ``docket_id``) and ``event_id`` to act on, the acting ``actor_id`` (the
    ``predictor_id`` for a predict cell, the ``evaluator_id`` for an evaluate
    cell), the shared ``run_id``, the ``role`` that selects which artifacts to
    produce, the ``prompt`` template the live engine would follow, and the
    ``data_root`` output root the artifacts are written under.

    ``prompt`` is carried for parity with the live engine (which reads it) even
    though the stub does not consult it; it is part of the cell contract.
    """

    role: UsageRole
    court_id: str
    docket_id: int
    event_id: str
    actor_id: str
    run_id: str
    prompt: Path
    data_root: Path

    @property
    def case_id(self) -> str:
        return make_case_id(self.court_id, self.docket_id)

    @property
    def event_paths(self) -> EventPaths:
        return CasePaths(self.data_root, self.court_id, self.docket_id).event(self.event_id)


class Runner(Protocol):
    """An engine that produces one cell's artifacts at the canonical paths.

    The same seam the agentic engines target in the workflow: given a
    :class:`RunRequest`, write the cell's artifacts (a prediction pair for a
    predict cell, an evaluation pair per scored predictor for an evaluate cell)
    and return the paths written, in sorted order.
    """

    @property
    def backend(self) -> str: ...

    def run(self, request: RunRequest) -> list[Path]: ...


def _created_at(run_id: str) -> datetime:
    """The cell's ``created_at``, derived from the run id so the stub has no clock.

    Run ids are UTC timestamps (:func:`fedcourtsai.ids.run_id`), so reusing the
    run id's instant keeps the stub a pure function of its request.
    """
    return parse_run_id(run_id)


def _input_snapshot(request: RunRequest) -> str:
    """The canonical snapshot path the cell would have read, as a stable string.

    The workflow provisions a case's latest corpus snapshot under ``record/`` and
    the predictor reads it; the stub names that same path (dated from the run id)
    so its ``input_snapshot`` matches the shape of a real prediction. Rendered
    relative to the data root's parent (typically repo-relative, e.g.
    ``data/cases/...``) when possible, else as an absolute path.
    """
    case = CasePaths(request.data_root, request.court_id, request.docket_id)
    snapshot = case.snapshot(_created_at(request.run_id).date().isoformat())
    try:
        return snapshot.relative_to(request.data_root.parent).as_posix()
    except ValueError:
        return snapshot.as_posix()


def _write_text(path: Path, text: str) -> None:
    """Write a newline-terminated markdown note, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


@dataclass(frozen=True)
class StubRunner:
    """Offline reference engine: writes deterministic, schema-valid canned artifacts.

    The runner counterpart to ``ConstantBacktester`` — no model call, no network,
    fully determined by the request. A predict cell yields ``prediction.json`` +
    ``reasoning.md``; an evaluate cell scores every predictor that produced a
    prediction for the event and yields an ``evaluation.json`` + ``evaluation.md``
    pair each, with the quantitative fields computed by the same
    :mod:`fedcourtsai.pipeline.evaluate` helpers the live evaluator must match.
    Output is byte-stable and identical in shape to what the workflow commits, so
    ``validate`` accepts it.
    """

    backend: str = "stub"
    engine: Engine = Engine.claude_code

    def run(self, request: RunRequest) -> list[Path]:
        if request.role == UsageRole.predictor:
            return self._predict(request)
        return self._evaluate(request)

    def _predict(self, request: RunRequest) -> list[Path]:
        events = request.event_paths
        prediction = Prediction(
            case_id=request.case_id,
            event_id=request.event_id,
            predictor_id=request.actor_id,
            engine=self.engine,
            run_id=request.run_id,
            created_at=_created_at(request.run_id),
            input_snapshot=_input_snapshot(request),
            granted=_STUB_GRANTED,
            probability=_STUB_PROBABILITY,
            predicted_disposition=_STUB_DISPOSITION,
        )
        json_path = events.prediction(request.actor_id, request.run_id)
        md_path = events.reasoning(request.actor_id, request.run_id)
        write_json(json_path, prediction)
        _write_text(md_path, self._reasoning_md(request))
        return sorted([json_path, md_path])

    def _evaluate(self, request: RunRequest) -> list[Path]:
        events = request.event_paths
        if not events.outcome.is_file():
            # Nothing to score until the event resolves; mirrors the prompt's
            # "if there is no outcome.json, there is nothing to evaluate".
            return []
        outcome = read_model(events.outcome, Outcome)
        written: list[Path] = []
        for predictor_id, prediction in self._latest_predictions(events):
            evaluation = Evaluation(
                case_id=request.case_id,
                event_id=request.event_id,
                predictor_id=predictor_id,
                evaluator_id=request.actor_id,
                run_id=request.run_id,
                created_at=_created_at(request.run_id),
                correct=is_correct(prediction, outcome),
                brier_score=brier_score(prediction, outcome),
                vote_accuracy=vote_accuracy(prediction, outcome),
                reasoning_quality=_STUB_REASONING_QUALITY,
            )
            dir_ = events.evaluation_dir(request.actor_id, predictor_id, request.run_id)
            json_path = events.evaluation(request.actor_id, predictor_id, request.run_id)
            write_json(json_path, evaluation)
            _write_text(dir_ / "evaluation.md", self._evaluation_md(request, predictor_id))
            written.extend([json_path, dir_ / "evaluation.md"])
        return sorted(written)

    @staticmethod
    def _latest_predictions(events: EventPaths) -> list[tuple[str, Prediction]]:
        """Each predictor's latest prediction for the event, in predictor-id order.

        One evaluate cell scores every predictor once (the
        ``evaluations/<evaluator>/<predictor>/<run>`` layout has no slot for a
        predictor's run id), so where a predictor has several runs the stub scores
        its most recent — the largest ``run_id``, which sorts chronologically.
        """
        predictions_root = events.base / "predictions"
        if not predictions_root.is_dir():
            return []
        scored: list[tuple[str, Prediction]] = []
        for predictor_dir in sorted(p for p in predictions_root.iterdir() if p.is_dir()):
            runs = sorted(
                run_dir
                for run_dir in predictor_dir.iterdir()
                if (run_dir / "prediction.json").is_file()
            )
            if not runs:
                continue
            prediction = read_model(runs[-1] / "prediction.json", Prediction)
            scored.append((predictor_dir.name, prediction))
        return scored

    def _reasoning_md(self, request: RunRequest) -> str:
        return (
            f"# Stub prediction for {request.event_id}\n\n"
            f"Deterministic offline stub output for case `{request.case_id}`, "
            f"predictor `{request.actor_id}`, run `{request.run_id}`. No model was "
            "called and no facts were read; the prediction is the trivial "
            f"`{_STUB_DISPOSITION.value}` floor with P(granted) "
            f"{_STUB_PROBABILITY:.1f}. This document stands in for a real "
            "predictor's qualitative analysis so the cell mechanics can be "
            "exercised offline.\n"
        )

    def _evaluation_md(self, request: RunRequest, predictor_id: str) -> str:
        return (
            f"# Stub evaluation of {predictor_id} for {request.event_id}\n\n"
            f"Deterministic offline stub scoring for case `{request.case_id}`, "
            f"evaluator `{request.actor_id}`, run `{request.run_id}`. The "
            "quantitative fields are computed in code from the prediction and the "
            "realized outcome; the reasoning-quality score is a fixed canned value "
            f"({_STUB_REASONING_QUALITY:.1f}). This document stands in for a real "
            "evaluator's qualitative write-up so the cell mechanics can be "
            "exercised offline.\n"
        )


# Offline backends keyed by name, mirroring how the workflow selects an engine.
# Only the stub exists today; agentic engines plug into the same `Runner` seam in
# the workflow, out of band.
_BACKENDS: dict[str, Runner] = {"stub": StubRunner()}


def get_runner(backend: str = "stub") -> Runner:
    """Return the offline runner registered under ``backend`` (default ``stub``).

    Raises ``KeyError`` for an unknown backend, naming the ones available.
    """
    try:
        return _BACKENDS[backend]
    except KeyError:
        raise KeyError(
            f"unknown runner backend {backend!r}; available: {sorted(_BACKENDS)}"
        ) from None
