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
  event that exist in the corpus (no orphan judgments); every evaluation
  targets a predictor that actually produced a prediction for that event; every
  evaluation recording a ``risk_set`` base-rate basis carries the salience
  version that population was banded under; every
  prose document a ``prediction.json`` names resolves to a file beside it; every
  committed claims block is one the claim scorer will not silently void; every
  committed semantic block — the predictor's propositions and the grader's
  grades alike — answers the declaration its event carries, since both sides are
  read past silently rather than refused loudly; and
  every merits-stage event's scored (latest-per-predictor) prediction carries
  its ``judgment`` — the stage-aware half of the merits prediction contract;
  no evaluation carries a ``vote_accuracy`` off a merits event, since an
  individual cert vote is never scored and that field is the evaluator's own to
  write; one cell's current gradings record the same ``correct`` bit, that bit
  being a function of two committed artifacts rather than a judgment; and no
  outcome carries a ``judgment`` off a merits event, that field's presence being
  what routes the accuracy comparison onto the merits axis.

The verdict is a pure function of its inputs (corpus, ledger, baseline,
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
from datetime import date, timedelta
from pathlib import Path

import yaml
from pydantic import ValidationError

from . import corpus, ids
from .integrity import cell_clock, latest_evaluation_runs
from .paths import CasePaths
from .pipeline import moments
from .pipeline.claims import claim_block_problems
from .pipeline.interim_signals import ApplicationKind
from .pipeline.semantic import semantic_claim_problems, semantic_grade_problems
from .schemas import (
    FILENAME_MODELS,
    MERITS_PROCEEDING_DISPOSITIONS,
    CorpusCheck,
    CorpusScopeAudit,
    CorpusValidation,
    Disposition,
    Evaluation,
    EventKind,
    LedgerValidation,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ScopeDocketShape,
    ScopeExclusion,
    ScopeUnclassified,
    Stage,
)

# Bounded sample of matched case ids per exclusion, so the scope audit stays small.
_MAX_SAMPLE = 10

# Cap the per-check problem sample so a pathological corpus cannot produce an
# unbounded verdict; `CorpusCheck.failures` still carries the true total.
_MAX_PROBLEMS = 20

# Accepted floor for `case_dates_ordered`: a stable handful of CourtListener rows
# carry `date_decided < date_filed` (faithful upstream data, not rewritten — the
# check below monitors the count). The observed steady-state is ~20; this floor leaves headroom
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
# The corpus→ledger direction of the same referential rule
# `CHECK_LEDGER_REFERENCES` runs the other way: a minted forecast moment owes
# both halves at its mint, so its corpus row must carry the committed
# `event.yaml` that defines it. Stage baselines are outside the rule — their
# ledger half is written at first touch or at resolution, not at discovery.
CHECK_CORPUS_EVENTS_IN_LEDGER = "minted_moments_defined_in_ledger"
CHECK_EVALUATION_TARGETS = "evaluation_targets_prediction"
# The id is the durable name of the whole basis-pairing rule (both the
# risk-set and the terminal half), kept stable across reports even though it
# reads as the risk-set half alone.
CHECK_BASE_RATE_VERSION = "base_rate_basis_carries_version"
CHECK_PREDICTION_DOCS = "prediction_docs_exist"
CHECK_PREDICTION_CLAIMS = "prediction_claims_scoreable"
CHECK_PREDICTION_SEMANTIC = "prediction_semantic_claims_conform"
CHECK_EVALUATION_SEMANTIC = "evaluation_semantic_grades_gradeable"
CHECK_MERITS_PREDICTIONS = "merits_predictions_carry_judgment"
CHECK_SCORED_VOTES = "vote_accuracy_only_on_merits_events"
# `correct` is a function of two committed artifacts, so one cell's current
# gradings must record the same bit whichever evaluator wrote them.
CHECK_CORRECT_AGREES = "evaluation_correct_agrees"
# Only a merits outcome has a judgment to record, and the field routes `correct`.
CHECK_JUDGMENT_ONLY_MERITS = "judgment_only_on_merits_outcomes"
CHECK_STALE_UNPARSED_GRANTS = "no_stale_unparsed_grants"
# Advisory, not a failure: ingest strips the marking at the write site, but rows
# written before it still carry one until they are re-ingested, and the verdict
# must not be red for the whole interval. Named for the capital marking
# specifically, which is exactly what it counts — a `*** … *** ` string the
# strip leaves alone (a consolidated circuit docket) is not a defect.
CHECK_DOCKET_NUMBER_MARKING = "docket_numbers_carry_no_capital_marking"

#: Ceiling on the advisory count above which it stops being advisory and fails.
#: The strip runs at every ingest write site, so this population can only ever
#: shrink; a count above the ceiling means a write path is landing the marking
#: again, which is a code defect and belongs in the failing set. Set with
#: headroom over the observed backlog so ordinary drainage never trips it.
#: Raise it only after establishing why the population grew — never to silence
#: a regression.
_DOCKET_MARKING_CEILING = 600

# The staleness bound lives in `corpus` (`STALE_GRANT_DAYS`, with the
# rationale beside it): one bound, two consumers — this check reports the
# class, and the merits forecastability arm refuses it, so what turns red
# here can never also be spending forecast cells.
_STALE_GRANT_DAYS = corpus.STALE_GRANT_DAYS

#: Real grants that the Court never disposed of by **order**, so the
#: `merits_judgment` half of this check's clear is not recoverable from docket
#: text by any re-snapshot, re-parse, or vocabulary widening. Naming them here
#: retires a row whose defect will not change, rather than letting the check
#: carry it indefinitely.
#:
#: The consolidated Title X trio — Nos. 20-429, 20-454 and 20-539, granted
#: together on 2021-02-22 in one VIDED order and consolidated for a single
#: hour of argument. The parties filed a joint stipulation to dismiss under
#: Rule 46.1 on 2021-03-12, and no dismissal order followed on any of the three
#: dockets — not on the docket a stipulation names, and not on its companions;
#: each docket's proceedings simply stop. There is nothing for a judgment parse
#: to read.
#:
#: **The exception is the cheaper of two live options, not the only one.** The
#: stipulation itself is dated docket text, so a curated ``merits_terminated``
#: would clear these rows permanently and is the more informative record;
#: :func:`fedcourtsai.pipeline.outcome.termination_signal` does not reach it
#: only because that reader is scoped to the docket's latest entry, which here
#: is a later letter brief. Prefer the curated termination whenever a writer-lane
#: pass is being composed anyway; this list is what keeps the verdict honest in
#: the meantime, and a member should be *removed* from it the moment its
#: termination is written.
#:
#: A member is **excepted, never dropped**: it stays in `checked`, and the
#: check's `detail` names every excepted row the run found, so the exemption is
#: as visible on the durable verdict as a failure would be. Adding one is a
#: maintainer's judgment recorded in code, and each entry earns a comment naming
#: why no order ever disposed of it.
#:
#: The list is **this check's alone, deliberately**. Its sibling consumer of the
#: same population and bound, :func:`fedcourtsai.corpus.is_stale_unparsed_grant`,
#: keeps refusing these rows at the merits queue seam, and should: excepting a
#: row says only that its record needs no mending, never that the docket is
#: still pending — it was decided years ago, so a forward cell on it would be a
#: mislabeled backtest exactly as before. One bound, two consumers, and only the
#: reporting half has anything to forgive.
_OFF_DOCKET_TERMINAL_CASES: frozenset[str] = frozenset(
    {
        ids.case_id("scotus", 72466202),  # 20-429, American Medical Association
        ids.case_id("scotus", 72466229),  # 20-454, Becerra
        ids.case_id("scotus", 72466705),  # 20-539, Oregon
    }
)


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


def _advisory(name: str, problems: list[str], *, checked: int, detail: str = "") -> CorpusCheck:
    """Assemble a check that **reports** its findings without failing the verdict.

    The same shape as :func:`_check` — the count in ``failures``, a bounded
    sample in ``problems`` — but ``passed`` stays true, so the finding rides on
    the durable verdict and in the command's warning lines while ``ok`` keeps
    meaning "nothing here blocks a merge".

    Reserved for a defect whose *remedy is a data pass, not a code fix*: failing
    would leave the verdict red for however long the backfill takes, which trains
    a reader to ignore a red verdict — the one cost a validator cannot afford.
    Anything a contributor can fix in their own PR is a :func:`_check`.
    """
    return CorpusCheck(
        name=name,
        passed=True,
        checked=checked,
        failures=len(problems),
        detail=detail,
        problems=sorted(problems)[:_MAX_PROBLEMS],
    )


# --- schema conformance (layer A, git ledger only) -----------------------------


def _in_provisioning_tree(file: Path, root: Path) -> bool:
    """Whether ``file`` sits under a case's gitignored ``record/`` provisioning tree.

    ``record/`` holds what a cell was *handed*, not what it produced: the corpus
    snapshot, the fetched document text, the cell context, and the evaluate
    cell's blinded candidate staging (:mod:`fedcourtsai.blinding`). None of it is
    committed, so none of it is ledger. The distinction is load-bearing rather
    than tidy-minded: a blinded candidate is a deliberately *masked* view of a
    prediction — no engine, no model, no process version — so it is not a
    ``Prediction`` and checking it against that schema would report a mask as a
    defect. Nothing under ``record/`` carries a ledger filename today apart from
    that staging, so this narrows the scan by exactly the tree it names.

    Matched **positionally** against the case layout rather than by looking for a
    ``record`` component anywhere in the path. An unanchored test would also fire
    on a data root that happens to sit under a directory called ``record``, and
    the failure would be a validation pass that checked nothing — the one shape a
    gate must never have.
    """
    try:
        parts = file.relative_to(root).parts
    except ValueError:  # pragma: no cover - rglob yields paths under root
        return False
    return len(parts) > 4 and parts[0] == "cases" and parts[3] == "record"


def validate_ledger(path: Path) -> LedgerValidation:
    """Validate every known artifact under ``path`` against its schema model.

    The corpus-free, git-only half of data health: the same per-file schema check
    the ``validate`` command (and the PR gate) runs, returned as a structured
    :class:`LedgerValidation` so the ops dashboard can present it alongside the
    corpus verdict. ``problems`` is capped like the corpus checks; ``invalid`` is
    the true failure count.

    Scoped to the committed ledger: the gitignored ``record/`` provisioning trees
    are skipped (:func:`_in_provisioning_tree`).
    """
    problems: list[str] = []
    checked = 0
    for file in sorted(path.rglob("*")):
        model = FILENAME_MODELS.get(file.name)
        if model is None or not file.is_file() or _in_provisioning_tree(file, path):
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


def check_docket_number_marking(conn: sqlite3.Connection) -> CorpusCheck:
    """No stored ``docket_number`` should carry the ``*** CAPITAL CASE ***`` marking.

    Upstream appends the marking to some case numbers. It is a flag on the case,
    never part of its number, and it is latched separately as ``capital_case``,
    so a stored number carrying it is a **spelling defect**: the column is not
    the number the Court assigned.

    Deliberately not "the base rates are missing these rows" — every reader that
    parses a docket number strips the marking first, so the cuts and the live
    channel's addressing all see these dockets. What the stored annotation
    actually costs is narrower and still worth counting: it breaks
    :func:`~fedcourtsai.corpus.normalize_docket_number`'s identity join for any
    consumer that does not normalize, it is wrong wherever the column is
    displayed, and it is a trap for the next parse site that forgets to strip.

    Scoped to what the ingest strip would change, which is the same rule on both
    sides: a ``*** … ***`` string the strip leaves alone — a consolidated circuit
    docket using the asterisks as separators — is not a defect and is not counted.

    **Advisory below the ceiling, a failure above it.** Ingest strips the
    marking at the write site, so no new row can acquire one, but a row written
    before that strip reached the store still carries it until it is
    re-ingested — the corpus is the only place the fix can land, and no
    contributor's PR can make this green. Failing on the backlog would hold the
    verdict red across that whole interval; reporting the count keeps it visible
    and shrinking instead.

    That reasoning holds only while the population is *shrinking*, which is why
    the advisory is ratcheted at :data:`_DOCKET_MARKING_CEILING`. Every write
    site strips, so a count above the ceiling is not a backlog — it means a
    write path is landing the marking again, and that is a code defect, fixable
    in a PR, and therefore a failure like any other. Without the ratchet the
    check would greet an unbounded regression with the same warning line it
    prints today.

    Two paths clear a row, neither of them a dedicated sweep: a live-slice row
    normalizes on its next live poll, which re-ingests the whole payload, so that
    part of the backlog drains on its own as the rotation comes around. A row
    outside the live slice needs a re-read aimed at it — ``refresh-dockets`` on
    named rows, or a Term re-walk — and stays counted here until one runs.

    ``checked`` is every case row, since the invariant is over all of them; the
    ``LIKE`` is only a prefilter, and the strip decides. That corpus-wide
    denominator is **not** the rate to quote — the marking is a SCOTUS-only
    upstream habit, so ``detail`` carries the SCOTUS count beside it and a
    reader dividing by ``checked`` would understate the concentration by two
    orders of magnitude.
    """
    problems = [
        f"{record['case_id']}: docket_number {stored!r} carries the capital-case "
        + f"marking (the number is {cleaned!r})"
        for record in conn.execute(
            "SELECT case_id, docket_number FROM cases "
            "WHERE docket_number LIKE '%*%' ORDER BY case_id"
        )
        if (cleaned := corpus.strip_docket_annotation(stored := str(record["docket_number"])))
        != stored
    ]
    scotus = int(
        conn.execute("SELECT count(*) AS n FROM cases WHERE court = 'scotus'").fetchone()["n"]
    )
    if len(problems) > _DOCKET_MARKING_CEILING:
        # Past the ceiling the population is growing, so this is a write path
        # that stopped stripping — a code defect, and a failure like any other.
        return _check(
            CHECK_DOCKET_NUMBER_MARKING,
            problems,
            checked=corpus.count(conn),
            detail=(
                f"{len(problems)} of {scotus} SCOTUS row(s) carry the marking, above the "
                f"ceiling of {_DOCKET_MARKING_CEILING} — a write site is landing it again"
            ),
        )
    return _advisory(
        CHECK_DOCKET_NUMBER_MARKING,
        problems,
        checked=corpus.count(conn),
        detail=(
            # "advisory" leads the line because `detail` is what travels into the
            # `::warning::` and the dashboard's monitored list, where nothing
            # else distinguishes this from a baseline-gated pass.
            f"advisory: {len(problems)} of {scotus} SCOTUS row(s) still carry the "
            "marking; cleared by re-ingest (a live-slice row on its next poll, one "
            "outside it on a targeted re-read)"
            if problems
            else "no marked docket numbers stored"
        ),
    )


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


def _is_excepted(case_id: str) -> bool:
    """Whether this row's terminal is recorded off its own docket (see the set above)."""
    return case_id in _OFF_DOCKET_TERMINAL_CASES


def check_stale_unparsed_grants(conn: sqlite3.Connection, today: date) -> CorpusCheck:
    """A long-past cert grant must have resolved into a merits outcome by now.

    The population is :func:`fedcourtsai.corpus.opens_merits_proceeding` — the
    grants that open a merits proceeding — and the defect is a row that carries
    neither a parsed ``merits_judgment`` nor a recorded ``merits_terminated``
    ``_STALE_GRANT_DAYS`` after its own grant. Such a row is not a pending case;
    it is a decided docket whose outcome the record never captured, because the
    judgment sweep could not read its terminal entry or never reached a
    snapshot of it.

    The point is that the residue stops being latent — and stops spending.
    The merits fan-out arm refuses this exact class at the queue seam
    (:func:`fedcourtsai.corpus.is_stale_unparsed_grant`, over the same
    population and the same bound), so a row this check turns red can never
    also be earning forecast cells: a *forward* cell on a case decided years
    ago is a mislabeled backtest with unrestricted retrieval. Inside the
    bound — a fresh grant whose judgment simply has not parsed yet — the
    snapshot-reading guards hold the line instead: the mint's pendency check
    (:func:`fedcourtsai.merits_event_migration._pendency_conflict`) and
    provisioning's leakage scan re-derive from the stored payload what the
    row failed to record. A failing check therefore
    names the cases whose record needs mending, which is the durable fix.

    A row in :data:`_OFF_DOCKET_TERMINAL_CASES` is **excepted**: no order ever
    disposed of it, so the ``merits_judgment`` half of the clear is unreachable
    from docket text and this row will not stop failing on its own. Excepting it
    retires a permanently unmendable row rather than forgiving a mendable one —
    the curated ``merits_terminated`` remains available and is preferred where a
    writer-lane pass is being composed (see the constant). Excepted rows stay in
    ``checked`` and every excepted row this run found is named in ``detail``, so
    the exemption is auditable on the same durable surface as a failure rather
    than silently dropped from the population. The exemption is this check's
    alone: :func:`fedcourtsai.corpus.is_stale_unparsed_grant` keeps refusing the
    same rows at the merits queue seam, because a record that needs no mending is
    still not a pending case.

    Corpus-side, so it runs on the scheduled verdict rather than the offline
    gate. Dates are stored ISO ``YYYY-MM-DD``, so a lexicographic ``<`` is a
    correct comparison. Unlike the row-shaped checks this one takes no SQL
    ``LIMIT``: the count *is* the signal, the population is the few hundred
    SCOTUS grants rather than the whole corpus, and ``_check`` truncates the
    published sample anyway.
    """
    cutoff = (today - timedelta(days=_STALE_GRANT_DAYS)).isoformat()
    dispositions = sorted(d.value for d in MERITS_PROCEEDING_DISPOSITIONS)
    placeholders = ", ".join("?" for _ in dispositions)
    population = (
        "FROM cases WHERE court = 'scotus' AND date_cert_granted IS NOT NULL "
        f"AND disposition IN ({placeholders})"
    )
    checked = int(conn.execute(f"SELECT count(*) {population}", dispositions).fetchone()[0])
    # The message opens with the grant date because `_check` re-sorts the
    # sample lexicographically: leading with the date makes the published
    # twenty the *oldest* grants rather than the lowest case ids.
    #
    # The exception list is applied *here*, over the defect rows, rather than in
    # the SQL population: an excepted case is one the check looked at and
    # declines to fail, so it stays inside `checked` and the denominator keeps
    # meaning the same thing whether or not the list is empty.
    defects = [
        (str(record["case_id"]), str(record["date_cert_granted"]))
        for record in conn.execute(
            f"SELECT case_id, date_cert_granted {population} "
            "AND date_cert_granted < ? AND merits_judgment IS NULL "
            "AND merits_terminated IS NULL",
            (*dispositions, cutoff),
        )
    ]
    excepted = sorted(case_id for case_id, _granted in defects if _is_excepted(case_id))
    problems = [
        f"granted {granted}: {case_id} still carries no merits judgment or termination"
        for case_id, granted in defects
        if not _is_excepted(case_id)
    ]
    # Rows this old that a termination *did* resolve are carried in the detail
    # rather than left implicit, because a termination clears this check
    # permanently and the classes do not all make that an equal trade: most
    # record a proceeding that demonstrably ended with nothing to recover,
    # while a `judgment-issued` stamp closes pendency over a case that *was*
    # decided on a docket whose disposition entry was never captured. Pooling
    # them into one number would average away the one sub-count that means
    # something bad, so the class breakdown rides beside the total.
    by_class = {
        str(record["merits_terminated"]): int(record["n"])
        for record in conn.execute(
            f"SELECT merits_terminated, count(*) AS n {population} "
            "AND date_cert_granted < ? AND merits_judgment IS NULL "
            "AND merits_terminated IS NOT NULL GROUP BY merits_terminated "
            "ORDER BY merits_terminated",
            (*dispositions, cutoff),
        )
    }
    terminated = sum(by_class.values())
    breakdown = ", ".join(f"{value} {name}" for name, value in by_class.items())
    # Every excepted id is named, not counted: three ids fit on the line, and a
    # bare count would make the exemption the one part of the verdict a reader
    # cannot audit against `_OFF_DOCKET_TERMINAL_CASES`.
    exemption = f"; excepted (terminal off-docket): {', '.join(excepted)}" if excepted else ""
    return _check(
        CHECK_STALE_UNPARSED_GRANTS,
        problems,
        checked=checked,
        detail=(
            f"granted before {cutoff} ({_STALE_GRANT_DAYS} days); "
            f"{terminated} resolved by termination"
            + (f" ({breakdown})" if breakdown else "")
            + exemption
        ),
    )


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
      do not rewrite (this check is the standing monitor). It fails only when the count climbs
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
        f"baseline {_CASE_DATE_ORDER_BASELINE} (as of {cutoff}); faithful upstream data — "
        "investigate the climb upstream before raising the baseline",
        problems=sorted(problems)[:_MAX_PROBLEMS],
    )


