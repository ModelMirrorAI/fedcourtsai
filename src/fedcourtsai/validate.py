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
  snapshot is future-dated and every case's filing/decision dates are ordered and
  not future-dated; coded columns hold values from their declared vocabulary
  (``Disposition``, ``EventKind``, the tracked-court set); and no case, event,
  snapshot, or whitespace-variant id is duplicated.
* **referential integrity** — the cross-store checks nothing else does: every
  ``outcome``/``prediction``/``evaluation`` under ``data/`` references a case and
  event that exist in the corpus (no orphan judgments); every evaluation targets a
  predictor that actually produced a prediction for that event; and the seed
  cursor reconciles against the corpus' per-court row counts.

The verdict is a pure function of its inputs (corpus, ledger, cursor, baseline,
tracked courts, as-of date), with no clock or network, so it is deterministic and
offline. Each check is a small function returning one :class:`CorpusCheck`. The
git-only referential subset (:func:`run_ledger_referential_checks`) needs no corpus
at all, so the PR gate runs it over ``data/`` to catch an orphan judgment in review;
the corpus-dependent checks stay scheduled, where the remote is present.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from . import corpus
from .schemas import (
    FILENAME_MODELS,
    CorpusCheck,
    CorpusScopeAudit,
    CorpusValidation,
    Disposition,
    EventKind,
    LedgerValidation,
    ScopeDocketShape,
    ScopeExclusion,
    ScopeUnclassified,
    SeedProgress,
)

# Bounded sample of matched case ids per exclusion, so the scope audit stays small.
_MAX_SAMPLE = 10

# Cap the per-check problem sample so a pathological corpus cannot produce an
# unbounded verdict; `CorpusCheck.failures` still carries the true total.
_MAX_PROBLEMS = 20

# Accepted floor for `case_dates_ordered`: a stable handful of CourtListener rows
# carry `date_decided < date_filed` (faithful upstream data, not rewritten — see the
# monitor issue #171). The observed steady-state is ~20; this floor leaves headroom
# so noise passes while a material climb fails. Raise it deliberately if the steady
# count grows (e.g. after a large historical backfill), never to silence a regression.
_CASE_DATE_ORDER_BASELINE = 50

# Stable check identifiers (the `name` field of each emitted CorpusCheck).
CHECK_CORPUS_OPENS = "corpus_opens"
CHECK_ROW_COUNT_MONOTONIC = "row_count_monotonic"
CHECK_REQUIRED_COLUMNS = "required_columns_non_empty"
CHECK_SNAPSHOT_NOT_FUTURE = "snapshot_not_future_dated"
CHECK_CASE_DATES = "case_dates_ordered"
CHECK_DOMAIN_VALUES = "domain_values_valid"
CHECK_NO_DUPLICATES = "no_duplicate_cases_or_events"
CHECK_LEDGER_REFERENCES = "ledger_references_exist"
CHECK_LEDGER_EVENTS_IN_GIT = "ledger_events_exist_in_git"
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


