"""The release dataset: the ledger re-laid as flat tables for analysis.

``fedcourts export`` builds a bundle a researcher can load without walking the
ledger tree: a ``predictions`` table (one row per prediction in the process
scope), a long-form ``gradings`` table (one row per judge's grading of an
exported prediction), the reasoning documents as JSONL keyed on the same ids,
a data dictionary generated from the row models, the relevant JSON Schemas, a
data licence, and a manifest carrying the source commit and each file's
checksum. The ledger stays authoritative; the bundle is derived from it.

**The rows cannot diverge from the board.** Which gradings count, why an
uncounted one is not, and in which stratum a scored prediction lands all come
from :func:`fedcourtsai.store.stratify`, the same pass the leaderboard
aggregates. The prediction population is the frozen gate the same pass
applies (:func:`fedcourtsai.process_version.is_frozen`), widened to ungraded
predictions; ``forward_claim_excluded`` calls the same breach rule
(:func:`fedcourtsai.integrity.forward_claim_breach`) so it covers an ungraded
prediction too; and ``set_aside`` is the one rule stated here — a breach, or
every in-scope grading leakage-flagged — which under the exclude policy is
exactly "has gradings, none of them counted, because of an integrity rule".

**Exactly one field crosses from the corpus**: the docket number
(:func:`read_docket_numbers` selects that column and no other). Everything
else is the ledger's own work product, as ``docs/data-sources.md`` (*What we
redistribute*) sets out.

**Deterministic.** Rows are sorted on their keys, the CSV, JSONL, Markdown
and manifest carry no build timestamp, and the Parquet writer's options are
pinned, so a rebuild from the same commit, against the same corpus blob,
with the same package and pyarrow versions, reproduces the bundle byte for
byte.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import shutil
import subprocess
import types
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel

from . import corpus
from .blinding import latest_prediction_dirs
from .integrity import FORWARD_CLAIM_POLICY, forward_claim_breach
from .paths import CasePaths
from .process_version import frozen_process_record, graded_post_freeze, is_frozen
from .schemas import (
    EXPORTABLE_MODELS,
    Evaluation,
    ExportCorpusVintage,
    ExportExclusionReason,
    ExportFile,
    ExportGradingRow,
    ExportManifest,
    ExportPredictionRow,
    ExportReasoningRecord,
    Outcome,
    PredictableEvent,
    Stratum,
)
from .serialize import read_model, write_json, write_jsonl, write_raw_json, write_text
from .store import (
    iter_predictions,
    named_document,
    normalized_moment,
    normalized_stage,
    scored_prediction_cell,
    stratify,
)

#: A prediction's identity in the bundle: ``(case_id, event_id, predictor_id, run_id)``.
PredictionKey = tuple[str, str, str, str]

#: A grading's identity: ``(case_id, event_id, predictor_id, evaluator_id, run_id)``.
GradingKey = tuple[str, str, str, str, str]

PREDICTIONS_CSV = "predictions.csv"
PREDICTIONS_PARQUET = "predictions.parquet"
GRADINGS_CSV = "gradings.csv"
GRADINGS_PARQUET = "gradings.parquet"
REASONING_JSONL = "reasoning.jsonl"
DATA_DICTIONARY = "DATA-DICTIONARY.md"
LICENSE_DATA = "LICENSE-DATA"
MANIFEST = "MANIFEST.json"

#: The schemas a bundle carries: its own row and manifest models, plus the three
#: ledger models its rows are drawn from. Keys are ``EXPORTABLE_MODELS`` names,
#: so the bundle's copies are the committed ``schemas/`` files byte for byte.
BUNDLE_SCHEMAS: tuple[str, ...] = (
    "export_prediction_row",
    "export_grading_row",
    "export_reasoning_record",
    "export_manifest",
    "prediction",
    "evaluation",
    "outcome",
)

#: The Parquet writer's options, pinned so the bytes depend on the rows and the
#: installed pyarrow alone — never on a default a pyarrow upgrade may move.
PARQUET_OPTIONS: Mapping[str, object] = types.MappingProxyType(
    {
        "compression": "zstd",
        "compression_level": 9,
        "version": "2.6",
        "data_page_version": "1.0",
        "use_dictionary": True,
        "write_statistics": True,
        "row_group_size": 1_000_000,
    }
)

CC_BY_LEGALCODE = "https://creativecommons.org/licenses/by/4.0/legalcode"


class ExportError(Exception):
    """The bundle cannot be built as asked; the message says why and what to pass."""


@dataclass(frozen=True)
class LedgerCommit:
    """The first-parent commit that added one ``prediction.json``."""

    sha: str
    committed_at: datetime


@dataclass(frozen=True)
class ExportTables:
    """The bundle's three row sets, each already in its deterministic order."""

    predictions: list[ExportPredictionRow]
    gradings: list[ExportGradingRow]
    reasoning: list[ExportReasoningRecord]