def check_domain_values(conn: sqlite3.Connection, tracked_courts: list[str] | None) -> CorpusCheck:
    """Coded columns must hold values from their declared vocabulary.

    A case ``disposition`` (when set) must be a :class:`~fedcourtsai.schemas.Disposition`,
    an ``application_kind`` (when set) an
    :class:`~fedcourtsai.pipeline.interim_signals.ApplicationKind`,
    an event ``kind`` an :class:`~fedcourtsai.schemas.EventKind`, and every case and
    event ``court`` one of the tracked courts. The pydantic enums enforce most of
    this at write time, so a violation means a corpus rebuilt from a source that
    bypassed them — defensive, like the duplicate check. ``application_kind`` is
    typed as text on the row models, so this check is its only vocabulary
    enforcement — and its storage latch compares the literal ``'unknown'``, so an
    off-vocabulary value would latch as if it were a real reading. The
    tracked-court half is skipped
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
    application_kinds = sorted(k.value for k in ApplicationKind)
    kind_values_ph = ", ".join("?" for _ in application_kinds)
    for r in conn.execute(
        f"SELECT case_id, application_kind FROM cases WHERE application_kind IS NOT NULL "
        f"AND application_kind NOT IN ({kind_values_ph}) ORDER BY case_id LIMIT ?",
        (*application_kinds, _MAX_PROBLEMS),
    ):
        problems.append(
            f"case {r['case_id']!r} has unknown application_kind {r['application_kind']!r}"
        )
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
    file that cannot be parsed is skipped rather than counted as an orphan — and
    a payload that parses to something other than an object is malformed too, so
    it is skipped rather than raising out of the verdict.
    """
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
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