def check_case_dates(conn: sqlite3.Connection, today: date) -> CorpusCheck:
    """A case's filing/decision dates must be ordered and not future-dated.

    The point-in-time counterpart to the snapshot check, over the normalized
    ``cases`` row, covering two distinct conditions. Dates are stored ISO
    ``YYYY-MM-DD``, so a lexicographic comparison is a correct date comparison; a
    null date (unfiled or undecided) is simply skipped.

    - **Future-dated** (``date_filed`` or ``date_decided`` after the as-of date) is
      a clock or ingestion bug and **always fails** — there is no benign cause.
    - **Decided-before-filed** (``date_filed > date_decided``) is, for a stable
      floor of rows, a faithful copy of upstream CourtListener data we deliberately
      do not rewrite (the monitor issue #171). It fails only when the count climbs
      **above** that accepted baseline — the "material climb → investigate" signal —
      so the steady-state condition does not hold the data-health verdict
      permanently red.

    ``failures`` always carries the true total of both conditions, so the monitor
    still sees the count even when the ordering condition is within baseline.
    """
    cutoff = today.isoformat()
    checked = corpus.count(conn)
    future_where = (
        "(date_filed IS NOT NULL AND date_filed > ?) "
        "OR (date_decided IS NOT NULL AND date_decided > ?)"
    )
    order_where = (
        "date_filed IS NOT NULL AND date_decided IS NOT NULL AND date_filed > date_decided"
    )
    future = int(
        conn.execute(
            f"SELECT COUNT(*) AS n FROM cases WHERE {future_where}", (cutoff, cutoff)
        ).fetchone()["n"]
    )
    out_of_order = int(
        conn.execute(f"SELECT COUNT(*) AS n FROM cases WHERE {order_where}").fetchone()["n"]
    )
    problems = [
        f"case {r['case_id']!r} is future-dated "
        f"(filed {r['date_filed']}, decided {r['date_decided']}, as of {cutoff})"
        for r in conn.execute(
            f"SELECT case_id, date_filed, date_decided FROM cases WHERE {future_where} "
            "ORDER BY case_id LIMIT ?",
            (cutoff, cutoff, _MAX_PROBLEMS),
        )
    ] + [
        f"case {r['case_id']!r} is decided before filed "
        f"(filed {r['date_filed']}, decided {r['date_decided']})"
        for r in conn.execute(
            f"SELECT case_id, date_filed, date_decided FROM cases WHERE {order_where} "
            "ORDER BY case_id LIMIT ?",
            (_MAX_PROBLEMS,),
        )
    ]
    return CorpusCheck(
        name=CHECK_CASE_DATES,
        passed=future == 0 and out_of_order <= _CASE_DATE_ORDER_BASELINE,
        checked=checked,
        failures=future + out_of_order,
        detail=f"{future} future-dated, {out_of_order} decided-before-filed vs accepted "
        f"baseline {_CASE_DATE_ORDER_BASELINE} (as of {cutoff}); see #171",
        problems=sorted(problems)[:_MAX_PROBLEMS],
    )


def check_domain_values(conn: sqlite3.Connection, tracked_courts: list[str] | None) -> CorpusCheck:
    """Coded columns must hold values from their declared vocabulary.

    A case ``disposition`` (when set) must be a :class:`~fedcourtsai.schemas.Disposition`,
    an event ``kind`` an :class:`~fedcourtsai.schemas.EventKind`, and every case and
    event ``court`` one of the tracked courts. The pydantic enums enforce this at
    write time, so a violation means a corpus rebuilt from a source that bypassed
    them — defensive, like the duplicate check. The tracked-court half is skipped
    when no court set is supplied, keeping the verdict a pure function of its inputs.
    """
    checked = corpus.count(conn) + corpus.event_count(conn)
    problems: list[str] = []
    dispositions = sorted(d.value for d in Disposition)
    disp_ph = ", ".join("?" for _ in dispositions)
    for r in conn.execute(
        f"SELECT case_id, disposition FROM cases WHERE disposition IS NOT NULL "
        f"AND disposition NOT IN ({disp_ph}) ORDER BY case_id LIMIT ?",
        (*dispositions, _MAX_PROBLEMS),
    ):
        problems.append(f"case {r['case_id']!r} has unknown disposition {r['disposition']!r}")
    kinds = sorted(k.value for k in EventKind)
    kind_ph = ", ".join("?" for _ in kinds)
    for r in conn.execute(
        f"SELECT case_id, event_id, kind FROM events WHERE kind NOT IN ({kind_ph}) "
        f"ORDER BY case_id, event_id LIMIT ?",
        (*kinds, _MAX_PROBLEMS),
    ):
        problems.append(
            f"event ({r['case_id']!r}, {r['event_id']!r}) has unknown kind {r['kind']!r}"
        )
    if tracked_courts:
        courts = sorted(set(tracked_courts))
        court_ph = ", ".join("?" for _ in courts)
        for r in conn.execute(
            f"SELECT case_id, court FROM cases WHERE court NOT IN ({court_ph}) "
            f"ORDER BY case_id LIMIT ?",
            (*courts, _MAX_PROBLEMS),
        ):
            problems.append(f"case {r['case_id']!r} is in untracked court {r['court']!r}")
        for r in conn.execute(
            f"SELECT case_id, event_id, court FROM events WHERE court NOT IN ({court_ph}) "
            f"ORDER BY case_id, event_id LIMIT ?",
            (*courts, _MAX_PROBLEMS),
        ):
            problems.append(
                f"event ({r['case_id']!r}, {r['event_id']!r}) is in untracked court {r['court']!r}"
            )
    return _check(CHECK_DOMAIN_VALUES, problems, checked=checked)


