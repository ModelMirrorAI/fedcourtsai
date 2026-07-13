"""Latch a run's agent-feedback roll-up onto the long-lived tracking issue.

The predict/evaluate ``collect`` job rolls each run's agent flags into a comment
(rendered by :func:`fedcourtsai.collect.render_feedback_comment`) and latches it
onto ONE long-lived ``agent-feedback`` issue, so a note survives even a fully
failed run that opens no PR. This module is that latch, lifted out of inline
workflow bash so the find-or-create and the once-only idempotency are unit-tested
rather than only lint-checked for shape — the same motivation as
:mod:`fedcourtsai.authz`. The ``gh`` side effects sit behind an injectable
:data:`GhRunner` seam so tests assert on the issued commands without a network
call, mirroring :class:`fedcourtsai.pipeline.runner.AgenticRunner`'s
``command_runner``.

The job invokes this with the ambient ``GITHUB_TOKEN`` (job-scoped
``issues: write``), never its contents-write App token: latching needs no
cross-workflow trigger because ``agent-feedback`` is a non-triggering label.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Iterable, Mapping, Sequence

# The non-triggering label (no ``run:*`` workflow keys on it) the single long-lived
# issue carries, with the appearance used when this job first creates it.
LABEL = "agent-feedback"
_LABEL_COLOR = "fbca04"
_LABEL_DESCRIPTION = "Long-lived agent feedback flags (predict/evaluate collect roll-up)"
_ISSUE_TITLE = "Agent feedback"
_ISSUE_BODY = (
    "Long-lived tracking issue for the agent flags the predict/evaluate `collect` "
    "job rolls up. Each run that surfaces a flag adds a comment below; triage them "
    "and close the issue only if you retire the channel. See docs/data-pipeline.md "
    "(the `flags.json` channel) and docs/pipeline.md."
)

# Runs a ``gh`` argv and returns its stdout, raising on a non-zero exit. Injected
# so the latch can be tested without invoking gh or hitting the network.
GhRunner = Callable[[Sequence[str]], str]


def already_posted(existing_bodies: Iterable[str], marker: str) -> bool:
    """Whether this run's note is already on the issue (its marker is present).

    Pure: mirrors the workflow's prior ``grep -qF "$marker"`` substring check, so a
    ``collect`` re-run posts each run's roll-up exactly once.
    """
    return any(marker in body for body in existing_bodies)


def choose_feedback_issue(issues: Sequence[Mapping[str, object]]) -> int | None:
    """The open ``agent-feedback`` issue to reuse, or ``None`` to create one.

    Pure: mirrors the workflow's prior ``.[0].number`` — reuse the first open issue
    under the label, else signal a create. There is normally exactly one.
    """
    if not issues:
        return None
    number = issues[0].get("number")
    return number if isinstance(number, int) else None


def _gh(argv: Sequence[str]) -> str:
    """Default :data:`GhRunner`: run ``gh`` and return stdout, raising on failure."""
    result = subprocess.run(list(argv), capture_output=True, text=True, check=True)
    return result.stdout


def post_agent_feedback(comment: str, repo: str, *, runner: GhRunner = _gh) -> str:
    """Latch one run's flag roll-up onto the long-lived agent-feedback issue.

    ``comment`` is the rendered roll-up whose first line is the per-run marker
    (see :func:`fedcourtsai.collect.render_feedback_comment`); an empty/blank one
    means the run raised no flags and nothing is posted. Ensures the non-triggering
    label exists, finds-or-creates the single issue, and posts the comment once —
    skipping if its marker already appears on the issue. Returns a one-line status
    for the workflow log. The ``runner`` seam lets tests assert on the gh commands
    without a network call.
    """
    if not comment.strip():
        return "no agent feedback to post"
    marker = comment.splitlines()[0]
    # Ensure the NON-triggering label exists so the first run does not fail.
    runner(
        [
            "gh",
            "label",
            "create",
            LABEL,
            "--repo",
            repo,
            "--force",
            "--color",
            _LABEL_COLOR,
            "--description",
            _LABEL_DESCRIPTION,
        ]
    )
    issues = json.loads(
        runner(
            [
                "gh",
                "issue",
                "list",
                "--repo",
                repo,
                "--label",
                LABEL,
                "--state",
                "open",
                "--json",
                "number",
            ]
        )
        or "[]"
    )
    number = choose_feedback_issue(issues)
    if number is None:
        url = runner(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                _ISSUE_TITLE,
                "--label",
                LABEL,
                "--body",
                _ISSUE_BODY,
            ]
        ).strip()
        number = int(url.rstrip("/").rsplit("/", 1)[-1])
    view = json.loads(
        runner(["gh", "issue", "view", str(number), "--repo", repo, "--json", "comments"]) or "{}"
    )
    bodies = [str(c.get("body", "")) for c in view.get("comments", [])]
    if already_posted(bodies, marker):
        return f"agent feedback already on #{number}"
    runner(["gh", "issue", "comment", str(number), "--repo", repo, "--body", comment])
    return f"posted agent feedback to #{number}"