def _utc(moment: datetime) -> datetime:
    """An aware UTC datetime; a bare timestamp reads as UTC, as every ledger writer means it."""
    return moment.replace(tzinfo=UTC) if moment.tzinfo is None else moment.astimezone(UTC)


def _grading_key(evaluation: Evaluation) -> GradingKey:
    return (
        evaluation.case_id,
        evaluation.event_id,
        evaluation.predictor_id,
        evaluation.evaluator_id,
        evaluation.run_id,
    )


def _exclusion_reason(
    *, in_scope: bool, counted: bool, forward_claim: bool, leakage: bool
) -> ExportExclusionReason | None:
    """Why a grading is not counted, read off where :func:`stratify` placed it.

    Every in-scope survivor of the run collapse lands in the cells, the
    forward-claim ledger or the leakage ledger, so an in-scope grading in none
    of them is one the collapse dropped: a superseded re-grade.
    """
    if not in_scope:
        return "out_of_scope"
    if counted:
        return None
    if forward_claim and leakage:
        return "forward_claim_and_leakage"
    if forward_claim:
        return "forward_claim"
    if leakage:
        return "leakage"
    return "superseded"


def build_tables(
    data_root: Path,
    *,
    all_versions: bool = False,
    ledger_commits: Mapping[Path, LedgerCommit] | None = None,
) -> ExportTables:
    """The bundle's rows, built from the committed ledger under ``data_root``.

    The population is every committed ``prediction.json`` whose process is
    frozen (:func:`fedcourtsai.process_version.is_frozen`), graded or not —
    the pre-registered record — or, with ``all_versions``, every prediction.
    Gradings are every ``evaluation.json`` whose graded prediction
    (:func:`fedcourtsai.store.scored_prediction_cell`) is in that population,
    with ``counted`` and ``excluded_reason`` read off the same
    :func:`fedcourtsai.store.stratify` pass the leaderboard aggregates.

    ``docket_number`` is left null here; :func:`with_docket_numbers` fills it
    from the corpus. ``ledger_commits`` maps a resolved ``prediction.json`` path to
    the commit that added it; ``None`` leaves those columns null.
    """
    run = stratify(data_root, frozen_only=not all_versions, policy=FORWARD_CLAIM_POLICY)
    strata: dict[GradingKey, Stratum] = {_grading_key(ev): s for ev, s, _st, _m in run.cells}
    forward_claim = {_grading_key(cell.evaluation) for cell in run.excluded}
    leaked = {_grading_key(cell.evaluation) for cell in run.leaked}

    ledger = [
        entry
        for entry in iter_predictions(data_root)
        if all_versions or is_frozen(entry.prediction.process_version)
    ]
    exported: set[PredictionKey] = {
        (entry.case_id, entry.event_id, entry.predictor_id, entry.run_id) for entry in ledger
    }

    gradings: list[ExportGradingRow] = []
    by_prediction: dict[PredictionKey, list[ExportGradingRow]] = {}
    events = sorted({(entry.court_id, entry.docket_id, entry.event_id) for entry in ledger})
    for court_id, docket_id, event_id in events:
        event_dir = CasePaths(data_root, court_id, docket_id).event(event_id).base
        for path in sorted(event_dir.glob("evaluations/*/*/*/evaluation.json")):
            evaluation = read_model(path, Evaluation)
            graded = scored_prediction_cell(
                event_dir, evaluation.predictor_id, evaluation.prediction_run_id
            )
            if graded is None:
                continue
            key: PredictionKey = (
                evaluation.case_id,
                evaluation.event_id,
                evaluation.predictor_id,
                graded[0].name,
            )
            if key not in exported:
                continue
            gkey = _grading_key(evaluation)
            row = ExportGradingRow(
                case_id=evaluation.case_id,
                event_id=evaluation.event_id,
                predictor_id=evaluation.predictor_id,
                prediction_run_id=graded[0].name,
                evaluator_id=evaluation.evaluator_id,
                evaluator_engine=evaluation.engine,
                evaluator_model=evaluation.model,
                run_id=evaluation.run_id,
                correct=evaluation.correct,
                brier_score=evaluation.brier_score,
                brier_skill_score=evaluation.brier_skill_score,
                segment_base_rate=evaluation.segment_base_rate,
                base_rate_salience_version=evaluation.base_rate_salience_version,
                leakage_suspected=evaluation.leakage_suspected,
                counted=gkey in strata,
                excluded_reason=_exclusion_reason(
                    # The prediction is frozen by the population filter, so the
                    # scope gate left to apply is the grading's own time half.
                    in_scope=all_versions or graded_post_freeze(evaluation.process_version),
                    counted=gkey in strata,
                    forward_claim=gkey in forward_claim,
                    leakage=gkey in leaked,
                ),
                process_digest=(
                    evaluation.process_version.digest if evaluation.process_version else None
                ),
                stamped_at=(
                    _utc(evaluation.process_version.stamped_at)
                    if evaluation.process_version
                    else None
                ),
            )
            gradings.append(row)
            by_prediction.setdefault(key, []).append(row)

    predictions: list[ExportPredictionRow] = []
    reasoning: list[ExportReasoningRecord] = []
    event_cache: dict[Path, tuple[PredictableEvent | None, Outcome | None, dict[str, Path]]] = {}
    for entry in ledger:
        event_paths = CasePaths(data_root, entry.court_id, entry.docket_id).event(entry.event_id)
        cached = event_cache.get(event_paths.base)
        if cached is None:
            cached = (
                read_model(event_paths.event_file, PredictableEvent)
                if event_paths.event_file.is_file()
                else None,
                read_model(event_paths.outcome, Outcome) if event_paths.outcome.is_file() else None,
                latest_prediction_dirs(event_paths),
            )
            event_cache[event_paths.base] = cached
        event, outcome, latest = cached
        prediction = entry.prediction
        key = (entry.case_id, entry.event_id, entry.predictor_id, entry.run_id)
        rows = by_prediction.get(key, [])
        judged = [r for r in rows if r.excluded_reason not in ("out_of_scope", "superseded")]
        flagged = sum(1 for r in judged if r.leakage_suspected is True)
        counted_strata = sorted(
            {
                strata[(r.case_id, r.event_id, r.predictor_id, r.evaluator_id, r.run_id)]
                for r in rows
                if r.counted
            }
        )
        breached = outcome is not None and forward_claim_breach(prediction, outcome) is not None
        stage = normalized_stage(event.kind, event.stage) if event is not None else None
        pv = prediction.process_version
        context = prediction.context
        commit = (
            ledger_commits.get(event_paths.prediction(entry.predictor_id, entry.run_id).resolve())
            if ledger_commits is not None
            else None
        )
        predictions.append(
            ExportPredictionRow(
                case_id=entry.case_id,
                court=entry.court_id,
                docket_id=entry.docket_id,
                docket_number=None,
                caption=event.title if event is not None else None,
                event_id=entry.event_id,
                event_kind=event.kind if event is not None else None,
                stage=stage,
                moment=(normalized_moment(stage, event.moment) if event is not None else None),
                predictor_id=entry.predictor_id,
                engine=prediction.engine,
                model=prediction.model,
                run_id=entry.run_id,
                created_at=_utc(prediction.created_at),
                probability=prediction.probability,
                granted=prediction.granted,
                predicted_disposition=prediction.predicted_disposition,
                mode=context.mode if context is not None else None,
                salience_version=context.salience_version if context is not None else None,
                band=context.band if context is not None else None,
                term=context.term if context is not None else None,
                process_label=pv.label if pv is not None else None,
                process_digest=pv.digest if pv is not None else None,
                process_frozen=is_frozen(pv),
                stamped_at=_utc(pv.stamped_at) if pv is not None else None,
                pipeline_sha=pv.pipeline_sha if pv is not None else None,
                ledger_commit=commit.sha if commit is not None else None,
                ledger_committed_at=commit.committed_at if commit is not None else None,
                resolved_at=outcome.resolved_at if outcome is not None else None,
                actual_disposition=outcome.actual_disposition if outcome is not None else None,
                actual_granted=outcome.actual_granted if outcome is not None else None,
                disposition_basis=outcome.disposition_basis if outcome is not None else None,
                stratum=counted_strata[0] if counted_strata else None,
                scored=bool(counted_strata),
                staged=(
                    entry.predictor_id in latest and latest[entry.predictor_id].name == entry.run_id
                ),
                forward_claim_excluded=breached,
                gradings_total=len(judged),
                gradings_leakage_flagged=flagged,
                set_aside=breached or (bool(judged) and flagged == len(judged)),
            )
        )
        cell_dir = event_paths.prediction_dir(entry.predictor_id, entry.run_id)
        reasoning.append(
            ExportReasoningRecord(
                case_id=entry.case_id,
                event_id=entry.event_id,
                predictor_id=entry.predictor_id,
                run_id=entry.run_id,
                predicted_reasoning=named_document(cell_dir, prediction.predicted_reasoning_doc),
                reasoning=named_document(cell_dir, prediction.reasoning_doc),
            )
        )

    predictions.sort(key=lambda r: (r.case_id, r.event_id, r.predictor_id, r.run_id))
    gradings.sort(
        key=lambda r: (
            r.case_id,
            r.event_id,
            r.predictor_id,
            r.prediction_run_id,
            r.evaluator_id,
            r.run_id,
        )
    )
    reasoning.sort(key=lambda r: (r.case_id, r.event_id, r.predictor_id, r.run_id))
    return ExportTables(predictions=predictions, gradings=gradings, reasoning=reasoning)


