"""Corpus-informed cleanup of committed derived artifacts under ``data/``.

The pipeline's append-only writers (predict / evaluate / reconcile) only ever *add*
artifacts; none removes one that later falls out of scope. This module is the
counterpart: deterministic sweeps that decide — from the corpus, never a proxy —
which already-merged artifacts to prune. They run in the ``run-cleanup`` workflow,
where the corpus is ``dvc pull``'d and the result lands as a reviewed (not
auto-merged) PR.

The decision is a pure function of the corpus plus the committed tree, so it is
testable offline and identical every run. The first rule prunes *predictions* for
cases that are out of predict scope: every scope-exclusion predicate the matrix
gate drops on — :func:`corpus.is_historical_mandatory` (#309),
:func:`corpus.is_stale_unresolvable` (#333) — does double duty here, one predicate
with two enforcement points (the forward gate in ``cli._scope_filtered`` and this
backward sweep). The event definition and any ``outcome.json`` stay; only the
out-of-scope predictions go.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from . import corpus
from .corpus import CorpusRow

# Each (predicate, reason) the matrix gate excludes a case on also makes that case's
# already-merged predictions prunable. Keep in sync with ``cli._scope_filtered``.
OUT_OF_SCOPE_RULES: list[tuple[Callable[[CorpusRow], bool], str]] = [
    (corpus.is_historical_mandatory, "pre-1925 mandatory-jurisdiction matter (#309)"),
    (corpus.is_stale_unresolvable, "stale unresolvable old SCOTUS petition (#333)"),
]


class PrunableCase(BaseModel):
    """An out-of-scope case whose committed prediction directories should be pruned."""

    case_id: str
    reason: str
    paths: list[str]  # repo-relative `…/predictions` directories to remove


def _out_of_scope_reason(row: CorpusRow) -> str | None:
    """The first exclusion reason that matches ``row``, or ``None`` if in scope."""
    for predicate, reason in OUT_OF_SCOPE_RULES:
        if predicate(row):
            return reason
    return None


def find_out_of_scope_predictions(data_root: Path, corpus_db: Path) -> list[PrunableCase]:
    """Committed prediction directories belonging to out-of-scope cases.

    Walks every ``data/cases/<court>/<docket>/events/<event>/predictions`` directory,
    groups by case, and keeps a case only when its corpus row matches an exclusion
    predicate. A case with predictions but **no** corpus row is left untouched — the
    gate is the real corpus row, never a proxy (issue #320). Read-only and
    deterministic (cases and paths returned in sorted order); callers decide whether
    to remove the returned paths. Paths are repo-relative posix strings.
    """
    cases_root = data_root / "cases"
    if not cases_root.exists() or not corpus_db.exists():
        return []
    repo_root = data_root.parent
    by_case: dict[str, list[str]] = {}
    for predictions_dir in sorted(cases_root.glob("*/*/events/*/predictions")):
        if not predictions_dir.is_dir():
            continue
        court, docket = predictions_dir.relative_to(cases_root).parts[:2]
        case_id = f"{court}/{docket}"
        by_case.setdefault(case_id, []).append(predictions_dir.relative_to(repo_root).as_posix())

    prunable: list[PrunableCase] = []
    with corpus.connect(corpus_db) as conn:
        for case_id in sorted(by_case):
            row = corpus.get_row(conn, case_id)
            if row is None:
                continue
            reason = _out_of_scope_reason(row)
            if reason is not None:
                prunable.append(
                    PrunableCase(case_id=case_id, reason=reason, paths=sorted(by_case[case_id]))
                )
    return prunable


def remove(prunable: list[PrunableCase], repo_root: Path) -> int:
    """Delete every prediction directory named in ``prunable``; return the count removed.

    Resolves each repo-relative path under ``repo_root`` and removes the directory
    tree. Idempotent: a path already gone is skipped, so a re-run after a partial
    apply is safe.
    """
    removed = 0
    for case in prunable:
        for rel_path in case.paths:
            target = repo_root / rel_path
            if target.exists():
                shutil.rmtree(target)
                removed += 1
    return removed
