"""Corpus integrity + cross-store referential validation.

``fedcourts validate`` checks every git-ledger artifact under ``data/`` against
its schema, one file at a time. It never opens the corpus, and nothing asserts
that the two stores *agree*. This module is that complement: it opens the packed
corpus and runs the correctness invariants the data must satisfy end to end,
returning a :class:`fedcourtsai.schemas.CorpusValidation` verdict.

Two layers of checks:

* **corpus integrity** — what the corpus must satisfy on its own: it opens; its
  row count never regresses against a supplied baseline (the append-only
  invariant the write role + bucket versioning enforce; absent a baseline this is
  a no-op pass); required identifier columns are non-empty; no point-in-time
  snapshot is future-dated; and no case or event id is duplicated.
* **referential integrity** — the cross-store checks nothing does today: every
  ``outcome``/``prediction``/``evaluation`` under ``data/`` references a case and
  event that exist in the corpus (no orphan judgments); every evaluation targets a
  predictor that actually produced a prediction for that event; and the seed
  cursor reconciles against the corpus' per-court row counts.

The verdict is a pure function of its inputs (corpus, ledger, cursor, baseline,
as-of date), with no clock or network, so it is deterministic and offline. Each
check is a small function returning one :class:`CorpusCheck`, and the orchestrator
is split into a corpus-needing half and a git-only half so a later PR-time gate can
reuse the git-only subset.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import yaml

from . import corpus
from .schemas import (
    FILENAME_MODELS,
    CorpusCheck,
    CorpusValidation,
    LedgerValidation,
    SeedProgress,
)

# Cap the per-check problem sample so a pathological corpus cannot produce an
# unbounded verdict; `CorpusCheck.failures` still carries the true total.
_MAX_PROBLEMS = 20

# Stable check identifiers (the `name` field of each emitted CorpusCheck).
CHECK_CORPUS_OPENS = "corpus_opens"
CHECK_ROW_COUNT_MONOTONIC = "row_count_monotonic"
CHECK_REQUIRED_COLUMNS = "required_columns_non_empty"
CHECK_SNAPSHOT_NOT_FUTURE = "snapshot_not_future_dated"
CHECK_NO_DUPLICATES = "no_duplicate_cases_or_events"
CHECK_LEDGER_REFERENCES = "ledger_references_exist"
CHECK_EVALUATION_TARGETS = "evaluation_targets_prediction"
CHECK_SEED_CURSOR = "seed_cursor_reconciles"


def _check(name: str, problems: list[str], *, checked: int, detail: str = "") -> CorpusCheck:
    """Assemble one check result from its sampled problems (passed iff none)."""
    return CorpusCheck(
        name=name,
        passed=not problems,
        checked=checked,
        failures=len(problems),
        detail=detail,
        problems=sorted(problems)[:_MAX_PROBLEMS],
    )


# --- schema conformance (layer A, git ledger only) -----------------------------


def validate_ledger(path: Path) -> LedgerValidation:
    """Validate every known artifact under ``path`` against its schema model.

    The corpus-free, git-only half of data health: the same per-file schema check
    the ``validate`` command (and the PR gate) runs, returned as a structured
    :class:`LedgerValidation` so the ops dashboard can present it alongside the
    corpus verdict. ``problems`` is capped like the corpus checks; ``invalid`` is
    the true failure count.
    """
    problems: list[str] = []
    checked = 0
    for file in sorted(path.rglob("*")):
        model = FILENAME_MODELS.get(file.name)
        if model is None or not file.is_file():
            continue
        checked += 1
        try:
            text = file.read_text()
            data = json.loads(text) if file.suffix == ".json" else yaml.safe_load(text)
            model.model_validate(data)
        except Exception as exc:
            problems.append(f"{file}: {exc}")
    return LedgerValidation(
        ok=not problems,
        checked=checked,
        invalid=len(problems),
        problems=sorted(problems)[:_MAX_PROBLEMS],
    )


# --- corpus integrity (layer B) ------------------------------------------------


def check_row_count_monotonic(conn: sqlite3.Connection, baseline_count: int | None) -> CorpusCheck:
    """Row count must not regress below a prior baseline (append-only invariant).

    The corpus only ever grows — the write role appends and bucket versioning
    guards history — so a count below the last observed one is a red flag. The
    baseline's transport is the wiring layer's job; absent one this is a no-op
    pass.
    """
    rows = corpus.count(conn)
    problems: list[str] = []
    if baseline_count is not None and rows < baseline_count:
        problems.append(f"row count {rows} dropped below baseline {baseline_count}")
    detail = (
        "no baseline supplied; monotonic check skipped"
        if baseline_count is None
        else f"{rows} rows vs baseline {baseline_count}"
    )
    return _check(CHECK_ROW_COUNT_MONOTONIC, problems, checked=rows, detail=detail)


def check_required_columns(conn: sqlite3.Connection) -> CorpusCheck:
    """Identifier columns that anchor the data model must be non-empty.

    ``case_id``/``court`` on cases, the ``(case_id, event_id, court, kind)`` spine
    on events, and ``(case_id, snapshot_date)`` on snapshots are declared NOT NULL,
    but an empty string slips past that — and an empty id silently breaks every
    referential join — so it is flagged here.
    """
    checked = corpus.count(conn) + corpus.event_count(conn) + corpus.snapshot_count(conn)
    problems: list[str] = []
    for record in conn.execute(
        "SELECT case_id FROM cases WHERE trim(coalesce(case_id, '')) = '' "
        "OR trim(coalesce(court, '')) = '' ORDER BY rowid LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(f"case row has an empty case_id/court (case_id={record['case_id']!r})")
    for record in conn.execute(
        "SELECT case_id, event_id FROM events WHERE trim(coalesce(case_id, '')) = '' "
        "OR trim(coalesce(event_id, '')) = '' OR trim(coalesce(court, '')) = '' "
        "OR trim(coalesce(kind, '')) = '' ORDER BY rowid LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(
            f"event row has an empty id/court/kind ({record['case_id']!r}, {record['event_id']!r})"
        )
    for record in conn.execute(
        "SELECT case_id FROM snapshots WHERE trim(coalesce(case_id, '')) = '' "
        "OR trim(coalesce(snapshot_date, '')) = '' OR trim(coalesce(payload, '')) = '' "
        "ORDER BY rowid LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(f"snapshot row has an empty case_id/date/payload ({record['case_id']!r})")
    return _check(CHECK_REQUIRED_COLUMNS, problems, checked=checked)


def check_snapshot_not_future(conn: sqlite3.Connection, today: date) -> CorpusCheck:
    """No point-in-time snapshot may be dated after the as-of date.

    A snapshot is a record of facts observed at a past pull; a future date means a
    clock or ingestion bug. ``snapshot_date`` is stored ISO ``YYYY-MM-DD``, so a
    lexicographic ``>`` is a correct date comparison.
    """
    cutoff = today.isoformat()
    total = corpus.snapshot_count(conn)
    problems = [
        f"snapshot {r['case_id']} dated {r['snapshot_date']} is after {cutoff}"
        for r in conn.execute(
            "SELECT case_id, snapshot_date FROM snapshots WHERE snapshot_date > ? "
            "ORDER BY case_id, snapshot_date LIMIT ?",
            (cutoff, _MAX_PROBLEMS),
        )
    ]
    return _check(CHECK_SNAPSHOT_NOT_FUTURE, problems, checked=total, detail=f"as of {cutoff}")


def check_no_duplicates(conn: sqlite3.Connection) -> CorpusCheck:
    """No case id and no ``(case_id, event_id)`` may appear more than once.

    The primary keys enforce this today; the check is a cheap defensive assertion
    that catches a regression if the corpus is ever rebuilt from a source without
    those constraints.
    """
    checked = corpus.count(conn) + corpus.event_count(conn)
    problems: list[str] = []
    for record in conn.execute(
        "SELECT case_id, COUNT(*) AS n FROM cases GROUP BY case_id HAVING n > 1 "
        "ORDER BY case_id LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(f"case {record['case_id']!r} appears {record['n']} times")
    for record in conn.execute(
        "SELECT case_id, event_id, COUNT(*) AS n FROM events GROUP BY case_id, event_id "
        "HAVING n > 1 ORDER BY case_id, event_id LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(
            f"event ({record['case_id']!r}, {record['event_id']!r}) appears {record['n']} times"
        )
    return _check(CHECK_NO_DUPLICATES, problems, checked=checked)


def check_seed_cursor(conn: sqlite3.Connection, cursor: SeedProgress | None) -> CorpusCheck:
    """The seed cursor must reconcile against the corpus' per-court row counts.

    The cursor records how many bulk rows were loaded per court; the relationship
    to corpus cases is loose (dedup shrinks it, forward discovery grows it), so the
    conservative invariant is one-directional: a court the cursor says it loaded
    rows for (``offset > 0``) must have at least one case in the corpus. A court
    booked as loaded yet absent from the corpus is a genuine desync (data loss or a
    cursor written against a different store); a count mismatch alone is not.
    """
    if cursor is None:
        return _check(CHECK_SEED_CURSOR, [], checked=0, detail="no seed cursor supplied")
    loaded = {court: prog for court, prog in cursor.courts.items() if prog.offset > 0}
    problems = [
        f"cursor loaded {loaded[court].offset} row(s) for {court} but the corpus has none"
        for court in sorted(loaded)
        if conn.execute("SELECT 1 FROM cases WHERE court = ? LIMIT 1", (court,)).fetchone() is None
    ]
    return _check(CHECK_SEED_CURSOR, problems, checked=len(loaded))


# --- referential integrity (layer C, git ledger vs corpus) ---------------------


def _ledger_files(data_root: Path, pattern: str) -> list[Path]:
    """Ledger artifacts matching ``pattern`` under ``data/cases``, in path order."""
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    return sorted(cases_dir.glob(pattern))


def _load_ids(path: Path) -> tuple[str, str] | None:
    """``(case_id, event_id)`` from a ledger JSON file, or ``None`` if unreadable.

    A malformed file is `validate`'s concern (schema law), not this command's, so a
    file that cannot be parsed is skipped rather than counted as an orphan.
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    case_id, event_id = data.get("case_id"), data.get("event_id")
    if isinstance(case_id, str) and isinstance(event_id, str):
        return case_id, event_id
    return None


