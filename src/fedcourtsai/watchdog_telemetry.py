"""The codex watchdog's off-runner record: one issue comment per cell, PATCHed live.

A wedged codex cell holds its engine step ``in_progress`` until the *job* cap
cancels the runner, and a cancelled job runs none of its ``always()`` tail and has
its logs dropped by GitHub. So every runner-local channel the watchdog has — the
diagnostics bundle under ``WATCHDOG_DIR``, the disarm step that publishes it, the
step summary, the job log — is erased by exactly the failure it documents, and
nothing afterwards says whether the watchdog even fired. Evidence about a runner
that may be cancelled has to leave the runner *while the runner is still
running*, which is what this module opens: a long-lived ``codex-watchdog``
tracking issue carrying one comment per cell, created here before the agent
starts and then PATCHed in place by ``scripts/codex-watchdog.sh`` itself as it
passes each state.

Built on :mod:`fedcourtsai.agent_feedback`: the same bounded ``gh`` runner (so
this channel is capped exactly as every other issue write is), the same
find-or-create over a **non-triggering** label, and the same hidden-marker test.
The marker keys a comment to one cell of one run, so a re-dispatch of the same
run resets that cell's record rather than stacking a second copy, and the issue
stays one readable row per cell. Closing the issue rotates it: the find-or-create
reuses the first *open* one and opens a fresh issue when there is none.

What may be written here is stricter than the published bundle's rule, not
merely equal to it. The bundle rides a cell artifact and so carries shapes and
metadata; this comment is on a **public issue** that outlives every run, so it
carries only timestamps, phase names, pid numbers, counts and the configured
deadline — never argv, never a file listing, never any content the cell read.
The renderers below are the whole of what a body can say, and the watchdog
composes its own lines from its own variables for the same reason.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta

from .agent_feedback import GhRunner, _gh, find_or_create_issue, marker_head

# The non-triggering label (no workflow keys on ``issues: labeled``) the single
# long-lived issue carries, with the appearance used when a cell first creates it.
LABEL = "codex-watchdog"
_LABEL_COLOR = "b60205"
_LABEL_DESCRIPTION = "Codex cell watchdog telemetry (armed records and live heartbeats)"
_ISSUE_TITLE = "Codex watchdog telemetry"
_ISSUE_BODY = (
    "Long-lived tracking issue for the codex cell watchdog "
    "(`scripts/codex-watchdog.sh`). Each codex cell records itself here as one "
    "comment: armed before the engine starts, then updated in place as the "
    "watchdog passes each state, so a wedge that cancels the runner — which "
    "drops the job's logs and skips its capture tail — cannot erase the account "
    "of itself. A cell that finished cleanly collapses to a single "
    "armed/disarmed line. **Close this issue to rotate it** — the next cell "
    "opens a fresh one, and rotating keeps every cell's own row inside the "
    "bounded window each check-in searches. See *Graceful degradation on "
    "limits* in docs/pipeline.md."
)

#: Keys one comment to one cell of one run. A hidden HTML comment, so the body
#: reads as prose while the find-or-reset test has something exact to match.
MARKER_TEMPLATE = "<!-- codex-watchdog: {run_id}/{court}/{docket}/{event_id}/{actor} -->"

#: The visible second line, so a maintainer reading the issue can tell the cells
#: apart without expanding the HTML comment above it.
_TITLE_TEMPLATE = "### codex watchdog · {court}/{docket} · {event_id} · {actor} · run `{run_id}`"

# How far back the marker is looked for, and — the part that matters — from
# which end. The issue accumulates one comment per codex cell per round, so an
# unbounded listing would grow into a per-check-in cost that a wedged runner is
# the worst place to pay. But the endpoint returns comments oldest-first and
# takes no direction, so a page-count bound *alone* searches the wrong end: once
# the issue outgrows it, every cell's own comment sits past the last page, the
# disarm cannot find the row the arm just wrote, and each cell ends up with two
# rows — the live one never collapsed, the closing one reading `armed_at=unknown`.
# The issue would then grow at twice the rate the bound was meant to cap.
#
# `since` moves the window to the recent end instead, and the page cap bounds
# the cost inside it. A window of days rather than hours because a re-dispatch
# of the same run is the only thing that legitimately looks for an older row;
# one older than the window posts a fresh comment, which costs one duplicate row
# and never a missed record.
_COMMENT_PAGE_SIZE = 100
_COMMENT_PAGES = 3
_COMMENT_WINDOW = timedelta(days=7)

#: How much of a candidate body the marker test may read: the two-line head this
#: module guarantees. A record quoted into a triage reply must not decide which
#: comment the next arming resets.
_MARKER_LINES = 2

_ARMED_AT = re.compile(r"armed_at=(\S+)")


def checkin_marker(*, run_id: str, court: str, docket: str, event_id: str, actor: str) -> str:
    """The hidden key identifying one cell's comment on the telemetry issue."""
    return MARKER_TEMPLATE.format(
        run_id=run_id, court=court, docket=docket, event_id=event_id, actor=actor
    )


