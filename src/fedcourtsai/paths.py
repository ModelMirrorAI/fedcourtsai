"""Resolves the on-disk layout for cases, events, predictions, and evaluations.

The layout is **case-centric**: everything derived about a single predictable
event — every predictor's prediction, the realized outcome, and every evaluation
— lives together under one event directory. This keeps the full context for an
evaluation in one place and keeps git diffs local to the thing that changed.

Raw facts (the docket, judges, case metadata, and the dated point-in-time
snapshots) live in the packed corpus (`fedcourtsai.corpus`), not in git. The
``snapshot`` path under ``record/`` is a *provisioning* location only: the
predict/evaluate workflows materialize a case's latest corpus snapshot
there, read-only for one run (the tree is gitignored, never committed). The
evaluate cell also stages its blinded candidates there
(:mod:`fedcourtsai.blinding`), for the same reason — a masked copy of a
prediction must never reach the ledger. The map that would unmask them is the
one blinding artifact that does *not* live here: the grader is sent into
``record/``, so its key is kept out of the tree entirely.

    data/cases/<court_id>/<docket_id>/
        record/snapshots/<YYYY-MM-DD>.json   # provisioned from the corpus (gitignored)
        record/blinded/<alias>/              # the evaluate cell's blinded candidates (gitignored)
        events/<event_id>/
            event.yaml
            outcome.json
            predictions/<predictor_id>/<run_id>/{prediction.json,reasoning.md,
                                                predicted_reasoning.md?,flags.json?}
            evaluations/<evaluator_id>/<predictor_id>/<run_id>/{evaluation.json,evaluation.md}
            evaluations/<evaluator_id>/<run_id>/flags.json?

The ``flags.json`` files are optional: a cell writes one only when it has a
durable, structured note to surface for maintainer triage (see
:class:`fedcourtsai.schemas.AgentFlags`).

The corpus's own two halves are addressed here too — see *Corpus store
addressing* below. They are not on-disk paths, but they are the same kind of
thing this module exists for: a layout derived in one place rather than
hand-assembled per call site.
"""

from __future__ import annotations

from pathlib import Path

# --- Corpus store addressing --------------------------------------------------
#
# One **base URL** names an environment's whole corpus estate
# (``s3://<bucket>[/<prefix>]``, supplied out of band — see SECURITY.md). The two
# halves the corpus has sit at fixed segments beneath it: the index remote that
# `fedcourtsai.corpus_remote` publishes the blob to, and the per-case content
# store `fedcourtsai.casestore` mirrors payloads to. Deriving both from one
# address is what makes an environment a single setting: pointing the index at
# one environment while the store answers from another is unrepresentable, and a
# new environment costs one variable rather than a pair that can disagree.
#
# The content store's segment carries the store layout's **version**, and it
# belongs here — beside the code that reads that layout — rather than inside a
# configured URL. A store-format migration then rides a promotion, where the
# reader and the address it reads move together, instead of being a settings
# edit racing one.

#: The index remote's segment under an environment's base URL.
CORPUS_INDEX_SEGMENT = "store"

#: The per-case content store's segment, layout version included.
CASESTORE_SEGMENT = "casestore/v1"


def _under_base(base_url: str, segment: str) -> str:
    """``<base_url>/<segment>``, tolerating padding and a trailing slash.

    Refuses a blank base outright: the alternative is a bare ``/<segment>``
    relative-looking URL that no parser rejects for the reason it is wrong, so
    a store address would silently become nonsense instead of failing where the
    configuration is missing.
    """
    base = base_url.strip().rstrip("/")
    if not base:
        raise ValueError("corpus base URL is empty; nothing to derive a store address from")
    return f"{base}/{segment}"


def corpus_index_url(base_url: str) -> str:
    """The corpus index remote's URL under an environment's base URL."""
    return _under_base(base_url, CORPUS_INDEX_SEGMENT)


def casestore_url(base_url: str) -> str:
    """The per-case content store's URL under an environment's base URL."""
    return _under_base(base_url, CASESTORE_SEGMENT)


