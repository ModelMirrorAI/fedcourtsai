"""Resolves the on-disk layout for cases, events, predictions, and evaluations.

The layout is **case-centric**: everything derived about a single predictable
event — every predictor's prediction, the realized outcome, and every evaluation
— lives together under one event directory. This keeps the full context for an
evaluation in one place and keeps git diffs local to the thing that changed.

Raw facts (the docket, judges, case metadata) live in the packed corpus
(`fedcourtsai.corpus`), not in git. The one git raw-fact file that remains is the
dated point-in-time ``snapshot``, kept transitionally so ``pull`` can detect
docket changes the normalized corpus row does not capture.

    data/cases/<court_id>/<docket_id>/
        record/snapshots/<YYYY-MM-DD>.json   # transitional point-in-time snapshot
        events/<event_id>/
            event.yaml
            outcome.json
            predictions/<predictor_id>/<run_id>/{prediction.json,reasoning.md}
            evaluations/<evaluator_id>/<predictor_id>/<run_id>/{evaluation.json,evaluation.md}
"""

from __future__ import annotations

from pathlib import Path


class EventPaths:
    def __init__(self, base: Path) -> None:
        self.base = base

    @property
    def event_file(self) -> Path:
        return self.base / "event.yaml"

    @property
    def outcome(self) -> Path:
        return self.base / "outcome.json"

    def prediction_dir(self, predictor_id: str, run_id: str) -> Path:
        return self.base / "predictions" / predictor_id / run_id

    def prediction(self, predictor_id: str, run_id: str) -> Path:
        return self.prediction_dir(predictor_id, run_id) / "prediction.json"

    def reasoning(self, predictor_id: str, run_id: str) -> Path:
        return self.prediction_dir(predictor_id, run_id) / "reasoning.md"

    def evaluation_dir(self, evaluator_id: str, predictor_id: str, run_id: str) -> Path:
        return self.base / "evaluations" / evaluator_id / predictor_id / run_id

    def evaluation(self, evaluator_id: str, predictor_id: str, run_id: str) -> Path:
        return self.evaluation_dir(evaluator_id, predictor_id, run_id) / "evaluation.json"


class CasePaths:
    def __init__(self, data_root: Path, court_id: str, docket_id: int) -> None:
        self.base = data_root / "cases" / court_id / str(docket_id)

    @property
    def case_file(self) -> Path:
        return self.base / "case.yaml"

    @property
    def record(self) -> Path:
        return self.base / "record"

    @property
    def docket(self) -> Path:
        return self.record / "docket.json"

    def snapshot(self, day: str) -> Path:
        return self.record / "snapshots" / f"{day}.json"

    @property
    def events_dir(self) -> Path:
        return self.base / "events"

    def event(self, event_id: str) -> EventPaths:
        return EventPaths(self.events_dir / event_id)