def check_corpus_events_in_ledger(conn: sqlite3.Connection, data_root: Path) -> CorpusCheck:
    """Every minted forecast moment in the corpus must carry its ledger definition.

    :func:`check_ledger_references` runs ledger→corpus: no judgment about an
    event the raw-fact store does not know. This is the same rule the other
    way. A declared **minted** moment
    (:func:`fedcourtsai.pipeline.moments.minted_moment_ids`) exists only because
    a mint seam wrote it, and that seam writes the corpus row and the ledger
    ``event.yaml`` together
    (:func:`fedcourtsai.pipeline.outcome.persist_moment_events`) — so a corpus
    row with no committed definition is a half-landed mint.

    Why that matters, given that ``materialize-event`` would project the row
    into the ledger at a cell's first touch anyway. Two reasons, and neither is
    the cell: **git is the pre-registration record**, so a moment must be
    declared there when it is *minted* — the day it became forecastable — not
    at whatever later touch happens to occur, or that date is recoverable only
    from the corpus blob. And a moment that never earns a cell never gets that
    touch: provisioning can refuse, and the materialization is skipped with it,
    so a corpus-only mint can go undefined until resolution, if it resolves at
    all. The offline gate's :func:`check_ledger_events_in_git` is no substitute
    either — it only notices once an artifact lands under the empty directory.

    A stage's case-level baseline is deliberately **not** in the population:
    the ingest projection derives it from a docket's own shape, so the corpus
    holds one for every case it has ever seen, and its ledger half is owed at
    first touch or at resolution rather than at discovery. Requiring a file
    there would fail on the whole corpus rather than on a defect.

    Scoped to SCOTUS, the only court whose stages declare moments at all. The
    scan is unindexed on ``court``, which is affordable because
    ``validate-corpus`` runs only where the corpus has been *pulled* — never
    against the ranged backend, whose per-query egress this would dominate.
    """
    minted_ids = moments.minted_moment_ids()
    problems: list[str] = []
    checked = 0
    for record in conn.execute(
        "SELECT case_id, event_id FROM events WHERE court = 'scotus' ORDER BY case_id, event_id"
    ):
        case_id, event_id = str(record["case_id"]), str(record["event_id"])
        if event_id not in minted_ids:
            continue
        court_id, _, docket = case_id.partition("/")
        if not docket.isdigit():
            # No numeric docket id, so the row addresses no ledger path at all —
            # a different defect (a malformed case id), and not this one's.
            continue
        checked += 1
        if not CasePaths(data_root, court_id, int(docket)).event(event_id).event_file.is_file():
            problems.append(
                f"event ({case_id!r}, {event_id!r}) is minted in the corpus "
                "with no event.yaml in the ledger"
            )
    return _check(CHECK_CORPUS_EVENTS_IN_LEDGER, problems, checked=checked)


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
        if not isinstance(data, dict):
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


