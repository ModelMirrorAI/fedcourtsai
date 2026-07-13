"""The corpus-side scope reconcile for predict scope.

The write counterpart of the read-only scope audit (``validate.run_scope_audit``).
Where the matrix gate excludes out-of-scope cases at *read time* and the
maintainer-run cleanup sweep
prunes their already-merged *git* predictions, this reconcile materializes the
exclusion into the **corpus**: it latches ``predict_excluded`` on cases an
exclusion predicate now matches, so ``store.open_events`` yields nothing for them
(they leave the predictable set at the source, not just the backstop), and clears
the latch on cases that have returned to scope.

It is **deterministic** (a pure function of the corpus + the shared reason
evaluator ``corpus.out_of_scope_reason_full``, which spans the row-only rules and
the snapshot-aware bare opinion-import rule) and **two-directional** — the latch
is not monotonic — so re-running it converges. Scoped
to the SCOTUS-docket universe (the prediction scope): a case that could never be
predicted needs no latch. It also normalizes the derived ``predict_eligible``
convenience column to the scope predicate (``court == 'scotus'``), so rows
latched under an earlier, broader rule converge — correctness never depends on
the column (every scope seam reads the court predicate directly).
``run-pull``'s historical job owns running it where the corpus is
pulled, with ``fedcourts corpus-push``.
"""

from __future__ import annotations

import sqlite3

from .. import corpus
from ..schemas import ScopeReconcileResult

# Bounded per-direction sample of affected case ids, for the run log / PR note.
_MAX_SAMPLE = 20


def reconcile_predict_scope(conn: sqlite3.Connection, *, apply: bool) -> ScopeReconcileResult:
    """Reconcile the ``predict_excluded`` latch across the predict-eligible cases.

    Dry run by default (counts what would change, writes nothing); ``apply`` performs
    the latch writes. Idempotent — a second run with no corpus change reports zero.
    """
    eligible = 0
    to_exclude: list[str] = []
    to_release: list[str] = []
    for row in corpus.iter_rows(conn, court="scotus"):
        eligible += 1
        should_exclude = corpus.out_of_scope_reason_full(conn, row) is not None
        if should_exclude and not row.predict_excluded:
            to_exclude.append(row.case_id)
        elif not should_exclude and row.predict_excluded:
            to_release.append(row.case_id)
    normalized = 0
    if apply:
        for case_id in to_exclude:
            corpus.set_predict_excluded(conn, case_id, True)
        for case_id in to_release:
            corpus.set_predict_excluded(conn, case_id, False)
        # Hygiene, not correctness: converge the derived scope columns to the
        # court predicate so rows written under the earlier, broader rule read
        # consistently (every scope seam uses the court predicate directly).
        normalized = corpus.normalize_predict_eligible(conn)
    return ScopeReconcileResult(
        applied=apply,
        skipped=False,
        eligible_cases=eligible,
        excluded=len(to_exclude),
        released=len(to_release),
        normalized=normalized,
        sample_excluded=sorted(to_exclude)[:_MAX_SAMPLE],
        sample_released=sorted(to_release)[:_MAX_SAMPLE],
    )
