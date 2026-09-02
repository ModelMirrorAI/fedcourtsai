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
``command_runner``. That seam is also where the bounded retry and the per-call
timeout live (:func:`_gh`), so every ``gh`` call this module makes — and every
one made by the commands built on it — is bounded in one tested place rather
than at each site.

The job invokes this with the ambient ``GITHUB_TOKEN`` (job-scoped
``issues: write``), never its contents-write App token: latching needs no
cross-workflow trigger because ``agent-feedback`` is a non-triggering label.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Mapping, Sequence

# The non-triggering label (no workflow keys on ``issues: labeled``) the single long-lived
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

# Sleeps between attempts. A parameter of :func:`_gh` rather than a bare
# ``time.sleep`` call so the retry's timing is asserted, not waited out, in tests.
Sleeper = Callable[[float], None]

# The default runner's bounds, mirroring ``scripts/gh_retry.sh``: three attempts,
# each capped at 30s, with a 5s-per-attempt linear backoff (5s then 10s), so one
# call costs at most 105s. Kept identical to the shell wrapper because the hazard
# is identical — a step whose ``timeout-minutes`` admits a wrapped shell call
# admits one of these too.
_GH_ATTEMPTS = 3
_GH_TIMEOUT_SECONDS = 30
_GH_BACKOFF_SECONDS = 5


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


def _gh(argv: Sequence[str], *, sleeper: Sleeper = time.sleep) -> str:
    """Default :data:`GhRunner`: run ``gh`` and return stdout, raising on failure.

    Bounded as ``scripts/gh_retry.sh`` bounds the workflows' shell-side ``gh``
    calls — the same three attempts, the same 30s cap on each — and for the same
    two reasons. A transient 5xx costs something the run never earned: this seam
    carries the plan report every non-empty predict/evaluate round posts before
    the review hold, plus the collect job's stall and secret-scan reports. What
    a blip costs differs by site. At the plan report the step runs under ``set
    -euo pipefail``, so a failure is loud and the *round* is what is lost, to a
    re-trigger; at the collect reports the loss is the record itself — the only
    durable notice that a run stalled or a scan hit. And ``gh`` sets no
    client-side request timeout, so a stalled connect against a degraded API
    would hang to the job's own kill with nothing written; the per-attempt
    ``timeout`` is what bounds that.

    Retrying changes when a call fails, never what its failure means: exhaustion
    re-raises the last attempt's error, so a report that never lands still fails
    its step as loudly as an unretried call would. What is bought is that a blip
    does not decide it. Both retried failure modes are subclasses of
    :class:`subprocess.SubprocessError`; the non-zero exit still surfaces as
    :class:`subprocess.CalledProcessError` with its captured streams attached.
    An :class:`OSError` — ``gh`` itself missing or unexecutable — is *not*
    retried, unlike the shell wrapper's blanket non-zero: that fault is
    deterministic and three attempts would only delay it.

    What the retry cannot make safe. ``gh issue comment`` and ``gh issue
    create`` are not idempotent, so a write that lands server-side and is then
    cut at the timeout is re-sent on the next attempt — the marker checks in
    this module run *before* the write and cannot see a re-send inside here. A
    duplicated comment is one repeated note; a duplicated create is worse, since
    a second open issue under the label makes :func:`choose_feedback_issue`
    settle on whichever ``gh`` lists first and strand the other's history. It is
    accepted for the same reason the shell wrapper accepts it: a write that
    takes more than 30s *and* still succeeds is far rarer than the transient
    failure being absorbed, and the create runs only until the one long-lived
    issue exists.

    Output is returned only from the attempt that succeeded, and stderr stays
    captured (callers parse stdout as JSON or as a created issue's URL). The
    annotations go to this process's stderr, where they reach the job log
    without contaminating what a *step* captures from stdout, and name only the
    first three argv words — so an issue body passed as an argument never lands
    in an annotation.

    ``sleeper`` is a seam for tests; production never passes it.
    """
    command = list(argv)
    what = " ".join(command[:3])
    attempt = 1
    while True:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=_GH_TIMEOUT_SECONDS,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt >= _GH_ATTEMPTS:
                print(f"::error::{what} failed after {_GH_ATTEMPTS} attempts", file=sys.stderr)
                raise
            print(
                f"::warning::{what} failed (attempt {attempt}/{_GH_ATTEMPTS}) — retrying",
                file=sys.stderr,
            )
            sleeper(attempt * _GH_BACKOFF_SECONDS)
            attempt += 1
        else:
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


def post_once(
    *,
    repo: str,
    issue: int,
    marker: str,
    body: str,
    runner: GhRunner = _gh,
) -> str:
    """Comment on ``issue`` unless ``marker`` already appears on it.

    The general form of the agent-feedback latch, for the collect job's stall and
    secret-scan reports. Those are posted by a step that reruns whenever the
    collect job does — and rerunning collect is the documented recovery for a
    transfer failure, so without this every recovery attempt would add another
    copy of the same warning to the issue, burying the signal it exists
    to raise.

    The marker is prepended rather than embedded by the renderers: the
    secret-scan body is *appended to* once per branch, so a marker inside the
    rendered content would repeat. Keeping it here also keeps both reports'
    idempotency in one tested place instead of two.
    """
    view = json.loads(
        runner(["gh", "issue", "view", str(issue), "--repo", repo, "--json", "comments"]) or "{}"
    )
    bodies = [str(c.get("body", "")) for c in view.get("comments", [])]
    if already_posted(bodies, marker):
        return f"already posted on #{issue}"
    runner(["gh", "issue", "comment", str(issue), "--repo", repo, "--body", f"{marker}\n{body}"])
    return f"posted to #{issue}"