def check_no_duplicates(conn: sqlite3.Connection) -> CorpusCheck:
    """No identifier may appear more than once across the keyed stores.

    The primary keys enforce uniqueness today; this is a cheap defensive assertion
    that catches a regression if the corpus is ever rebuilt from a source without
    those constraints. It checks three keys — case id, ``(case_id, event_id)``, and
    snapshot ``(case_id, snapshot_date)`` — and also flags ids that differ only by
    surrounding whitespace: those are distinct primary keys yet one logical id, so
    they collide on every referential join.
    """
    checked = corpus.count(conn) + corpus.event_count(conn) + corpus.snapshot_count(conn)
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
    for record in conn.execute(
        "SELECT case_id, snapshot_date, COUNT(*) AS n FROM snapshots "
        "GROUP BY case_id, snapshot_date HAVING n > 1 ORDER BY case_id, snapshot_date LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(
            f"snapshot ({record['case_id']!r}, {record['snapshot_date']!r}) "
            f"appears {record['n']} times"
        )
    for record in conn.execute(
        "SELECT trim(case_id) AS k, COUNT(DISTINCT case_id) AS n FROM cases "
        "GROUP BY trim(case_id) HAVING n > 1 ORDER BY k LIMIT ?",
        (_MAX_PROBLEMS,),
    ):
        problems.append(f"case id {record['k']!r} has {record['n']} whitespace-variant spellings")
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


# --- referential integrity (git-only subset, for the PR gate) ------------------


def _event_ref_from_path(path: Path, data_root: Path) -> tuple[str, str, Path] | None:
    """``(case_id, event_id, event_dir)`` inferred from a ledger artifact's path.

    The on-disk layout encodes the case and event an artifact belongs to:
    ``cases/<court>/<docket>/events/<event_id>/...``. Returns ``None`` for a path
    that does not sit under that layout (so it is simply skipped, not flagged).
    """
    try:
        parts = path.relative_to(data_root / "cases").parts
    except ValueError:
        return None
    if len(parts) < 5 or parts[2] != "events":
        return None
    court, docket, _events, event_id = parts[0], parts[1], parts[2], parts[3]
    event_dir = data_root / "cases" / court / docket / "events" / event_id
    return f"{court}/{docket}", event_id, event_dir


def check_ledger_events_in_git(data_root: Path) -> CorpusCheck:
    """Every ledger judgment must reference an event that exists in the git tree.

    The corpus-free counterpart to :func:`check_ledger_references`, for the PR gate
    where there is no corpus remote: the git event tree (an ``event.yaml`` under
    ``events/<event_id>/``) is the available source of event existence. An
    ``outcome``/``prediction``/``evaluation`` sitting under an event directory with
    no ``event.yaml``, or whose declared ``(case_id, event_id)`` disagrees with the
    path it lives at, is an orphan — caught here in review rather than a day later on
    the schedule, where the stronger corpus check also runs.
    """
    problems: list[str] = []
    checked = 0
    for kind, path in _iter_ledger_artifacts(data_root):
        ref = _event_ref_from_path(path, data_root)
        if ref is None:
            continue
        checked += 1
        case_id, event_id, event_dir = ref
        declared = _load_ids(path)
        if declared is not None and declared != (case_id, event_id):
            problems.append(
                f"{kind} {path}: declares {declared} but its path is ({case_id!r}, {event_id!r})"
            )
        elif not (event_dir / "event.yaml").is_file():
            problems.append(
                f"{kind} {path}: event ({case_id!r}, {event_id!r}) has no event.yaml in the ledger"
            )
    return _check(CHECK_LEDGER_EVENTS_IN_GIT, problems, checked=checked)


