"""The seed-side corpus reconcile for predict scope (issue #343).

The write counterpart of the read-only scope audit (``validate.run_scope_audit``).
Where the matrix gate excludes out-of-scope cases at *read time* and run-cleanup
prunes their already-merged *git* predictions, this reconcile materializes the
exclusion into the **corpus**: it latches ``predict_excluded`` on cases an
exclusion predicate now matches, so ``store.open_events`` yields nothing for them
(they leave the predictable set at the source, not just the backstop), and clears
the latch on cases that have returned to scope.

It is **deterministic** (a pure function of the corpus + the shared reason
evaluator ``corpus.out_of_scope_reason_full``, which spans the row-only rules and
the snapshot-aware bare opinion-import rule) and **two-directional** — the latch
is not monotonic, unlike ``predict_eligible`` — so re-running it converges. Scoped
to the predict-eligible universe: a case that could never be predicted needs no
latch. ``run-seed`` owns running it where the corpus is pulled, with ``dvc push``.
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
    for row in corpus.iter_rows(conn, predict_eligible=True):
        eligible += 1
        should_exclude = corpus.out_of_scope_reason_full(conn, row) is not None
        if should_exclude and not row.predict_excluded:
            to_exclude.append(row.case_id)
        elif not should_exclude and row.predict_excluded:
            to_release.append(row.case_id)
    if apply:
        for case_id in to_exclude:
            corpus.set_predict_excluded(conn, case_id, True)
        for case_id in to_release:
            corpus.set_predict_excluded(conn, case_id, False)
    return ScopeReconcileResult(
        applied=apply,
        skipped=False,
        eligible_cases=eligible,
        excluded=len(to_exclude),
        released=len(to_release),
        sample_excluded=sorted(to_exclude)[:_MAX_SAMPLE],
        sample_released=sorted(to_release)[:_MAX_SAMPLE],
    )
