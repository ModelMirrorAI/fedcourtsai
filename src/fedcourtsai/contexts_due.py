"""When a promotion owes the promotion gate's admin-read ``contexts`` stage.

``scripts/promotion-gate.sh contexts`` reads repository settings — the rulesets,
the environments, the contexts ``main`` requires — and judges them against what
the code expects. It needs repository-administration read, which no CI token
holds, so it runs by hand rather than on every promotion. What it guards drifts
when someone changes a setting, or when a batch changes what the settings are
judged against: a workflow renames a required job or names a new environment
(which GitHub creates unprotected), or a check's own expectations move.

:func:`contexts_due` names the paths in a batch that do the latter. The gate's
``contexts-due`` stage and the promotion train's body print the verdict, so a
promotion that changes one of them says so before it merges; one that changes
none does not ask for the stage. The verdict is advisory and never fails the
gate: a setting changed by hand drifts with no batch at all, which is what
running the stage after any settings change is for.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .promotion_record import git

#: What the ``contexts`` stage judges settings against. A directory entry ends in
#: ``/`` and covers everything under it; any other entry is one file.
CONTEXTS_SENSITIVE: tuple[str, ...] = (
    # The jobs `main`'s ruleset requires, and every environment a job names.
    ".github/workflows/",
    # The stage itself.
    "scripts/promotion-gate.sh",
    # The tested judgments the stage calls.
    "src/fedcourtsai/required_checks.py",
    "src/fedcourtsai/ruleset_checks.py",
    "src/fedcourtsai/environment_checks.py",
    # The configs those judgments read: the corpus-check approver, and the
    # review-hold caps the `review-auto` environment is checked against.
    "config/corpus-check.yaml",
    "config/review-hold.yaml",
)

#: How many due paths the one-line verdict names before counting the rest.
_NAMED = 5


def contexts_due(paths: Iterable[str]) -> list[str]:
    """The paths in ``paths`` that make a promotion owe the ``contexts`` stage, sorted."""
    due = {
        path
        for path in (raw.strip() for raw in paths)
        if path
        and any(
            path.startswith(entry) if entry.endswith("/") else path == entry
            for entry in CONTEXTS_SENSITIVE
        )
    }
    return sorted(due)


def batch_paths(repo: Path, at: str, main_ref: str) -> list[str]:
    """The paths a promotion of ``at`` changes on ``main_ref``: the three-dot diff.

    Three-dot, from the merge base, so what ``main`` gained since the batch
    branched (data commits, a promotion record) is not read as the batch's own.
    """
    return git(repo, "diff", "--name-only", f"{main_ref}...{at}").splitlines()


def verdict_line(due: list[str]) -> str:
    """The one line the gate prints: due, naming what makes it so, or not due."""
    if not due:
        return "contexts: not due — the batch changes nothing the admin-read stage judges against"
    named = ", ".join(due[:_NAMED])
    more = f" (+{len(due) - _NAMED} more)" if len(due) > _NAMED else ""
    return (
        f"contexts: due — the batch changes {named}{more}; run "
        "`scripts/promotion-gate.sh contexts` with an admin-read token before merging"
    )