class EventPaths:
    def __init__(self, base: Path) -> None:
        self.base = base

    @property
    def event_file(self) -> Path:
        return self.base / "event.yaml"

    @property
    def outcome(self) -> Path:
        return self.base / "outcome.json"

    def sibling(self, event_id: str) -> EventPaths:
        """Another event of the **same case**.

        The one cross-event read the ledger layout supports: events sit
        side-by-side under the case, so a later forecast moment can reach the
        first moment's definition without knowing the case path it was built
        from.
        """
        return EventPaths(self.base.parent / event_id)

    @property
    def predictions_dir(self) -> Path:
        return self.base / "predictions"

    def prediction_dir(self, predictor_id: str, run_id: str) -> Path:
        return self.predictions_dir / predictor_id / run_id

    def prediction(self, predictor_id: str, run_id: str) -> Path:
        return self.prediction_dir(predictor_id, run_id) / "prediction.json"

    def reasoning(self, predictor_id: str, run_id: str) -> Path:
        # The predictor's rationale for its own numbers (`reasoning_doc`).
        return self.prediction_dir(predictor_id, run_id) / "reasoning.md"

    def predicted_reasoning(self, predictor_id: str, run_id: str) -> Path:
        # The forecast of the Court's own reasoning (`predicted_reasoning_doc`) —
        # claims that resolve against the docket, kept out of the rationale above
        # so the two can be read, and later scored, separately. The pointer is
        # optional, so a prediction may name no document here.
        return self.prediction_dir(predictor_id, run_id) / "predicted_reasoning.md"

    def prediction_flags(self, predictor_id: str, run_id: str) -> Path:
        # A predict cell's optional flags.json, alongside its prediction.
        return self.prediction_dir(predictor_id, run_id) / "flags.json"

    def prediction_tooling(self, predictor_id: str, run_id: str) -> Path:
        # A predict cell's optional tooling.json self-report, alongside its prediction.
        return self.prediction_dir(predictor_id, run_id) / "tooling.json"

    def prediction_attempt(self, predictor_id: str, run_id: str) -> Path:
        # A predict cell's durable failure fact, written by the corpus-blind collect
        # job when the cell ran and produced no usable prediction. Run-scoped so a
        # rerun overwrites; counted per (predictor, event) against the attempt cap.
        return self.prediction_dir(predictor_id, run_id) / "attempt.json"

    def prediction_usage(self, predictor_id: str, run_id: str) -> Path:
        return self.prediction_dir(predictor_id, run_id) / "usage.json"

    def prediction_retrieval_log(self, predictor_id: str, run_id: str) -> Path:
        # The harness-captured tool-call transcript, beside usage.json.
        return self.prediction_dir(predictor_id, run_id) / "retrieval_log.json"

    @property
    def evaluations_dir(self) -> Path:
        # Every evaluator's output for the event, the sibling of predictions_dir.
        return self.base / "evaluations"

    def evaluation_cell_dir(self, evaluator_id: str, run_id: str) -> Path:
        # One evaluate cell's own run-keyed files, a level above the per-predictor
        # evaluation directories: a single cell scores every predictor for the
        # event, so its usage, transcript, flags, and tooling report are keyed by
        # evaluator x run rather than per predictor.
        return self.base / "evaluations" / evaluator_id / run_id

    def evaluation_usage(self, evaluator_id: str, run_id: str) -> Path:
        return self.evaluation_cell_dir(evaluator_id, run_id) / "usage.json"

    def evaluation_retrieval_log(self, evaluator_id: str, run_id: str) -> Path:
        # The harness-captured tool-call transcript, keyed like its usage.
        return self.evaluation_cell_dir(evaluator_id, run_id) / "retrieval_log.json"

    def evaluation_flags(self, evaluator_id: str, run_id: str) -> Path:
        # An evaluate cell's optional flags.json.
        return self.evaluation_cell_dir(evaluator_id, run_id) / "flags.json"

    def evaluation_tooling(self, evaluator_id: str, run_id: str) -> Path:
        # An evaluate cell's optional tooling.json self-report.
        return self.evaluation_cell_dir(evaluator_id, run_id) / "tooling.json"

    def evaluation_attempt(self, evaluator_id: str, run_id: str) -> Path:
        # An evaluate cell's durable failure fact. Written by the corpus-blind
        # collect job; counted per (evaluator, event) against the attempt cap.
        return self.evaluation_cell_dir(evaluator_id, run_id) / "attempt.json"

    def evaluator_dir(self, evaluator_id: str) -> Path:
        # One evaluator's whole output for the event: the per-predictor
        # evaluation directories plus its own run-keyed cell files.
        return self.base / "evaluations" / evaluator_id

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
        # from the corpus by the predict/evaluate workflow. Gitignored
        # (`record/` is never committed) — the snapshot's home is the corpus.
        return self.record / "snapshots" / f"{day}.json"

    @property
    def cell_context(self) -> Path:
        # The cell's provisioned mode (`{"mode": "forward" | "replay", ...}`):
        # written at provisioning so the prompt contract can key etiquette on it.
        # Gitignored with the rest of record/.
        return self.record / "context.json"

    @property
    def blinded_predictions(self) -> Path:
        # Staging area for the evaluate cell's blinded candidates, one
        # `<alias>/` directory each (:mod:`fedcourtsai.blinding`). Gitignored
        # with the rest of record/, which is what keeps the masked copies off
        # the ledger. The alias map that would undo them lives outside this tree
        # entirely — the grader is sent in here, so the key does not live here.
        return self.record / "blinded"

    def blinded_prediction_dir(self, alias: str) -> Path:
        return self.blinded_predictions / alias

    @property
    def documents_dir(self) -> Path:
        # Provisioning location for the case's fetched filed-document text
        # (petition, questions presented, BIO, and on an application docket the
        # application itself), materialized from the corpus alongside the
        # snapshot. Gitignored like everything in record/.
        return self.record / "documents"

    def document(self, kind: str) -> Path:
        return self.documents_dir / f"{kind}.txt"

    @property
    def documents_manifest(self) -> Path:
        return self.documents_dir / "documents.json"

    @property
    def events_dir(self) -> Path:
        return self.base / "events"

    def event(self, event_id: str) -> EventPaths:
        return EventPaths(self.events_dir / event_id)