def check_base_rate_version(data_root: Path) -> CorpusCheck:
    """A recorded base-rate basis must agree with the scored prediction's record.

    The basis and its version are one record: ``base_rate_basis`` says which
    population the segment base rate was read over, and
    ``base_rate_salience_version`` says under which salience version that
    population was banded — a skill score is only comparable to another taken
    under the same pair (``metrics/README.md``). Two shapes contradict that
    record, and both fail here as they do at the stamp — the stamp is a run-log
    error, this check is what keeps the cell out of a merged ledger:

    - a ``risk_set`` basis beside a null version. On the ``risk_set`` path the
      version is the scored prediction's frozen ``context.salience_version``,
      so the null means the join found no prediction, no frozen context, or no
      version in it — the rate was taken off a risk-set table nothing pins
      down.
    - a ``terminal`` basis on a **cert** cell while the scored prediction —
      the predictor's latest for the event, the same join every scoring
      surface uses — froze a band at all. ``terminal`` is the fallback for a
      prediction that froze no band, so against a frozen band it prices the
      cell off the wrong population; where the band's version also resolves
      the record looks well-formed while doing so. Cert-only because the
      frozen-band pairing is a cert-petition concept while the frozen context
      is stamped per case, so on any other stage a case-level band must not
      reach this rule — the same narrowing the stamp's guard applies.

    A record that took no segment base rate (both halves null) and a
    ``terminal`` record whose version is not yet stamped still pass. The
    terminal-version gap is a weaker guarantee than it looks: a never-stamped
    ``terminal`` cell was banded under whatever scorer was live when it ran,
    which need not be today's, so its version is genuinely unknown — only a
    stamp contemporaneous with the evaluation, which the workflow makes it,
    records the right one, and a later re-stamp overwrites it with the live
    version rather than leaving the gap. Tolerated here because the stamp, not
    the ledger, is where that answer exists. The terminal-basis rule inherits
    the same caveat from the other side: its join reads the predictor's latest
    prediction *now*, so a prediction landing after the evaluation would
    retro-judge a record that was correct when written — accepted because a
    resolved event takes no further predictions, which is what keeps the join
    stable once an evaluation exists.

    The remedy is a corrected evaluation whose rate, basis, and version come
    off one population together (omitting the rate is always open), never a
    relabel of the recorded basis under the number as written: that would pair
    one population's version with a rate read over the other's table — a worse
    record than the null, because nothing downstream could tell the two apart.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/evaluations/*/*/*/evaluation.json"):
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        basis = data.get("base_rate_basis")
        if basis == "risk_set":
            checked += 1
            if data.get("base_rate_salience_version") is None:
                problems.append(
                    f"evaluation {path}: base_rate_basis 'risk_set' with a null "
                    + "base_rate_salience_version"
                )
        elif basis == "terminal":
            checked += 1
            # `==`, never `is`: the models carry `use_enum_values`, so the
            # stage comes back as the enum's value.
            if _evaluation_event_stage(path) != Stage.cert:
                continue
            context = _scored_prediction_context(path, data.get("predictor_id"))
            if context is not None and context.band is not None:
                problems.append(
                    f"evaluation {path}: base_rate_basis 'terminal' while the scored "
                    + f"prediction froze band {context.band!r} — the fallback taken "
                    + "where a risk-set pairing was available"
                )
    return _check(CHECK_BASE_RATE_VERSION, problems, checked=checked)


def _evaluation_event_stage(evaluation_path: Path) -> Stage | None:
    """The declared stage of the event one evaluation file sits under.

    Tolerant like the rest of this check's inputs: ``None`` where the event
    file is missing or does not parse — that is another check's problem, and a
    rule keyed on the stage must not fire off a record it cannot read.
    """
    event_file = evaluation_path.parents[4] / "event.yaml"
    try:
        return PredictableEvent.model_validate(yaml.safe_load(event_file.read_text())).stage
    except (OSError, ValueError, ValidationError):
        return None


def _scored_prediction_context(
    evaluation_path: Path, predictor_id: object
) -> PredictionContext | None:
    """The frozen context of the scored prediction for one evaluation file.

    The scored prediction is the evaluation's predictor's **latest** for the
    event by :func:`fedcourtsai.integrity.cell_clock` — the same join every
    scoring surface uses. ``predictor_id`` is the evaluation record's own
    field, never the directory name, because the stamp and every scoring
    surface join on the field and an un-aliasing that moved the directory but
    not the field (or vice versa) must not make the two enforcers of one rule
    score different predictions. ``None`` where the field is not a string, no
    prediction parses, or the latest carries no context; a file that fails to
    parse is another check's problem, never reported as a join miss here.
    """
    if not isinstance(predictor_id, str) or not predictor_id:
        return None
    event_dir = evaluation_path.parents[4]
    predictions = []
    for path in sorted(event_dir.glob(f"predictions/{predictor_id}/*/prediction.json")):
        try:
            predictions.append(Prediction.model_validate_json(path.read_text()))
        except (OSError, ValidationError):
            continue
    if not predictions:
        return None
    return max(predictions, key=cell_clock).context


def check_prediction_docs(data_root: Path) -> CorpusCheck:
    """Every prose document a prediction names must exist beside the prediction.

    ``prediction.json`` points at its prose by filename — ``reasoning_doc`` (the
    predictor's rationale for its numbers) and ``predicted_reasoning_doc`` (its
    forecast of the court's reasoning). Schema conformance only checks the pointer
    is a string, so a cell that names a document it never wrote passes ``validate``
    with a dangling pointer, and every later reader — an evaluator, a scorer — finds
    nothing where the prediction promised prose. This check resolves the pointers.

    A pointer must also be a plain filename in the prediction's own directory: a
    document named through a separator or ``..`` would reach outside the cell's lane,
    so it is flagged rather than followed.

    For a **process-stamped** cell, a null ``predicted_reasoning_doc`` is itself a
    problem: the prompt contract requires the forecast document at every stage, and
    the field is nullable only so records written before it existed still validate.
    The stamp is the key because no stamped record predates the field: the whole
    committed ledger is unstamped (the alpha marker), no predict run has committed
    since stamping was wired, and every run after it also carries the field — so a
    stamped cell missing the document is a broken cell, never a legacy shape.
    Unstamped (alpha/shakedown) records stay valid.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/predictions/*/*/prediction.json"):
        # Parsed through the model so an omitted `reasoning_doc` resolves to its
        # declared default rather than reading as "no document named". A file that
        # does not parse is `validate_ledger`'s concern (schema law), so it is
        # skipped here rather than double-reported.
        try:
            prediction = Prediction.model_validate(json.loads(path.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if prediction.process_version is not None and prediction.predicted_reasoning_doc is None:
            problems.append(
                f"prediction {path}: predicted_reasoning_doc is null on a "
                "process-stamped cell; no stamped record predates the field, so "
                "the prompt contract's required forecast document is missing "
                "rather than merely pre-dating it"
            )
        for field_name, doc in (
            ("reasoning_doc", prediction.reasoning_doc),
            ("predicted_reasoning_doc", prediction.predicted_reasoning_doc),
        ):
            if doc is None:
                continue
            checked += 1
            if not doc or Path(doc).name != doc or doc in (".", ".."):
                problems.append(
                    f"prediction {path}: {field_name} {doc!r} is not a plain filename "
                    "beside the prediction"
                )
            elif (path.parent / doc).is_symlink():
                problems.append(
                    f"prediction {path}: {field_name} {doc!r} is a symlink; a "
                    "document must be a real file in the cell's own directory"
                )
            elif not (path.parent / doc).is_file():
                problems.append(f"prediction {path}: {field_name} {doc!r} does not exist")
    return _check(CHECK_PREDICTION_DOCS, problems, checked=checked)


def check_prediction_claims(data_root: Path) -> CorpusCheck:
    """A committed claims block must be one the claim scorer will not void.

    Schema conformance cannot see the void conditions — a duplicated claim id,
    a declared claim left unstated, a headline claim diverging from the
    prediction's own ``probability`` — and the scorer's refusal is
    deliberately silent at read time (``None``, never a crash), so an
    incoherent block would commit green and the claim board would simply lack
    the cell weeks later. Surfaced here instead, while the cell can still be
    fixed. Absence stays legitimate: a prediction without a block, or on an
    event with no declared set, is skipped, not flagged.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/predictions/*/*/prediction.json"):
        # Parsed through the model; a file that does not parse is
        # `validate_ledger`'s concern (schema law), not double-reported here.
        try:
            prediction = Prediction.model_validate(json.loads(path.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if prediction.claims is None:
            continue
        checked += 1
        problems.extend(
            f"prediction {path}: {reason}" for reason in claim_block_problems(prediction)
        )
    return _check(CHECK_PREDICTION_CLAIMS, problems, checked=checked)


def check_prediction_semantic_claims(data_root: Path) -> CorpusCheck:
    """A committed semantic block must answer the declaration it was asked for.

    The semantic sibling of :func:`check_prediction_claims`, and it exists
    because the failure is quieter: a mechanical block that voids at least costs
    the cell its ``claim_scores``, whereas a non-conforming ``semantic_claims``
    block is simply read past — the declaration fixes what a grader grades, so a
    claim the predictor invented is never asked about and a declared claim it
    skipped is graded against nothing it wrote. Neither shows up anywhere later.
    Surfaced here instead, while the cell can still be fixed. Absence stays
    legitimate: a prediction without a block, or on an event declaring no
    semantic set, is skipped rather than flagged.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/predictions/*/*/prediction.json"):
        # Parsed through the model; a file that does not parse is
        # `validate_ledger`'s concern (schema law), not double-reported here.
        try:
            prediction = Prediction.model_validate(json.loads(path.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if prediction.semantic_claims is None:
            continue
        checked += 1
        problems.extend(
            f"prediction {path}: {reason}" for reason in semantic_claim_problems(prediction)
        )
    return _check(CHECK_PREDICTION_SEMANTIC, problems, checked=checked)


def check_evaluation_semantic_grades(data_root: Path) -> CorpusCheck:
    """A committed semantic grade block must be one the roll-up will not refuse.

    ``pipeline.semantic.graded_units`` refuses a non-conforming block **whole**
    and silently — the same deliberate quiet as the claim scorer's — so a block
    that skips a declared claim, grades one twice, or answers another
    declaration would commit green and drop out of the census weeks later, with
    nothing recording that a grader graded this cell at all. The refusal is
    right; the silence is what this check replaces. Absence stays legitimate: an
    evaluation without a block, or on an event declaring no semantic set, is
    skipped rather than flagged.
    """
    problems: list[str] = []
    checked = 0
    for path in _ledger_files(data_root, "*/*/events/*/evaluations/*/*/*/evaluation.json"):
        try:
            evaluation = Evaluation.model_validate(json.loads(path.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if evaluation.semantic_grades is None:
            continue
        checked += 1
        problems.extend(
            f"evaluation {path}: {reason}" for reason in semantic_grade_problems(evaluation)
        )
    return _check(CHECK_EVALUATION_SEMANTIC, problems, checked=checked)


def check_merits_predictions(data_root: Path) -> CorpusCheck:
    """A merits-stage event's latest prediction per predictor must carry a judgment.

    The half of the merits prediction contract the schema cannot enforce
    self-contained: a ``prediction.json`` does not carry its event's stage, so
    the schema holds "judgment set => votes non-empty" while this check reads
    the committed ``event.yaml`` and holds "merits-stage event => the scored
    prediction carries a judgment". Latest per predictor, because that is the
    prediction every scoring join reads (the evaluation layout has no slot for
    a prediction run id); an earlier judgment-less run superseded by a
    compliant one is history, not a defect. A file that does not parse is
    ``validate_ledger``'s concern (schema law) and is skipped here.

    The directory test comes before the parse deliberately: ``validate data``
    runs once per cell in both fan-outs, and most of the ledger's events carry
    no predictions at all, so parsing every ``event.yaml`` to reach a handful
    would put the whole ledger's YAML cost on every cell. The two orders check
    the same events.
    """
    problems: list[str] = []
    checked = 0
    for event_file in _ledger_files(data_root, "*/*/events/*/event.yaml"):
        predictions_root = event_file.parent / "predictions"
        if not predictions_root.is_dir():
            continue
        try:
            event = PredictableEvent.model_validate(yaml.safe_load(event_file.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if event.stage != Stage.merits:
            continue
        for predictor_dir in sorted(p for p in predictions_root.iterdir() if p.is_dir()):
            predictions = []
            for path in sorted(predictor_dir.glob("*/prediction.json")):
                try:
                    predictions.append(Prediction.model_validate(json.loads(path.read_text())))
                except (OSError, ValueError, ValidationError):
                    continue
            if not predictions:
                continue
            checked += 1
            latest = max(predictions, key=cell_clock)
            if latest.judgment is None:
                problems.append(
                    f"prediction {predictor_dir}: latest prediction for merits-stage "
                    f"event {event.event_id!r} carries no judgment"
                )
    return _check(CHECK_MERITS_PREDICTIONS, problems, checked=checked)


def check_scored_votes(data_root: Path) -> CorpusCheck:
    """No committed evaluation may carry ``vote_accuracy`` off a merits event.

    An individual cert vote is never scored (``docs/decision-model.md``), and
    ``pipeline.moments.scores_votes`` enforces that wherever the harness computes
    the figure. But on a real cell ``vote_accuracy`` is the *evaluator's* field to
    write on every stage — the harness stamps ``claim_scores``, the base-rate
    basis record, and (on the merits and interim stages only) the whole skill
    record of ``brier_score`` / ``segment_base_rate`` / ``brier_skill_score``,
    but never this field anywhere — so the computed gate cannot speak for an
    agent that wrote the number itself. The leaderboard refuses to aggregate
    such a value, which keeps it out of every published total; this check
    refuses to let it be committed at all, so the prohibition holds on the
    artifact and not merely on the figures derived from it.

    Read against the committed ``event.yaml`` rather than the moments register:
    an ``evaluation.json`` does not carry its event's stage, and the ledger's
    stage stamp is what a reader of the artifact sees. That makes this the same
    shape as :func:`check_merits_predictions` — the schema holds what it can
    self-contained, and the half needing the event definition lives here. A file
    that does not parse is ``validate_ledger``'s concern (schema law) and is
    skipped.

    The directory test precedes the parse for the reason
    :func:`check_merits_predictions` gives: most events carry no evaluations, and
    ``validate data`` runs once per cell in both fan-outs.
    """
    problems: list[str] = []
    checked = 0
    for event_file in _ledger_files(data_root, "*/*/events/*/event.yaml"):
        evaluations_root = event_file.parent / "evaluations"
        if not evaluations_root.is_dir():
            continue
        try:
            event = PredictableEvent.model_validate(yaml.safe_load(event_file.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        if event.stage == Stage.merits:
            continue
        for path in sorted(evaluations_root.glob("*/*/*/evaluation.json")):
            try:
                evaluation = Evaluation.model_validate(json.loads(path.read_text()))
            except (OSError, ValueError, ValidationError):
                continue
            checked += 1
            if evaluation.vote_accuracy is not None:
                problems.append(
                    f"evaluation {path}: carries vote_accuracy on "
                    f"{event.stage or 'stage-less'}-stage event {event.event_id!r} — "
                    f"a vote is scored only on a merits event"
                )
    return _check(CHECK_SCORED_VOTES, problems, checked=checked)


def check_evaluation_correct_agrees(data_root: Path) -> CorpusCheck:
    """One cell's current gradings must record the same ``correct`` bit.

    ``correct`` is not a judgment: ``stamp-cell --role evaluator`` computes it
    through :func:`fedcourtsai.pipeline.evaluate.is_correct` from the
    predictor's latest committed prediction and the committed outcome. Both
    inputs are properties of the cell — the ``(case_id, event_id,
    predictor_id)`` triple — and neither depends on *who* judged it, so two
    graders reading one cell cannot land on different bits *from the same
    committed pair*. A disagreement means the group's stamps did not read one
    pair: an evaluator's own bit that predates correct-stamping (or a
    hand-edit) surviving, or two graders' stamps straddling a re-prediction so
    each read a different "latest" prediction. Either way the accuracy column
    — the surface that averages this bit — would fold two answers to two
    different questions into one mean, and the remedy is the same: re-stamp
    the event's evaluations so every current grading reads the current pair.

    **Across runs it is not a defect, so the rule does not reach there.** The
    bit is computed against the predictor's latest prediction *as at stamp
    time*, so a re-predicted cell's older evaluation records what was true when
    it ran — history, exactly as an earlier judgment-less prediction is history
    to :func:`check_merits_predictions`. Nothing aggregates it either: every
    surface collapses re-runs of one grader on one cell first, newest winning.
    So this check collapses the same way, through
    :func:`fedcourtsai.integrity.latest_evaluation_runs`, **before** grouping —
    the rule then holds across evaluators over precisely the records the
    leaderboard reads, and a superseded stamp can neither fire it nor be
    repaired by a gate that has no bulk re-stamp to offer.

    Only **stamped** survivors take part (``process_version`` non-null): an
    unstamped cell's ``correct`` is whatever it was written with, so its
    disagreement with a stamped sibling is the signal the stamp displaces
    rather than a defect to refuse. A null ``correct`` — the value the stamp
    writes where a committed artifact is missing — carries no claim to
    contradict, so it is excluded too. ``checked`` counts the **groups** with
    at least one participating record, since the group is the unit the rule
    holds over; only a group holding two or more can contribute a problem. A
    file that does not parse is ``validate_ledger``'s concern (schema law) and
    is skipped.

    The ``(case_id, event_id, predictor_id)`` key is read from the record's own
    fields, never the path, for the reason
    :func:`_scored_prediction_context` gives: the stamp joins on the fields, so
    an un-aliasing that moved a directory but not a field must not let this
    check group cells the stamp kept apart.
    """
    records: list[tuple[Evaluation, Path]] = []
    for path in _ledger_files(data_root, "*/*/events/*/evaluations/*/*/*/evaluation.json"):
        # Parsed through the model so `process_version` resolves to its declared
        # default on a record that omits it rather than reading as unparseable.
        try:
            evaluation = Evaluation.model_validate(json.loads(path.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        records.append((evaluation, path))
    groups: dict[tuple[str, str, str], list[tuple[int, Path]]] = {}
    for evaluation, path in latest_evaluation_runs(records, lambda record: record[0]):
        if evaluation.process_version is None or evaluation.correct is None:
            continue
        key = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id)
        groups.setdefault(key, []).append((evaluation.correct, path))
    problems: list[str] = []
    for (case_id, event_id, predictor_id), graded in sorted(groups.items()):
        if len({correct for correct, _ in graded}) < 2:
            continue
        recorded = ", ".join(
            f"{correct} at {path}" for correct, path in sorted(graded, key=lambda r: r[1])
        )
        problems.append(
            f"cell ({case_id!r}, {event_id!r}, {predictor_id!r}): its evaluators' current "
            f"gradings record disagreeing `correct` values — {recorded}"
        )
    return _check(CHECK_CORRECT_AGREES, problems, checked=len(groups))


def check_judgment_only_on_merits_outcomes(data_root: Path) -> CorpusCheck:
    """No committed outcome may carry a ``judgment`` off a merits event.

    ``Outcome.judgment`` is the merits axis, and its presence is what routes
    the accuracy comparison: :func:`fedcourtsai.pipeline.evaluate.is_correct`
    takes the judgment comparison wherever the field is non-null and the
    disposition comparison otherwise. That routing is **stage-blind**, so the
    population at risk is every event that is not merits-stage — a judgment
    there does not merely record a field the stage has no use for, it silently
    moves the cell onto the merits axis, where the predictor was never asked
    for a ``judgment`` and the cell is scored against a question it never
    received.
    Stage-less events are inside the rule for the same reason: the router does
    not read the stage, so a missing stamp cannot excuse the misrouting.

    Refusing this cannot cost a legitimate outcome, because the merits outcome
    builder is the only writer of the field: "carries a judgment => merits-stage
    event" is the pipeline's own invariant, and the check holds it on the
    artifact. The schema states it in ``Outcome.judgment``'s own description
    but cannot enforce it — an ``outcome.json`` does not carry its event's
    stage — so the rule needs the committed ``event.yaml`` and lives here, the
    same shape as :func:`check_scored_votes`.

    ``checked`` counts the non-merits events carrying an ``outcome.json``. The
    sibling test comes before the parse for the reason
    :func:`check_merits_predictions` gives: an event with no outcome is outside
    the rule, and ``validate data`` runs once per cell in both fan-outs. An
    ``event.yaml`` that does not parse is ``validate_ledger``'s concern (schema
    law) and is skipped.
    """
    problems: list[str] = []
    checked = 0
    for event_file in _ledger_files(data_root, "*/*/events/*/event.yaml"):
        outcome_file = event_file.parent / "outcome.json"
        if not outcome_file.is_file():
            continue
        try:
            event = PredictableEvent.model_validate(yaml.safe_load(event_file.read_text()))
        except (OSError, ValueError, ValidationError):
            continue
        # `==`, never `is`: the models carry `use_enum_values`, so the stage
        # comes back as the enum's value.
        if event.stage == Stage.merits:
            continue
        checked += 1
        # Read raw rather than through `Outcome`, and deliberately unlike the
        # sibling checks: any non-null value misroutes `is_correct` whatever it
        # is, so a judgment outside the vocabulary must fire here rather than
        # be skipped as a model-parse failure. The enclosing file being
        # malformed JSON is still `validate_ledger`'s concern.
        try:
            data = json.loads(outcome_file.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        judgment = data.get("judgment")
        if judgment is not None:
            problems.append(
                f"outcome {outcome_file}: carries judgment {judgment!r} on "
                f"{event.stage or 'stage-less'}-stage event {event.event_id!r} — "
                "the field is the merits axis, and its presence routes the accuracy "
                "comparison off the disposition this cell forecast"
            )
    return _check(CHECK_JUDGMENT_ONLY_MERITS, problems, checked=checked)


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
    every judgment references an event defined in git, every evaluation targets
    a prediction that exists, every recorded ``risk_set`` base-rate basis carries
    the salience version it was banded under, every prose document a prediction
    names is there, every committed claims block is one the claim scorer will not
    void, every committed semantic block on either side answers the declaration
    it was asked for, every merits-stage event's scored prediction carries
    its judgment, one cell's current gradings record the same ``correct`` bit,
    and no outcome carries a judgment off a merits event.
    The corpus-dependent referential checks (which need
    the corpus blob) stay on the schedule — the gate is deliberately offline.
    """
    return [
        check_ledger_events_in_git(data_root),
        check_evaluation_targets(data_root),
        check_base_rate_version(data_root),
        check_prediction_docs(data_root),
        check_prediction_claims(data_root),
        check_prediction_semantic_claims(data_root),
        check_evaluation_semantic_grades(data_root),
        check_merits_predictions(data_root),
        check_scored_votes(data_root),
        check_evaluation_correct_agrees(data_root),
        check_judgment_only_on_merits_outcomes(data_root),
    ]


# --- orchestration -------------------------------------------------------------


def _run_checks(
    conn: sqlite3.Connection,
    *,
    data_root: Path,
    today: date,
    baseline_count: int | None,
    tracked_courts: list[str] | None,
) -> CorpusValidation:
    """Run every check against an open corpus and roll the results into a verdict."""
    checks = [
        _check(CHECK_CORPUS_OPENS, [], checked=1, detail="corpus opened"),
        check_row_count_monotonic(conn, baseline_count),
        check_required_columns(conn),
        check_docket_number_marking(conn),
        check_snapshot_not_future(conn, today),
        check_stale_unparsed_grants(conn, today),
        check_case_dates(conn, today),
        check_domain_values(conn, tracked_courts),
        check_no_duplicates(conn),
        check_ledger_references(conn, data_root),
        # Corpus-dependent, so it stays off `run_ledger_referential_checks` —
        # that gate is deliberately offline and has no corpus to read.
        check_corpus_events_in_ledger(conn, data_root),
        check_evaluation_targets(data_root),
        check_base_rate_version(data_root),
        check_prediction_docs(data_root),
        check_prediction_claims(data_root),
        check_prediction_semantic_claims(data_root),
        check_evaluation_semantic_grades(data_root),
        check_merits_predictions(data_root),
        check_scored_votes(data_root),
        check_evaluation_correct_agrees(data_root),
        check_judgment_only_on_merits_outcomes(data_root),
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
    today: date,
    baseline_count: int | None = None,
    tracked_courts: list[str] | None = None,
) -> CorpusValidation:
    """Validate the corpus + ledger and return the verdict (the CLI is a thin wrapper).

    Graceful when the corpus is absent — returns a skipped verdict (``ok`` true, no
    checks), so the command is safe to call before a corpus pull. If the file
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

    Reads the ``has_opinion`` presence bit, not ``opinion_text``, so it holds under
    the corpus split (the opinion body moves to the content store).
    """
    return bool(
        row.has_opinion or row.citations or row.citation_count or row.date_decided is not None
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


# The bucket whose docket-number shapes we histogram, so a refinement can see
# exactly which formats the Term parser would need to handle. Kept as a constant so the
# tally below and the bucket label never drift apart. Accepted-fragment threshold: a
# shape carrying fewer than ~100 open events is an accepted fragment — it stays
# visible in this bucket and the shape histogram by design, and no exclusion
# predicate is chased for it (the residual tail is cheaper to see than to classify).
_UNPARSEABLE_REASON = "docket Term not parseable (a format the predicate skips)"

# Top docket-number shapes to report — enough to see the long tail, still bounded.
_MAX_SHAPES = 15


def _unclassified_reason(row: corpus.CorpusRow) -> str:
    """Why an open SCOTUS event no predicate excluded stays in scope (audit bucketing)."""
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
    """Census the corpus's open events that the predict scope excludes.

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