def checkin_head(*, run_id: str, court: str, docket: str, event_id: str, actor: str) -> str:
    """The two lines every version of this cell's comment opens with.

    The watchdog PATCHes the *whole* body each time, so whatever it composes has
    to reproduce this head or the next find-by-marker would miss the comment it
    just rewrote. It never builds the head itself: the arm step hands it the
    armed body verbatim to append to, so the marker format has one spelling.
    """
    marker = checkin_marker(
        run_id=run_id, court=court, docket=docket, event_id=event_id, actor=actor
    )
    title = _TITLE_TEMPLATE.format(
        run_id=run_id, court=court, docket=docket, event_id=event_id, actor=actor
    )
    return f"{marker}\n{title}"


def arm_times(deadline_s: int, now: datetime | None = None) -> tuple[str, str]:
    """``(armed_at, fire_eta)`` as UTC stamps, in the watchdog's own format.

    The ETA is the whole point of writing the deadline down: a maintainer reading
    the issue mid-round can tell a cell that is still inside its window from one
    that is past it, without recomputing the arithmetic the arm step did.
    """
    started = now or datetime.now(UTC)
    fires = started + timedelta(seconds=deadline_s)
    return _stamp(started), _stamp(fires)


def _stamp(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _since(now: datetime | None) -> str:
    """The recent end of the issue, as the comment listing's ``since`` bound."""
    return _stamp((now or datetime.now(UTC)) - _COMMENT_WINDOW)


def armed_body(head: str, *, armed_at: str, fire_eta: str, deadline_s: int, run_url: str) -> str:
    """The record the arm step writes, before a single model token is spent.

    Its existence is half the evidence: a cell whose comment says only this, on a
    run that never came back, is a wedge the watchdog did not convert — which is
    a different fault from one it converted and reported, and the only thing that
    tells the two apart is a record written before either could happen.
    """
    lines = [
        head,
        f"armed_at={armed_at} deadline_s={deadline_s} fire_eta={fire_eta}",
    ]
    if run_url:
        lines.append(f"run: {run_url}")
    return "\n".join(lines)


def disarmed_body(
    head: str, *, prior: str, disarmed_at: str, conclusion: str, healthy: bool
) -> str:
    """The final record: collapsed on a healthy round, appended to on any other.

    A round where nothing fired has nothing worth keeping — and keeping it would
    bury the rounds that do behind hundreds of uneventful heartbeat logs — so the
    body collapses to the one line that says the guard was armed and stood down.
    Where the watchdog reached its deadline, the live record it PATCHed is what a
    maintainer came for, so the conclusion is appended to it rather than
    replacing it.
    """
    if healthy:
        found = _ARMED_AT.search(prior)
        armed_at = found.group(1) if found else "unknown"
        return (
            f"{head}\narmed_at={armed_at} disarmed_at={disarmed_at} "
            f"conclusion={conclusion} — stood down cleanly; the deadline was never reached."
        )
    body = prior or head
    return f"{body}\n[{disarmed_at}] disarmed: conclusion={conclusion}"


def _authored_by_app(comment: Mapping[str, object]) -> bool:
    """Whether an App wrote this comment, rather than any account that can type.

    This repository is public, so anyone with a GitHub account can comment on the
    telemetry issue — and every part of a marker (run id, case, event, actor) is
    derivable from the issue's own visible history and the committed ledger. A
    marker test alone would therefore let a stranger *pre-post* a future cell's
    marker and have the arming reset, and the watchdog then beat into, a comment
    they keep the ability to edit: a forgeable account of a hang, on the one
    channel that exists because every other account gets destroyed. Requiring an
    App author means a planted marker is passed over and a fresh comment written
    instead, which costs one ignorable row and keeps the record ours.
    """
    user = comment.get("user")
    return isinstance(user, Mapping) and user.get("type") == "Bot"


def _comment_id(comment: Mapping[str, object]) -> int | None:
    """The comment's numeric id, or ``None`` if the payload is not shaped like one."""
    identifier = comment.get("id")
    return identifier if isinstance(identifier, int) else None


def _find_marked(
    comments: Sequence[Mapping[str, object]], marker: str
) -> Mapping[str, object] | None:
    """This cell's existing comment: App-authored, and carrying the marker.

    The marker test is bounded to each body's leading lines
    (:func:`~fedcourtsai.agent_feedback.marker_head`), as the digests' is: every
    body this module writes is harness-composed, but a maintainer triaging a
    wedge naturally quotes a record into a reply, and a whole-body search would
    then let that reply be the row the next arming resets.
    """
    for comment in comments:
        if not _authored_by_app(comment) or _comment_id(comment) is None:
            continue
        if marker in marker_head(str(comment.get("body", "")), _MARKER_LINES):
            return comment
    return None


def _locate(
    repo: str, issue: int, marker: str, since: str, runner: GhRunner
) -> Mapping[str, object] | None:
    """This cell's comment on the issue, searched over the recent window only.

    ``since`` is what makes the page bound meaningful — see the constants above:
    the endpoint pages oldest-first, so a bound applied without it searches the
    end of the issue this cell's comment is never at.
    """
    for page in range(1, _COMMENT_PAGES + 1):
        raw = runner(
            [
                "gh",
                "api",
                f"repos/{repo}/issues/{issue}/comments",
                "--method",
                "GET",
                "-f",
                f"since={since}",
                "-F",
                f"per_page={_COMMENT_PAGE_SIZE}",
                "-F",
                f"page={page}",
            ]
        )
        comments = json.loads(raw or "[]")
        found = _find_marked(comments, marker)
        if found is not None:
            return found
        if len(comments) < _COMMENT_PAGE_SIZE:
            return None
    return None


def _write(
    repo: str, issue: int, existing: Mapping[str, object] | None, body: str, runner: GhRunner
) -> str:
    """Reset this cell's comment where it exists, else create it. Returns its API URL.

    The API URL, not the browser one: it is what the detached watchdog PATCHes,
    and deriving it on the shell side would be one more format to keep in step.
    """
    if existing is None:
        written = runner(
            [
                "gh",
                "api",
                f"repos/{repo}/issues/{issue}/comments",
                "--method",
                "POST",
                "-f",
                f"body={body}",
            ]
        )
    else:
        written = runner(
            [
                "gh",
                "api",
                f"repos/{repo}/issues/comments/{_comment_id(existing)}",
                "--method",
                "PATCH",
                "-f",
                f"body={body}",
            ]
        )
    return str(json.loads(written or "{}").get("url", ""))


def _issue_for(repo: str, runner: GhRunner) -> int:
    return find_or_create_issue(
        repo=repo,
        label=LABEL,
        label_color=_LABEL_COLOR,
        label_description=_LABEL_DESCRIPTION,
        title=_ISSUE_TITLE,
        body=_ISSUE_BODY,
        runner=runner,
    )


def arm_checkin(  # noqa: PLR0913 - the cell's five identifiers are five of these
    *,
    repo: str,
    run_id: str,
    court: str,
    docket: str,
    event_id: str,
    actor: str,
    deadline_s: int,
    run_url: str = "",
    now: datetime | None = None,
    runner: GhRunner = _gh,
) -> tuple[str, str]:
    """Record this cell as armed, returning ``(comment API URL, the body written)``.

    Both halves go to the detached watchdog: the URL is what it PATCHes, and the
    body is the **base** it appends each state to. The whole body and not just
    its head, because the watchdog PATCHes what it has composed — so a base
    trimmed to the marker would have the first heartbeat erase the arming time,
    the fire ETA and the run link, which are exactly what a reader of a run that
    never came back has to go on.
    """
    head = checkin_head(run_id=run_id, court=court, docket=docket, event_id=event_id, actor=actor)
    marker = head.splitlines()[0]
    armed_at, fire_eta = arm_times(deadline_s, now)
    issue = _issue_for(repo, runner)
    existing = _locate(repo, issue, marker, _since(now), runner)
    body = armed_body(
        head, armed_at=armed_at, fire_eta=fire_eta, deadline_s=deadline_s, run_url=run_url
    )
    return _write(repo, issue, existing, body, runner), body


def disarm_checkin(  # noqa: PLR0913 - the cell's five identifiers are five of these
    *,
    repo: str,
    run_id: str,
    court: str,
    docket: str,
    event_id: str,
    actor: str,
    conclusion: str,
    healthy: bool,
    now: datetime | None = None,
    runner: GhRunner = _gh,
) -> tuple[str, str]:
    """Close this cell's record out with the engine step's conclusion.

    Returns ``(comment API URL, the body written)``, symmetrically with
    :func:`arm_checkin`; nothing consumes the second half here, since the
    watchdog it would have fed has just been stood down.
    """
    head = checkin_head(run_id=run_id, court=court, docket=docket, event_id=event_id, actor=actor)
    marker = head.splitlines()[0]
    issue = _issue_for(repo, runner)
    existing = _locate(repo, issue, marker, _since(now), runner)
    prior = str(existing.get("body", "")) if existing is not None else ""
    body = disarmed_body(
        head,
        prior=prior,
        disarmed_at=_stamp(now or datetime.now(UTC)),
        conclusion=conclusion,
        healthy=healthy,
    )
    return _write(repo, issue, existing, body, runner), body


__all__ = [
    "LABEL",
    "MARKER_TEMPLATE",
    "arm_checkin",
    "arm_times",
    "armed_body",
    "checkin_head",
    "checkin_marker",
    "disarm_checkin",
    "disarmed_body",
]