# --- Inputs from outside the ledger -------------------------------------------


def read_docket_numbers(conn: corpus.ReadConnection, case_ids: Sequence[str]) -> dict[str, str]:
    """The Court-assigned docket number of each case the corpus holds one for.

    Selects the ``docket_number`` column and nothing else: it is the one corpus
    field the release dataset may carry (``docs/data-sources.md``, *What we
    redistribute*), so the query itself is where that boundary is kept. A case
    absent from the corpus, or stored with an empty number, is left out.
    """
    numbers: dict[str, str] = {}
    for case_id in sorted(set(case_ids)):
        record = conn.execute(
            "SELECT docket_number FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
        if record is not None and record["docket_number"]:
            numbers[case_id] = str(record["docket_number"])
    return numbers


def with_docket_numbers(tables: ExportTables, numbers: Mapping[str, str]) -> ExportTables:
    """``tables`` with each prediction row's ``docket_number`` filled from ``numbers``."""
    return ExportTables(
        predictions=[
            row.model_copy(update={"docket_number": numbers.get(row.case_id)})
            for row in tables.predictions
        ],
        gradings=tables.gradings,
        reasoning=tables.reasoning,
    )


def corpus_vintage(conn: corpus.ReadConnection, backend: str) -> ExportCorpusVintage:
    """The blob's freshness, as ``fedcourts corpus-info`` reports it."""
    return ExportCorpusVintage(
        backend=backend,
        latest_pull=corpus.latest_pull_date(conn),
        latest_snapshot=corpus.latest_snapshot_date(conn),
    )


def _git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` and return stdout; a failure raises :class:`ExportError`.

    An inherited ``GIT_DIR`` / ``GIT_WORK_TREE`` (a hook's environment) would
    override ``-C``, so both are dropped: the repository is the one holding the
    ledger.
    """
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    try:
        done = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else exc
        raise ExportError(f"git {' '.join(args[:2])} failed in {repo}: {detail}") from exc
    return done.stdout


@dataclass(frozen=True)
class GitSource:
    """Where the ledger's history lives and which commit is checked out."""

    toplevel: Path
    head: str
    dirty: bool


def git_source(data_root: Path) -> GitSource:
    """The checkout holding ``data_root``: its top level, HEAD, and whether it is dirty.

    Refuses a shallow clone: its one fetched commit is grafted parentless, so a
    history read would attribute every file to the tip. Dirty means a modified
    tracked file anywhere, or an untracked file under the ledger — either makes
    the bundle something other than the commit it names.
    """
    if not data_root.is_dir():
        raise ExportError(f"no ledger at {data_root}")
    toplevel = Path(_git(data_root, "rev-parse", "--show-toplevel").strip())
    if _git(toplevel, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise ExportError(
            "the checkout is a shallow clone, whose history cannot say which commit added "
            "each prediction; fetch full history (`git fetch --unshallow`) or pass --no-git"
        )
    head = _git(toplevel, "rev-parse", "HEAD").strip()
    tracked = _git(toplevel, "status", "--porcelain", "--untracked-files=no").strip()
    untracked = _git(
        toplevel, "status", "--porcelain", "--untracked-files=all", "--", str(data_root.resolve())
    ).strip()
    return GitSource(toplevel=toplevel, head=head, dirty=bool(tracked or untracked))


def ledger_commit_index(data_root: Path, source: GitSource) -> dict[Path, LedgerCommit]:
    """Each committed ``prediction.json`` mapped to the first-parent commit that added it.

    One ``git log --first-parent`` pass over the ledger, not a read per file.
    Following first parents from HEAD, an addition that arrived through a merge
    is attributed to the merge commit that landed it on the checked-out line —
    on ``main``, the merge or squash commit, whose committer date is the
    server's for a web merge. Renames are not followed, so a moved file is
    attributed to the commit that put it at its current path; walking
    newest-first, the newest addition wins, the one the current file is.
    """
    try:
        cases = (data_root.resolve() / "cases").relative_to(source.toplevel.resolve())
    except ValueError as exc:
        raise ExportError(
            f"the ledger {data_root} resolves outside the checkout {source.toplevel}"
        ) from exc
    out = _git(
        source.toplevel,
        "-c",
        "core.quotePath=false",
        "log",
        "--first-parent",
        "--diff-merges=first-parent",
        "--no-renames",
        "--diff-filter=A",
        "--name-only",
        "--format=%x00%H %cI",
        "--",
        f":(glob){cases.as_posix()}/**/prediction.json",
    )
    index: dict[Path, LedgerCommit] = {}
    for record in out.split("\x00"):
        lines = [line for line in record.splitlines() if line]
        if not lines:
            continue
        sha, _, stamp = lines[0].partition(" ")
        commit = LedgerCommit(sha=sha, committed_at=_utc(datetime.fromisoformat(stamp)))
        for name in lines[1:]:
            index.setdefault((source.toplevel / name).resolve(), commit)
    return index


# --- Writing the bundle -------------------------------------------------------


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    """``(inner, nullable)`` for ``X | None``; any other annotation is ``(it, False)``."""
    if get_origin(annotation) in (Union, types.UnionType):
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
    return annotation, False


def _is_literal(annotation: Any) -> bool:
    return get_origin(annotation) is Literal


def _type_label(annotation: Any) -> str:
    """How the data dictionary names a column's type."""
    inner, nullable = _unwrap_optional(annotation)
    if _is_literal(inner):
        label = "string, one of " + ", ".join(f"`{v}`" for v in get_args(inner))
    elif isinstance(inner, type) and issubclass(inner, Enum):
        label = "string, one of " + ", ".join(f"`{m.value}`" for m in inner)
    elif inner is bool:
        label = "boolean"
    elif inner is int:
        label = "integer"
    elif inner is float:
        label = "number"
    elif inner is datetime:
        label = "timestamp (UTC, ISO 8601)"
    elif inner is date:
        label = "date (ISO 8601)"
    elif inner is str:
        label = "string"
    else:
        raise TypeError(f"no export column type for {annotation!r}")
    return f"{label}; nullable" if nullable else label


def _arrow_schema(model: type[BaseModel]) -> Any:
    """The Parquet schema for a row model, read off its fields and descriptions."""
    import pyarrow as pa  # noqa: PLC0415 - lazy: only the export pays for pyarrow

    fields = []
    for name, info in model.model_fields.items():
        inner, nullable = _unwrap_optional(info.annotation)
        if (
            _is_literal(inner)
            or inner is str
            or (isinstance(inner, type) and issubclass(inner, Enum))
        ):
            arrow_type = pa.string()
        elif inner is bool:
            arrow_type = pa.bool_()
        elif inner is int:
            arrow_type = pa.int64()
        elif inner is float:
            arrow_type = pa.float64()
        elif inner is datetime:
            arrow_type = pa.timestamp("us", tz="UTC")
        elif inner is date:
            arrow_type = pa.date32()
        else:
            raise TypeError(f"no Parquet type for {model.__name__}.{name}: {info.annotation!r}")
        metadata = {"description": info.description} if info.description else None
        fields.append(pa.field(name, arrow_type, nullable=nullable, metadata=metadata))
    return pa.schema(fields)


def _python_value(value: object) -> object:
    """A row value as pyarrow takes it: an enum member as its string value."""
    return value.value if isinstance(value, Enum) else value


def write_parquet(path: Path, model: type[BaseModel], rows: Sequence[BaseModel]) -> None:
    """Write rows as one Parquet table with the pinned writer options."""
    import pyarrow as pa  # noqa: PLC0415 - lazy: only the export pays for pyarrow
    import pyarrow.parquet as pq  # noqa: PLC0415

    schema = _arrow_schema(model)
    columns = {
        name: [_python_value(getattr(row, name)) for row in rows] for name in model.model_fields
    }
    table = pa.Table.from_pydict(columns, schema=schema)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, str(path), **PARQUET_OPTIONS)


def _csv_cell(value: object) -> str:
    """A JSON-mode value as its CSV text: empty for null, lowercase booleans."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_csv(path: Path, model: type[BaseModel], rows: Sequence[BaseModel]) -> None:
    """Write rows as CSV with a header, ``\\n`` line endings, minimal quoting."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    names = list(model.model_fields)
    writer.writerow(names)
    for row in rows:
        payload = row.model_dump(mode="json")
        writer.writerow([_csv_cell(payload[name]) for name in names])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(buffer.getvalue(), encoding="utf-8")


DICTIONARY_TABLES: tuple[tuple[str, type[BaseModel]], ...] = (
    (f"`{PREDICTIONS_CSV}` / `{PREDICTIONS_PARQUET}`", ExportPredictionRow),
    (f"`{GRADINGS_CSV}` / `{GRADINGS_PARQUET}`", ExportGradingRow),
    (f"`{REASONING_JSONL}`", ExportReasoningRecord),
)

DICTIONARY_PREAMBLE = f"""# FedCourtsAI ledger export: data dictionary

This bundle re-lays the FedCourtsAI prediction ledger as flat tables. The
ledger in the project's git history is authoritative; every row here is
derived from it at the commit `{MANIFEST}` names.

## What the rows are

- **Predictions.** Under the `frozen` scope (the release) the population is
  every committed prediction made by a pre-registered frozen process at or
  after the freeze instant, graded or not; `{MANIFEST}` records the blessed
  digests and the instant. The `all` scope widens it to every process version
  and is diagnostic only.
- **Counted and set aside.** `scored` marks a prediction at least one counted
  grading names; `stratum` then says which stratum the scored figures place it
  in. A prediction is `set_aside` when its record claims a forward forecast the
  outcome's date contradicts (`forward_claim_excluded`), or when every in-scope
  judge flagged possible leakage. One flagged judge among several does not set
  a prediction aside; that grading alone is left uncounted. An unresolved
  prediction has null outcome columns and is neither scored nor set aside.
- **Gradings.** One row per judge's grading of an exported prediction, joined
  to it on `case_id`, `event_id`, `predictor_id` and `prediction_run_id`.
  Superseded re-grades and gradings unstamped or stamped before the freeze
  are kept, with `counted` false and `excluded_reason` saying why.
- **Rows are runs.** A row is one run of one predictor on one event of
  one case; a case with several events, predictors or runs has several rows.

## Licence and attribution

The data files are licensed under CC BY 4.0 ({CC_BY_LEGALCODE}); the
schemas under `schemas/` under the BSD 3-Clause License. See `{LICENSE_DATA}`.

This project builds on court data from CourtListener, a project of the Free
Law Project (https://free.law/, https://www.courtlistener.com/). Most case ids
here are CourtListener docket ids; a petition the Court's own site reached
first carries a reserved-range id the project mints. The ledger was built from
that corpus either way, but the bundle carries no CourtListener content: its
only corpus field is `docket_number`, the number the Court itself assigned.
The underlying federal court records are public records. The predictions and
evaluations are model-generated and are not official court records; FedCourtsAI
is not affiliated with or endorsed by the Free Law Project or any court.
"""


def render_data_dictionary() -> str:
    """The bundle's ``DATA-DICTIONARY.md``: the fixed preamble, then every row model's fields.

    Generated from the row models, so a column the code adds, drops or
    re-describes changes the dictionary with it.
    """
    parts = [DICTIONARY_PREAMBLE]
    for title, model in DICTIONARY_TABLES:
        doc = " ".join((model.__doc__ or "").split("\n\n")[0].split())
        parts.append(f"\n## {title}\n\n{doc}\n\n| Column | Type | Description |\n|---|---|---|\n")
        for name, info in model.model_fields.items():
            description = (info.description or "").replace("|", "\\|")
            parts.append(f"| `{name}` | {_type_label(info.annotation)} | {description} |\n")
    return "".join(parts)


LICENSE_DATA_TEXT = f"""FedCourtsAI ledger export
Copyright (c) 2026 Model Mirror, LLC

The data files in this bundle ({PREDICTIONS_CSV}, {PREDICTIONS_PARQUET},
{GRADINGS_CSV}, {GRADINGS_PARQUET}, {REASONING_JSONL}, {DATA_DICTIONARY}
and {MANIFEST}) are licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0):
{CC_BY_LEGALCODE}

Attribution: "FedCourtsAI ledger export, Model Mirror, LLC, CC BY 4.0",
with the source commit named in {MANIFEST}.

The licence covers the project's own predictions, outcomes and evaluations.
The underlying U.S. federal court records are public records, and the docket
numbers are identifiers the Court assigned.

The JSON Schemas under schemas/ are generated from the FedCourtsAI source code
and are licensed under the BSD 3-Clause License, the licence of that code.
"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class BuildContext:
    """How the bundle was built, for its manifest."""

    build_command: str
    package_version: str
    all_versions: bool
    source: GitSource | None
    vintage: ExportCorpusVintage | None


def write_bundle(out: Path, tables: ExportTables, context: BuildContext) -> ExportManifest:
    """Write the bundle into ``out``, which must be absent or empty, and return its manifest."""
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ExportError(f"{out} is not an empty directory; the bundle needs a fresh one")
    out.mkdir(parents=True, exist_ok=True)
    try:
        write_csv(out / PREDICTIONS_CSV, ExportPredictionRow, tables.predictions)
        write_parquet(out / PREDICTIONS_PARQUET, ExportPredictionRow, tables.predictions)
        write_csv(out / GRADINGS_CSV, ExportGradingRow, tables.gradings)
        write_parquet(out / GRADINGS_PARQUET, ExportGradingRow, tables.gradings)
        write_jsonl(out / REASONING_JSONL, tables.reasoning)
        write_text(out / DATA_DICTIONARY, render_data_dictionary())
        write_text(out / LICENSE_DATA, LICENSE_DATA_TEXT)
        for name in BUNDLE_SCHEMAS:
            write_raw_json(
                out / "schemas" / f"{name}.schema.json",
                EXPORTABLE_MODELS[name].model_json_schema(),
            )
        files = [
            ExportFile(
                path=path.relative_to(out).as_posix(),
                sha256=_sha256(path),
                size=path.stat().st_size,
            )
            for path in sorted(p for p in out.rglob("*") if p.is_file())
        ]
        predictions = tables.predictions
        manifest = ExportManifest(
            source_commit=context.source.head if context.source else None,
            source_dirty=context.source.dirty if context.source else None,
            build_command=context.build_command,
            package_version=context.package_version,
            process_scope="all" if context.all_versions else "frozen",
            frozen_process=None if context.all_versions else frozen_process_record(),
            forward_claim_policy=FORWARD_CLAIM_POLICY,
            ledger_commits="git" if context.source else "omitted",
            docket_numbers="corpus" if context.vintage else "omitted",
            corpus_vintage=context.vintage,
            counts={
                "predictions": len(predictions),
                "gradings": len(tables.gradings),
                "reasoning": len(tables.reasoning),
                "predictions_scored": sum(r.scored for r in predictions),
                "predictions_set_aside": sum(r.set_aside for r in predictions),
                "predictions_resolved": sum(r.resolved_at is not None for r in predictions),
                "gradings_counted": sum(r.counted for r in tables.gradings),
                "predictions_without_ledger_commit": sum(
                    r.ledger_commit is None for r in predictions
                ),
                "predictions_without_docket_number": sum(
                    r.docket_number is None for r in predictions
                ),
            },
            files=files,
        )
        write_json(out / MANIFEST, manifest)
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    return manifest


def verify_bundle(out: Path) -> list[str]:
    """Every mismatch between the manifest's checksums and the files in ``out``."""
    manifest = read_model(out / MANIFEST, ExportManifest)
    problems: list[str] = []
    listed = {entry.path for entry in manifest.files}
    for entry in manifest.files:
        path = out / entry.path
        if not path.is_file():
            problems.append(f"{entry.path}: missing")
        elif _sha256(path) != entry.sha256:
            problems.append(f"{entry.path}: checksum mismatch")
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        relative = path.relative_to(out).as_posix()
        if relative != MANIFEST and relative not in listed:
            problems.append(f"{relative}: not in the manifest")
    return problems
