"""Resolves the on-disk layout for cases, events, predictions, and evaluations.

The layout is **case-centric**: everything derived about a single predictable
event — every predictor's prediction, the realized outcome, and every evaluation
— lives together under one event directory. This keeps the full context for an
evaluation in one place and keeps git diffs local to the thing that changed.

Raw facts (the docket, judges, case metadata, and the dated point-in-time
snapshots) live in the packed corpus (`fedcourtsai.corpus`), not in git. The
``snapshot`` path under ``record/`` is a *provisioning* location only: the
predict/evaluate/reconcile workflows materialize a case's latest corpus snapshot
there, read-only for one run (the tree is gitignored, never committed).

    data/cases/<court_id>/<docket_id>/
        record/snapshots/<YYYY-MM-DD>.json   # provisioned from the corpus (gitignored)
        events/<event_id>/
            event.yaml
            outcome.json
            predictions/<predictor_id>/<run_id>/{prediction.json,reasoning.md,flags.json?}
            evaluations/<evaluator_id>/<predictor_id>/<run_id>/{evaluation.json,evaluation.md}
            evaluations/<evaluator_id>/<run_id>/flags.json?

The ``flags.json`` files are optional: a cell writes one only when it has a
durable, structured note to surface for maintainer triage (see
:class:`fedcourtsai.schemas.AgentFlags`).
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

    def prediction_flags(self, predictor_id: str, run_id: str) -> Path:
        # A predict cell's optional flags.json, alongside its prediction.
        return self.prediction_dir(predictor_id, run_id) / "flags.json"

    def prediction_tooling(self, predictor_id: str, run_id: str) -> Path:
        # A predict cell's optional tooling.json self-report, alongside its prediction.
        return self.prediction_dir(predictor_id, run_id) / "tooling.json"

    def prediction_usage(self, predictor_id: str, run_id: str) -> Path:
        return self.prediction_dir(predictor_id, run_id) / "usage.json"

    def evaluation_usage(self, evaluator_id: str, run_id: str) -> Path:
        # One evaluate cell scores every predictor for the event in a single run,
        # so its usage is keyed by evaluator x run, a level above the per-predictor
        # evaluation directories.
        return self.base / "evaluations" / evaluator_id / run_id / "usage.json"

    def evaluation_flags(self, evaluator_id: str, run_id: str) -> Path:
        # An evaluate cell's optional flags.json, keyed by evaluator x run like its
        # usage (one level above the per-predictor evaluation directories).
        return self.base / "evaluations" / evaluator_id / run_id / "flags.json"

    def evaluation_tooling(self, evaluator_id: str, run_id: str) -> Path:
        # An evaluate cell's optional tooling.json self-report, keyed by evaluator x
        # run like its usage and flags.
        return self.base / "evaluations" / evaluator_id / run_id / "tooling.json"

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
        # Provisioning location for a run's point-in-time snapshot, materialized
        # from the corpus by the predict/evaluate/reconcile workflow. Gitignored
        # (`record/` is never committed) — the snapshot's home is the corpus.
        return self.record / "snapshots" / f"{day}.json"

    @property
    def events_dir(self) -> Path:
        return self.base / "events"

    def event(self, event_id: str) -> EventPaths:
        return EventPaths(self.events_dir / event_id)

    def reconcile_dir(self, run_id: str) -> Path:
        # Reconcile fans out per case (it weighs a case's open events together), so
        # its run-level artifacts live at the case root, above the per-event outcomes.
        return self.base / "reconcile" / run_id

    def reconcile_flags(self, run_id: str) -> Path:
        # A reconcile cell's optional flags.json — e.g. an ambiguous disposition it
        # could not settle — keyed by run at the case level.
        return self.reconcile_dir(run_id) / "flags.json"

    def reconcile_tooling(self, run_id: str) -> Path:
        # A reconcile cell's optional tooling.json self-report, keyed by run.
        return self.reconcile_dir(run_id) / "tooling.json"