def run_ledger_referential_checks(data_root: Path) -> list[CorpusCheck]:
    """The git-only referential checks the PR gate runs (no corpus, no network).

    The subset of layer-C checks that need only the git ledger under ``data/``:
    every judgment references an event defined in git, and every evaluation targets
    a prediction that exists. The corpus-dependent referential checks (which need
    the DVC blob) stay on the schedule — the gate is deliberately offline.
    """
    return [check_ledger_events_in_git(data_root), check_evaluation_targets(data_root)]


# --- orchestration -------------------------------------------------------------


def _run_checks(
    conn: sqlite3.Connection,
    *,
    data_root: Path,
    seed_cursor: SeedProgress | None,
    today: date,
    baseline_count: int | None,
    tracked_courts: list[str] | None,
) -> CorpusValidation:
    """Run every check against an open corpus and roll the results into a verdict."""
    checks = [
        _check(CHECK_CORPUS_OPENS, [], checked=1, detail="corpus opened"),
        check_row_count_monotonic(conn, baseline_count),
        check_required_columns(conn),
        check_snapshot_not_future(conn, today),
        check_case_dates(conn, today),
        check_domain_values(conn, tracked_courts),
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
    tracked_courts: list[str] | None = None,
) -> CorpusValidation:
    """Validate the corpus + ledger and return the verdict (the CLI is a thin wrapper).

    Graceful when the corpus is absent — returns a skipped verdict (``ok`` true, no
    checks), so the command is safe to call before a ``dvc pull``. If the file
    exists but does not open as a database, that is itself a failed integrity check
    rather than a crash. ``tracked_courts`` scopes the domain check; absent it, the
    court-membership half is skipped.
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
                tracked_courts=tracked_courts,
            )
    except sqlite3.Error as exc:
        opens = _check(
            CHECK_CORPUS_OPENS,
            [f"{corpus_db_path.name}: corpus did not open ({exc})"],
            checked=1,
        )
        return CorpusValidation(ok=False, skipped=False, checks=[opens])


def _recoverable_signal(row: corpus.CorpusRow) -> bool:
    """Whether a case carries a hint its disposition is recoverable (ingestion gap).

    An opinion, a citation, a citation count, or a decision date means the corpus
    already knows the case was decided — so a still-open event on it is likely a
    missed disposition (re-ingestible) rather than a genuinely absent one.
    """
    return bool(
        row.opinion_text or row.citations or row.citation_count or row.date_decided is not None
    )


@dataclass
class _ReasonAgg:
    """Mutable tally for one exclusion reason while scanning open events."""

    cases: set[str] = field(default_factory=set)
    open_events: int = 0
    recoverable: int = 0
    sample: list[str] = field(default_factory=list)


@dataclass
class _Bucket:
    """Mutable tally for one unclassified (in-scope) bucket."""

    open_events: int = 0
    sample: list[str] = field(default_factory=list)


# The bucket whose docket-number shapes we histogram, so a refinement (#343) can see
# exactly which formats the Term parser would need to handle. Kept as a constant so the
# tally below and the bucket label never drift apart. Accepted-fragment threshold: a
# shape carrying fewer than ~100 open events is an accepted fragment — it stays
# visible in this bucket and the shape histogram by design, and no exclusion
# predicate is chased for it (the residual tail is cheaper to see than to classify).
_UNPARSEABLE_REASON = "docket Term not parseable (a format the predicate skips)"

# Top docket-number shapes to report — enough to see the long tail, still bounded.
_MAX_SHAPES = 15


def _unclassified_reason(row: corpus.CorpusRow) -> str:
    """Why an open SCOTUS event no predicate excluded stays in scope (#343 bucketing)."""
    if row.disposition is not None or row.date_decided is not None:
        return "carries a disposition signal (open despite a recorded decision)"
    if corpus.scotus_term_year(row.docket_number) is not None:
        return "recent or current Term (legitimately pending)"
    if row.docket_number.strip():
        return _UNPARSEABLE_REASON
    return "no docket number"


def _docket_shape(docket_number: str) -> str:
    """Mask a docket number to its shape: digit→``9``, letter→``A``/``a``, else kept.

    ``"01-7700"`` -> ``"99-9999"``, ``"22O141"`` -> ``"99A999"`` — so distinct numbers
    of the same format collapse to one shape we can count. ``A`` masks *every*
    uppercase letter, not the literal letter A: ``"D-1234"`` also renders as
    ``"A-9999"``, so read a shape as a format class, never as a specific docket letter.
    """
    out = []
    for ch in docket_number.strip():
        if ch.isdigit():
            out.append("9")
        elif ch.isalpha():
            out.append("A" if ch.isupper() else "a")
        else:
            out.append(ch)
    return "".join(out)


def run_scope_audit(*, corpus_db_path: Path) -> CorpusScopeAudit:
    """Census the corpus's open events that the predict scope excludes (issue #343).

    For every still-open SCOTUS event, classify its case by the shared exclusion
    predicates (`corpus.out_of_scope_reason`): the matched ones are tallied per reason
    (cases / open events / recoverable subset), and the rest are bucketed by *why* the
    scope still keeps them — the refinement signal for broadening the predicate.
    Read-only and a pure function of the corpus; graceful (skipped) when the corpus is
    absent, like :func:`run_corpus_validation`.
    """
    if not corpus_db_path.exists():
        return CorpusScopeAudit(skipped=True)
    by_reason: dict[str, _ReasonAgg] = {}
    by_bucket: dict[str, _Bucket] = {}
    shapes: Counter[str] = Counter()
    seen_rows: dict[str, corpus.CorpusRow | None] = {}
    open_events = 0
    with corpus.connect(corpus_db_path) as conn:
        corpus_rows = corpus.count(conn)
        for event in corpus.iter_open_events(conn, court="scotus"):
            open_events += 1
            row = seen_rows.setdefault(event.case_id, corpus.get_row(conn, event.case_id))
            if row is None:
                continue
            reason = corpus.out_of_scope_reason_full(conn, row)
            if reason is None:
                bucket_reason = _unclassified_reason(row)
                bucket = by_bucket.setdefault(bucket_reason, _Bucket())
                bucket.open_events += 1
                if event.case_id not in bucket.sample and len(bucket.sample) < _MAX_SAMPLE:
                    bucket.sample.append(event.case_id)
                if bucket_reason == _UNPARSEABLE_REASON:
                    shapes[_docket_shape(row.docket_number)] += 1
                continue
            agg = by_reason.setdefault(reason, _ReasonAgg())
            agg.cases.add(event.case_id)
            agg.open_events += 1
            # The bare opinion-import class is recoverable by construction: its
            # exclusion signal *is* a linked published opinion cluster, the same
            # ingestion-gap hint the row-level signal looks for.
            if _recoverable_signal(row) or reason == corpus.BARE_OPINION_IMPORT_REASON:
                agg.recoverable += 1
            if event.case_id not in agg.sample and len(agg.sample) < _MAX_SAMPLE:
                agg.sample.append(event.case_id)
    exclusions = [
        ScopeExclusion(
            reason=reason,
            cases=len(agg.cases),
            open_events=agg.open_events,
            recoverable=agg.recoverable,
            sample_cases=sorted(agg.sample),
        )
        for reason, agg in sorted(by_reason.items())
    ]
    unclassified = [
        ScopeUnclassified(reason=reason, open_events=b.open_events, sample_cases=sorted(b.sample))
        for reason, b in sorted(by_bucket.items(), key=lambda kv: -kv[1].open_events)
    ]
    docket_shapes = [
        ScopeDocketShape(shape=shape, count=count)
        for shape, count in shapes.most_common(_MAX_SHAPES)
    ]
    return CorpusScopeAudit(
        skipped=False,
        unclassified=unclassified,
        unparseable_docket_shapes=docket_shapes,
        corpus_rows=corpus_rows,
        scotus_open_events=open_events,
        exclusions=exclusions,
    )