def _corpus_case_ids(conn: sqlite3.Connection) -> set[str]:
    return {r["case_id"] for r in conn.execute("SELECT case_id FROM cases")}


def _corpus_event_keys(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    return {
        (r["case_id"], r["event_id"]) for r in conn.execute("SELECT case_id, event_id FROM events")
    }


def _iter_ledger_artifacts(data_root: Path) -> Iterator[tuple[str, Path]]:
    """Yield ``(kind, path)`` for every outcome/prediction/evaluation under ``data/``."""
    for kind, pattern in (
        ("outcome", "*/*/events/*/outcome.json"),
        ("prediction", "*/*/events/*/predictions/*/*/prediction.json"),
        ("evaluation", "*/*/events/*/evaluations/*/*/*/evaluation.json"),
    ):
        for path in _ledger_files(data_root, pattern):
            yield kind, path


def check_ledger_references(conn: sqlite3.Connection, data_root: Path) -> CorpusCheck:
    """Every ledger judgment must reference a case + event that exist in the corpus.

    An ``outcome``/``prediction``/``evaluation`` whose ``(case_id, event_id)`` has
    no matching corpus row is an orphan: a judgment about a case or event the
    raw-fact store does not know, which the leaderboard and back-test would then
    aggregate against nothing.
    """
    case_ids = _corpus_case_ids(conn)
    event_keys = _corpus_event_keys(conn)
    problems: list[str] = []
    checked = 0
    for kind, path in _iter_ledger_artifacts(data_root):
        ids = _load_ids(path)
        if ids is None:
            continue
        checked += 1
        case_id, event_id = ids
        if case_id not in case_ids:
            problems.append(f"{kind} {path}: case {case_id!r} is not in the corpus")
        elif (case_id, event_id) not in event_keys:
            problems.append(
                f"{kind} {path}: event ({case_id!r}, {event_id!r}) is not in the corpus"
            )
    return _check(CHECK_LEDGER_REFERENCES, problems, checked=checked)


def check_evaluation_targets(data_root: Path) -> CorpusCheck:
    """Every evaluation must score a predictor that produced a prediction for the event.

    An evaluation lives at ``evaluations/<evaluator>/<predictor>/<run>/`` and names
    its ``predictor_id``; the prediction(s) it scores live at
    ``predictions/<predictor>/<run>/prediction.json`` under the same event. An
    evaluation with no matching prediction is an orphan scoring nothing.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/evaluations/*/*/*/evaluation.json"):
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        predictor_id = data.get("predictor_id")
        if not isinstance(predictor_id, str):
            continue
        checked += 1
        # event_dir/evaluations/<evaluator>/<predictor>/<run>/evaluation.json
        event_dir = path.parents[4]
        predictions = event_dir / "predictions" / predictor_id
        if not any(predictions.glob("*/prediction.json")):
            problems.append(
                f"evaluation {path}: predictor {predictor_id!r} has no prediction for this event"
            )
    return _check(CHECK_EVALUATION_TARGETS, problems, checked=checked)


# --- orchestration -------------------------------------------------------------


def _run_checks(
    conn: sqlite3.Connection,
    *,
    data_root: Path,
    seed_cursor: SeedProgress | None,
    today: date,
    baseline_count: int | None,
) -> CorpusValidation:
    """Run every check against an open corpus and roll the results into a verdict."""
    checks = [
        _check(CHECK_CORPUS_OPENS, [], checked=1, detail="corpus opened"),
        check_row_count_monotonic(conn, baseline_count),
        check_required_columns(conn),
        check_snapshot_not_future(conn, today),
        check_no_duplicates(conn),
        check_ledger_references(conn, data_root),
        check_evaluation_targets(data_root),
        check_seed_cursor(conn, seed_cursor),
    ]
    return CorpusValidation(
        ok=all(c.passed for c in checks),
        skipped=False,
        corpus_rows=corpus.count(conn),
        corpus_events=corpus.event_count(conn),
        checks=checks,
    )


def run_corpus_validation(
    *,
    corpus_db_path: Path,
    data_root: Path,
    seed_cursor: SeedProgress | None,
    today: date,
    baseline_count: int | None = None,
) -> CorpusValidation:
    """Validate the corpus + ledger and return the verdict (the CLI is a thin wrapper).

    Graceful when the corpus is absent — returns a skipped verdict (``ok`` true, no
    checks), so the command is safe to call before a ``dvc pull``. If the file
    exists but does not open as a database, that is itself a failed integrity check
    rather than a crash.
    """
    if not corpus_db_path.exists():
        return CorpusValidation(ok=True, skipped=True)
    try:
        with corpus.connect(corpus_db_path) as conn:
            return _run_checks(
                conn,
                data_root=data_root,
                seed_cursor=seed_cursor,
                today=today,
                baseline_count=baseline_count,
            )
    except sqlite3.Error as exc:
        opens = _check(
            CHECK_CORPUS_OPENS,
            [f"{corpus_db_path.name}: corpus did not open ({exc})"],
            checked=1,
        )
        return CorpusValidation(ok=False, skipped=False, checks=[opens])
