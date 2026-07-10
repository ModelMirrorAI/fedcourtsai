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
gate drops on — :func:`corpus.is_historical_mandatory`,
:func:`corpus.is_stale_unresolvable` — does double duty here, one predicate
with two enforcement points (the forward gate in ``cli._scope_filtered`` and this
backward sweep). The event definition and any ``outcome.json`` stay; only the
out-of-scope predictions go.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pydantic import BaseModel

from . import corpus


class PrunableCase(BaseModel):
    """An out-of-scope case whose committed prediction directories should be pruned."""

    case_id: str
    reason: str
    paths: list[str]  # repo-relative `…/predictions` directories to remove


class CleanupPr(BaseModel):
    """The branch and PR prose for a sweep, rendered here so the workflow only plumbs."""

    branch: str
    title: str
    commit_message: str
    body: str


def render_cleanup_pr(
    prunable: list[PrunableCase], run_id: str, issue: int | None = None
) -> CleanupPr:
    """Render the review PR (branch / title / commit / body) for a sweep's results.

    Keeps the branch name and the markdown — the per-case table and the optional
    ``Closes #<issue>`` line — in tested code rather than assembled with ``jq`` and a
    heredoc in the workflow (mirroring how ``collect_plan`` renders the run PR). The
    workflow passes its run id for a unique branch and the trigger issue (if any).
    """
    count = len(prunable)
    plural = "" if count == 1 else "s"
    title = f"cleanup: prune predictions for {count} out-of-scope case{plural}"
    rows = "\n".join(
        f"| `{case.case_id}` | {case.reason} | {len(case.paths)} |" for case in prunable
    )
    closes = f"\nCloses #{issue}.\n" if issue is not None else ""
    body = (
        "Deterministic cleanup sweep: pruned merged predictions for cases now out of "
        "predict scope (gated on the live corpus row, not a proxy). The event "
        "definitions and any `outcome.json` are untouched.\n\n"
        "| case | reason | dirs removed |\n"
        "|------|--------|--------------|\n"
        f"{rows}\n"
        f"{closes}\n"
        "Review and merge — this PR is intentionally **not** auto-merged.\n"
    )
    return CleanupPr(
        branch=f"cleanup/out-of-scope-predictions-{run_id}",
        title=title,
        commit_message=title,
        body=body,
    )


def find_out_of_scope_predictions(data_root: Path, corpus_db: Path) -> list[PrunableCase]:
    """Committed prediction directories belonging to out-of-scope cases.

    Walks every ``data/cases/<court>/<docket>/events/<event>/predictions`` directory,
    groups by case, and keeps a case only when its corpus row matches an exclusion
    predicate. A case with predictions but **no** corpus row is left untouched — the
    gate is the real corpus row, never a proxy. Read-only and
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
            reason = corpus.out_of_scope_reason_full(conn, row)
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
