"""The promotion train: one decision per tick about the staging→main promotion.

`promotion-prep` runs hourly, and on a maintainer's dispatch, and asks this
module what to do next. The answer is a single :class:`TrainStep`, derived only
from what the workflow read — whether the tick is that dispatch, the open PRs
into `main`, the existing `promote/*` branches and their heads, staging's
relation to `main`, the train's own paid dispatches today, and, for
the one open candidate, its PR, integration runs, reviews, check runs and the
gate stages read live — so the rule is testable without the Actions API and
the workflow only routes on the answer.

A **candidate** is a frozen release branch, ``promote/<UTC date>`` (``-2``,
``-3`` … when the date is taken), cut at staging's tip and never moved again,
with a PR from it into `main`. Freezing the head is the point: staging keeps
taking merges and syncs while the maintainer takes hours or days to read the
batch, and neither the integration evidence nor the approval — both bound to
one SHA — is invalidated by them. The steps:

====================  ================================================  =========================
action                when                                              does
====================  ================================================  =========================
``cut``               the tick is a dispatch; no open promotion PR;     create the branch at the
                      `main` changed nothing since its merge-base with  staging tip read, open a
                      staging outside the writer lanes and staging      draft PR into `main`
                      holds `main`'s last promotion merge (staging is
                      synced); staging changed something since that
                      merge-base; no ``promote/`` branch already sits
                      at that tip
``dispatch_gate``     no dispatched integration-test run of any kind    dispatch integration-test
                      at the head and ref, the registry gate passes,    ``gate`` (``offline-gate``
                      and today's paid-dispatch cap is not reached      under the waiver label)
``mark_ready``        green evidence at the head and the PR is a        mark ready, request the
                      draft the train has not marked before             approvers' review; the
                                                                        body edit re-fires CI
``refire_gate``       approved at the head, quiescent, registry clean,  edit the body, which
                      freshness passes, every other required check      re-runs ci.yml's
                      green, ``promotion-gate`` red or missing, and     ``promotion-gate``
                      fewer than :data:`REFIRE_CAP` re-fires failed
``merge``             approved at the head with no changes requested,   merge commit, pinned to
                      mergeable, quiescent now, registry clean, every   the head SHA (dev App)
                      required check green
``wait``              something will change without anyone acting       nothing (body refresh)
``report``            a human has to act                                nothing (body refresh)
====================  ================================================  =========================

Green evidence is a green ``gate`` run at the head and ref (an ``offline-gate``
one under the ``promote:skip-engine-smoke`` label), or the promotion gate's own
freshness stage passing there — per-scenario runs a maintainer dispatched
count. Everything unreadable resolves to ``wait``, never to an act. The paid
suite runs at most once per candidate: the dispatch is refused while *any*
dispatched integration run sits at the head, whatever its title, so a renamed
title can never read as "no run yet"; a failed or unrecognised run is reported
and never re-dispatched, and a daily cap bounds the train's paid dispatches
across candidates. Candidate branches are never deleted, so a branch already
at the staging tip means that tip was cut before: a candidate the maintainer
closed unmerged is not re-cut, and the next one waits for staging to move
(reopening the PR, or opening one from the branch, puts it back on the train).
A hand-opened ``staging`` → `main` PR makes the train stand aside, so there is
one promotion in flight at a time.

Only a dispatch cuts. The maintainer decides when a batch closes; the hourly
schedule carries a candidate from there to the merge and, with none open,
reports whether one is ready to cut. A dispatch whose cut cannot happen — a
candidate already open, the last promotion not yet synced, nothing to promote —
does what a scheduled tick would and names the reason; the request is not
remembered, so it is dispatched again once the reason has cleared.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .promotion_body import BEGIN, END, READY_MARKER

#: The train's configuration file, under the config root (``config/``).
CONFIG_FILENAME = "promotion-train.yaml"

#: The dispatch that asks the train to cut: the batch closes when the
#: maintainer says so, not whenever staging moves.
CUT_COMMAND = "gh workflow run promotion-prep.yml --ref main"

#: Every candidate branch lives under this prefix.
BRANCH_PREFIX = "promote/"

#: The paths `main` takes directly from the deterministic writers and the bot
#: lanes, never through staging. `main` moves on these every few hours, so the
#: cut cannot wait for `main` to be an ancestor of staging; what it waits for is
#: anything *else* `main` holds that staging lacks — after a promotion, the
#: merge itself and the record commit's registry and freeze-record stamps —
#: which only a sync brings.
WRITER_LANE_PATHS = ("data/", "metrics/", "corpus/corpus.db.ref")

#: The only branch names the train cuts and acts on: the UTC date, and a
#: numeric suffix from 2 when that date is already taken. ASCII digits only.
BRANCH_NAME = re.compile(r"promote/[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-(?:[2-9]|[1-9][0-9]+))?")

#: The integration-test run titles that are whole-suite promotion evidence.
#: A `promote/*` dispatch resolves the `staging` environment, so the titles are
#: the staging branch's; the branch itself is pinned by the run's head_branch.
GATE_TITLE = "integration-test: gate @ staging"
OFFLINE_GATE_TITLE = "integration-test: offline-gate @ staging"

#: The label under which the promotion gate accepts an `offline-gate` run, and
#: under which the train dispatches that token-free suite instead of `gate`.
WAIVER_LABEL = "promote:skip-engine-smoke"

#: The required check the train may re-fire by a body edit.
PROMOTION_GATE_CHECK = "promotion-gate"

#: How many ``promotion-gate`` failures after the approval the train re-fires
#: through before it reports instead: a check that keeps failing with every
#: other condition holding needs a person, not another CI run.
REFIRE_CAP = 3

#: The bot login the train's integration dispatches run as.
DISPATCH_BOT = "fedcourtsai-dispatch[bot]"

#: Logins the approver list may never name: an approval from one would land
#: code on `main` without the maintainer.
FORBIDDEN_APPROVERS = frozenset({"modelmirror-agent"})

#: The app every counted check run must come from.
_ACTIONS_APP = "github-actions"

_IN_FLIGHT = frozenset({"queued", "in_progress", "waiting", "pending", "requested"})
_HUMAN_LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
_SHA = re.compile(r"[0-9a-f]{40}")


class TrainConfigError(ValueError):
    """The train's configuration is missing or malformed; the train acts on nothing."""


class TrainConfig(BaseModel):
    """``config/promotion-train.yaml``: whose approval the train merges on, on
    which required checks, and how many paid gate suites it may start a day.

    ``approvers`` are the GitHub logins whose approving review of a candidate's
    head is the merge decision. The dev App bypasses `main`'s approval rule, so
    this list — not the ruleset — is what binds the train's merge to a person.
    ``required_checks`` are the check contexts `main`'s ruleset requires; the
    platform enforces them on the merge too, and the train waits for them so it
    never asks for a merge it knows will be refused.
    ``max_gate_dispatches_per_day`` caps the integration suites the train
    starts per UTC day, across candidates: unattended spend, bounded.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    approvers: tuple[str, ...]
    required_checks: tuple[str, ...]
    max_gate_dispatches_per_day: int = Field(ge=1, le=4)

    @field_validator("approvers")
    @classmethod
    def _logins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("names no approver: the train could never merge")
        for login in value:
            if not _HUMAN_LOGIN.fullmatch(login):
                raise ValueError(f"{login!r} is not a GitHub user login")
            if login.casefold() in FORBIDDEN_APPROVERS:
                raise ValueError(f"{login!r} may never approve a promotion")
        folded = [login.casefold() for login in value]
        if len(set(folded)) != len(folded):
            raise ValueError("lists a login twice")
        return value

    @field_validator("required_checks")
    @classmethod
    def _checks(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if PROMOTION_GATE_CHECK not in value:
            raise ValueError(f"must require {PROMOTION_GATE_CHECK!r}: it is the gate")
        if len(set(value)) != len(value):
            raise ValueError("lists a check twice")
        return value

    def is_approver(self, login: str) -> bool:
        """Whether ``login`` is a listed approver (logins compare case-insensitively)."""
        folded = login.casefold()
        return any(approver.casefold() == folded for approver in self.approvers)


def load_train_config(path: Path) -> TrainConfig:
    """Read and validate the configuration; raise :class:`TrainConfigError`."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise TrainConfigError(f"cannot read {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise TrainConfigError(f"{path} is not a mapping")
    try:
        return TrainConfig.model_validate(raw)
    except ValueError as exc:
        raise TrainConfigError(f"{path}: {exc}") from exc


class TrainAction(StrEnum):
    """What the tick does."""

    CUT = "cut"
    DISPATCH_GATE = "dispatch_gate"
    MARK_READY = "mark_ready"
    REFIRE_GATE = "refire_gate"
    MERGE = "merge"
    WAIT = "wait"
    REPORT = "report"


class TrainStep(BaseModel):
    """One tick's answer, with the line the PR body and the run summary carry."""

    action: TrainAction
    reason: str
    pr: int | None = None
    ref: str | None = None
    sha: str | None = None
    #: The branch a ``cut`` creates.
    branch: str | None = None
    #: Whose review a ``mark_ready`` requests: the configured approvers.
    reviewers: tuple[str, ...] = ()
    #: The integration suite a ``dispatch_gate`` starts: ``gate``, or
    #: ``offline-gate`` under the waiver label.
    scenario: str | None = None


class Candidate(BaseModel):
    """The one open promotion candidate."""

    number: int
    ref: str
    sha: str
    draft: bool
    body: str = ""
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class Observed:
    """What the tick read. ``None`` anywhere means the read failed."""

    repo: str
    now: datetime
    open_pulls: Sequence[Mapping[str, Any]] | None
    #: The existing ``promote/`` branches as ``(name, head SHA)``.
    branches: Sequence[tuple[str, str]] | None = None
    staging_sha: str | None = None
    #: The paths `main` changed since its merge-base with staging.
    main_ahead_paths: Sequence[str] | None = None
    #: Whether staging changed anything since that merge-base.
    staging_differs_from_main: bool | None = None
    #: Whether staging contains the last promotion merge on `main`'s
    #: first-parent chain (true when `main` holds none).
    last_promotion_synced: bool | None = None
    #: integration-test dispatches of the current UTC day (REST runs list).
    recent_dispatches: Sequence[Mapping[str, Any]] | None = None
    #: Whether this tick is a maintainer's dispatch of `promotion-prep`: the
    #: only tick that may cut. A scheduled tick advances an open candidate and
    #: reports a batch ready to cut, never cuts one.
    cut_requested: bool = False
    # The candidate's own reads; unused when no candidate is open.
    head_on_staging: bool | None = None
    #: The candidate PR as `GET pulls/{n}` returns it (for ``mergeable``).
    pull: Mapping[str, Any] | None = None
    runs: Sequence[Mapping[str, Any]] | None = None
    reviews: Sequence[Mapping[str, Any]] | None = None
    #: Every check run at the head (``filter=all``), re-runs included.
    check_runs: Sequence[Mapping[str, Any]] | None = None
    quiescent: bool | None = None
    registry_ok: bool | None = None
    #: The promotion gate's freshness stage at the head and ref, read live
    #: (under the waiver label when the candidate carries it).
    freshness_ok: bool | None = None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _same_repo_into_main(pull: Mapping[str, Any], repo: str) -> bool:
    head = _mapping(pull.get("head"))
    return (
        _mapping(pull.get("base")).get("ref") == "main"
        and _mapping(head.get("repo")).get("full_name") == repo
    )


def _head_ref(pull: Mapping[str, Any]) -> str:
    ref = _mapping(pull.get("head")).get("ref")
    return ref if isinstance(ref, str) else ""


def _head_sha(pull: Mapping[str, Any]) -> str:
    sha = _mapping(pull.get("head")).get("sha")
    return sha if isinstance(sha, str) else ""


def is_train_branch(ref: str) -> bool:
    """Whether ``ref`` is a branch name the train cuts (case-sensitive, whole-name)."""
    return BRANCH_NAME.fullmatch(ref) is not None


def promotion_pulls(pulls: Iterable[Mapping[str, Any]], *, repo: str) -> list[Mapping[str, Any]]:
    """The open same-repo PRs into `main` whose head is `staging` or under `promote/`."""
    return [
        pull
        for pull in pulls
        if pull.get("state", "open") == "open"
        and _same_repo_into_main(pull, repo)
        and (_head_ref(pull) == "staging" or _head_ref(pull).startswith(BRANCH_PREFIX))
    ]


def marked_ready(body: str) -> bool:
    """Whether the train's ready marker sits in ``body`` outside the generated block.

    The block quotes feature PRs' text, so a marker inside it is not the
    train's; :func:`fedcourtsai.promotion_body.render` defuses one there too.
    """
    start = body.find(BEGIN)
    end = body.find(END, start + len(BEGIN)) if start != -1 else -1
    outside = body if start == -1 or end == -1 else body[:start] + body[end + len(END) :]
    return READY_MARKER in outside


def find_candidate(
    pulls: Iterable[Mapping[str, Any]], *, repo: str
) -> tuple[Candidate | None, str | None]:
    """The one open candidate, or why there is none to act on.

    Returns ``(candidate, None)`` for exactly one open same-repo PR from a
    train-named branch; ``(None, None)`` when no promotion is open at all; and
    ``(None, reason)`` when one is open that the train must not act on — a
    hand-opened `staging` PR, a `promote/` head the train would not have cut,
    or more than one candidate.
    """
    open_promotions = promotion_pulls(pulls, repo=repo)
    if not open_promotions:
        return None, None
    staging = [pull for pull in open_promotions if _head_ref(pull) == "staging"]
    if staging:
        numbers = ", ".join(f"#{pull.get('number')}" for pull in staging)
        return None, (
            f"a hand-opened staging → main promotion ({numbers}) is open; the train "
            "stands aside until it merges or closes"
        )
    malformed = [pull for pull in open_promotions if not is_train_branch(_head_ref(pull))]
    if malformed:
        names = ", ".join(f"#{pull.get('number')} ({_head_ref(pull)})" for pull in malformed)
        return None, f"{names}: not a branch name the train cuts; the train stands aside"
    if len(open_promotions) > 1:
        numbers = ", ".join(f"#{pull.get('number')}" for pull in open_promotions)
        return None, f"more than one open candidate ({numbers}); the train stands aside"
    (pull,) = open_promotions
    number = pull.get("number")
    sha = _head_sha(pull)
    if not isinstance(number, int) or not _SHA.fullmatch(sha):
        return None, "the open candidate's number or head SHA could not be read"
    labels = tuple(str(_mapping(label).get("name")) for label in pull.get("labels") or [] if label)
    body = pull.get("body")
    return (
        Candidate(
            number=number,
            ref=_head_ref(pull),
            sha=sha,
            draft=pull.get("draft") is True,
            body=body if isinstance(body, str) else "",
            labels=labels,
        ),
        None,
    )


def next_branch_name(now: datetime, existing: Iterable[str]) -> str:
    """``promote/<UTC date>``, or the first free ``-N`` suffix from 2 when taken."""
    base = f"{BRANCH_PREFIX}{now.strftime('%Y-%m-%d')}"
    taken = set(existing)
    if base not in taken:
        return base
    suffix = 2
    while f"{base}-{suffix}" in taken:
        suffix += 1
    return f"{base}-{suffix}"


class GateEvidence(StrEnum):
    """Where the candidate's integration runs stand."""

    NONE = "none"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    #: Dispatched runs sit at the head, but none under a title the train reads.
    UNRECOGNISED = "unrecognised"


def gate_evidence(
    runs: Iterable[Mapping[str, Any]], *, ref: str, sha: str, waived: bool
) -> tuple[GateEvidence, Mapping[str, Any] | None]:
    """The state of the candidate's integration runs, and the run that decides it.

    Only a dispatched run at exactly ``sha`` from exactly ``ref`` counts. A
    green ``gate`` run (or, under the waiver label, a green ``offline-gate``
    run) is evidence; otherwise such a run in flight is waited for; otherwise a
    concluded one is a failure the train reports. Any *other* dispatched run at
    the head — a per-scenario run, or a whole-suite run whose title this code
    does not recognise because the candidate's workflow titles it differently
    — is :attr:`GateEvidence.UNRECOGNISED`, never :attr:`GateEvidence.NONE`:
    only a head with no dispatched run at all is owed a dispatch, so no drift
    in the title can make the train pay for the suite again.
    """
    titles = {GATE_TITLE, OFFLINE_GATE_TITLE} if waived else {GATE_TITLE}
    at_head = [
        run
        for run in runs
        if run.get("head_sha") == sha
        and run.get("head_branch") == ref
        and run.get("event") == "workflow_dispatch"
    ]
    mine = [run for run in at_head if run.get("display_title") in titles]
    for run in mine:
        if run.get("status") == "completed" and run.get("conclusion") == "success":
            return GateEvidence.SUCCEEDED, run
    for run in mine:
        if run.get("status") in _IN_FLIGHT:
            return GateEvidence.RUNNING, run
    for run in mine:
        if run.get("status") == "completed":
            return GateEvidence.FAILED, run
    # Any other status (an unknown one) is not a conclusion: wait on it.
    for run in mine:
        return GateEvidence.RUNNING, run
    for run in at_head:
        return GateEvidence.UNRECOGNISED, run
    return GateEvidence.NONE, None


def dispatches_today(runs: Iterable[Mapping[str, Any]], *, now: datetime) -> int:
    """The integration-test runs the dispatch bot started on ``now``'s UTC day."""
    day = now.strftime("%Y-%m-%d")
    return sum(
        1
        for run in runs
        if run.get("event") == "workflow_dispatch"
        and _mapping(run.get("actor")).get("login") == DISPATCH_BOT
        and str(run.get("created_at") or "").startswith(day)
    )


class Approval(StrEnum):
    """The review state of the candidate's head."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    PENDING = "pending"


def approval_state(
    reviews: Iterable[Mapping[str, Any]], *, sha: str, config: TrainConfig
) -> tuple[Approval, str, str]:
    """Whether a listed approver approved exactly ``sha`` with nothing requested since.

    Returns the state, its reason, and the approval's ``submitted_at`` (empty
    unless approved). Each reviewer's latest decisive review counts (a comment
    is not one; a dismissal clears the earlier verdict). Any reviewer whose
    latest is a change request blocks the merge, whoever they are. An approval
    counts only from a listed approver and only at ``sha``: one at an older
    head is stale. The caller passes *every* review: a list cut short by
    pagination could hide a later change request.
    """
    latest: dict[str, Mapping[str, Any]] = {}
    ordered = sorted(reviews, key=lambda review: str(review.get("submitted_at") or ""))
    for review in ordered:
        state = review.get("state")
        if state not in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            continue
        login = _mapping(review.get("user")).get("login")
        if not isinstance(login, str) or not login:
            continue
        latest[login.casefold()] = review
    requested = sorted(
        str(_mapping(review.get("user")).get("login"))
        for review in latest.values()
        if review.get("state") == "CHANGES_REQUESTED"
    )
    if requested:
        return Approval.CHANGES_REQUESTED, f"changes requested by {', '.join(requested)}", ""
    stale: list[str] = []
    for review in latest.values():
        login = str(_mapping(review.get("user")).get("login"))
        if review.get("state") != "APPROVED" or not config.is_approver(login):
            continue
        if review.get("commit_id") == sha:
            return (
                Approval.APPROVED,
                f"approved at {sha[:9]} by {login}",
                str(review.get("submitted_at") or ""),
            )
        stale.append(f"{login} at {str(review.get('commit_id'))[:9]}")
    detail = f" (stale approval: {', '.join(sorted(stale))})" if stale else ""
    return (
        Approval.PENDING,
        f"awaiting approval of {sha[:9]} by {' or '.join(config.approvers)}{detail}",
        "",
    )


class Checks(StrEnum):
    """Where the required checks on the candidate's head stand."""

    GREEN = "green"
    PENDING = "pending"
    REFIRE = "refire"
    FAILING = "failing"


def _actions_runs(check_runs: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        run
        for run in check_runs
        if isinstance(run.get("name"), str) and _mapping(run.get("app")).get("slug") == _ACTIONS_APP
    ]


def check_state(
    check_runs: Iterable[Mapping[str, Any]], *, config: TrainConfig
) -> tuple[Checks, str]:
    """The required checks on the head, from its check runs (newest per name wins).

    ``promotion-gate`` must conclude ``success``; every other required check may
    also be ``skipped`` or ``neutral``, which satisfies a required check. Only
    GitHub Actions' check runs count. Anything still running is waited for; a
    missing or failed ``promotion-gate`` alone is re-fired; any other failure
    or missing check needs a human.
    """
    newest: dict[str, Mapping[str, Any]] = {}
    for run in _actions_runs(check_runs):
        name = str(run["name"])
        run_id = run.get("id")
        held = newest.get(name)
        if (
            held is None
            or not isinstance(held.get("id"), int)
            or (isinstance(run_id, int) and run_id > held["id"])
        ):
            newest[name] = run
    pending: list[str] = []
    failing: list[str] = []
    missing: list[str] = []
    for name in config.required_checks:
        latest = newest.get(name)
        if latest is None:
            missing.append(name)
            continue
        if latest.get("status") != "completed":
            pending.append(name)
            continue
        passing = {"success"} if name == PROMOTION_GATE_CHECK else {"success", "skipped", "neutral"}
        if latest.get("conclusion") not in passing:
            failing.append(f"{name} ({latest.get('conclusion')})")
    if pending:
        return Checks.PENDING, f"required checks still running: {', '.join(pending)}"
    others = [entry for entry in failing if not entry.startswith(f"{PROMOTION_GATE_CHECK} ")]
    other_missing = [name for name in missing if name != PROMOTION_GATE_CHECK]
    if others or other_missing:
        parts = [*others, *(f"{name} (missing)" for name in other_missing)]
        return Checks.FAILING, f"required checks not green: {', '.join(parts)}"
    if failing or missing:
        return Checks.REFIRE, f"{PROMOTION_GATE_CHECK} is not green at the head"
    return Checks.GREEN, "every required check is green"


def gate_failures_since(check_runs: Iterable[Mapping[str, Any]], since: str) -> int:
    """``promotion-gate`` check runs that concluded red at or after ``since`` (ISO).

    Re-fires happen only once the head is approved, so the failures after the
    approval are the re-fires that did not take.
    """
    return sum(
        1
        for run in _actions_runs(check_runs)
        if run.get("name") == PROMOTION_GATE_CHECK
        and run.get("status") == "completed"
        and run.get("conclusion") not in {"success", "skipped", "neutral"}
        and str(run.get("completed_at") or "") >= since
    )


def _dispatch_command(ref: str, scenario: str) -> str:
    return f"gh workflow run integration-test.yml --ref {ref} -f scenario={scenario}"


def _is_writer_lane_path(path: str) -> bool:
    return any(
        path == prefix or (prefix.endswith("/") and path.startswith(prefix))
        for prefix in WRITER_LANE_PATHS
    )


def _cut_step(observed: Observed) -> TrainStep:  # noqa: PLR0911 - one return per outcome
    if (
        observed.main_ahead_paths is None
        or observed.staging_differs_from_main is None
        or observed.last_promotion_synced is None
    ):
        return TrainStep(
            action=TrainAction.WAIT,
            reason="staging's relation to main could not be read; nothing cut",
        )
    if not observed.last_promotion_synced:
        return TrainStep(
            action=TrainAction.WAIT,
            reason=(
                "staging does not yet hold main's last promotion merge; the next "
                "candidate waits for the sync"
            ),
        )
    unsynced = sorted(p for p in observed.main_ahead_paths if not _is_writer_lane_path(p))
    if unsynced:
        shown = ", ".join(unsynced[:3]) + (" …" if len(unsynced) > 3 else "")
        return TrainStep(
            action=TrainAction.WAIT,
            reason=(
                f"main holds changes staging lacks outside the writer lanes ({shown}); "
                "the next candidate waits for the sync"
            ),
        )
    if not observed.staging_differs_from_main:
        return TrainStep(
            action=TrainAction.WAIT, reason="staging carries nothing over main; nothing to cut"
        )
    sha = observed.staging_sha
    if sha is None or not _SHA.fullmatch(sha):
        return TrainStep(action=TrainAction.WAIT, reason="staging's tip could not be read")
    if observed.branches is None:
        return TrainStep(action=TrainAction.WAIT, reason="the promote/ branches could not be read")
    for name, head in observed.branches:
        if head == sha:
            return TrainStep(
                action=TrainAction.WAIT,
                reason=(
                    f"{name} already sits at staging {sha[:9]} with no open PR (closed "
                    "unmerged, or its PR never opened); the next candidate waits for "
                    "staging to move — reopen its PR, or open one from it, to retry this tip"
                ),
            )
    if not observed.cut_requested:
        return TrainStep(
            action=TrainAction.WAIT,
            reason=(
                f"staging {sha[:9]} carries a batch over main, ready to cut; a candidate "
                "is cut only when promotion-prep is dispatched: "
                f"`{CUT_COMMAND}`"
            ),
        )
    branch = next_branch_name(observed.now, (name for name, _ in observed.branches))
    return TrainStep(
        action=TrainAction.CUT,
        reason=f"cut {branch} at staging {sha[:9]} and opened its draft promotion PR",
        sha=sha,
        branch=branch,
    )


def _candidate_step(  # noqa: PLR0911, PLR0912 - one return per outcome, each named
    candidate: Candidate, observed: Observed, config: TrainConfig
) -> TrainStep:
    def step(action: TrainAction, reason: str) -> TrainStep:
        return TrainStep(
            action=action,
            reason=reason,
            pr=candidate.number,
            ref=candidate.ref,
            sha=candidate.sha,
        )

    if observed.head_on_staging is None:
        return step(TrainAction.WAIT, "staging's first-parent chain could not be read")
    if not observed.head_on_staging:
        return step(
            TrainAction.REPORT,
            f"head {candidate.sha[:9]} is not on staging's first-parent chain, so it is "
            "not a cut of staging: the train will not dispatch, mark ready or merge it",
        )
    pull = observed.pull
    if pull is not None and (
        pull.get("mergeable") is False or pull.get("mergeable_state") == "dirty"
    ):
        return step(
            TrainAction.REPORT,
            "conflicts with main; close this candidate — the next one needs a sync that "
            "resolves the conflict on staging",
        )
    if observed.runs is None:
        return step(TrainAction.WAIT, "the integration runs at the head could not be read")
    waived = WAIVER_LABEL in candidate.labels
    scenario = "offline-gate" if waived else "gate"
    evidence, run = gate_evidence(
        observed.runs, ref=candidate.ref, sha=candidate.sha, waived=waived
    )
    run_url = str(_mapping(run).get("html_url") or "")
    green = evidence is GateEvidence.SUCCEEDED or observed.freshness_ok is True
    if not green:
        if evidence is GateEvidence.NONE:
            if observed.registry_ok is None:
                return step(TrainAction.WAIT, "the registry gate could not be read")
            if not observed.registry_ok:
                return step(
                    TrainAction.REPORT,
                    "the process registry gate refuses this head, so the integration "
                    "gate is not dispatched (see the run's annotations); fix it on "
                    "staging and close this candidate",
                )
            if observed.recent_dispatches is None:
                return step(TrainAction.WAIT, "today's integration dispatches could not be read")
            started = dispatches_today(observed.recent_dispatches, now=observed.now)
            if started >= config.max_gate_dispatches_per_day:
                return step(
                    TrainAction.REPORT,
                    f"the train already started {started} integration suite(s) today, its "
                    f"daily cap of {config.max_gate_dispatches_per_day}: dispatch it by hand "
                    f"(`{_dispatch_command(candidate.ref, scenario)}`) or wait for tomorrow",
                )
            return step(
                TrainAction.DISPATCH_GATE,
                f"dispatched the integration {scenario} suite at {candidate.sha[:9]} "
                + f"(`{_dispatch_command(candidate.ref, scenario)}`)",
            ).model_copy(update={"scenario": scenario})
        if evidence is GateEvidence.RUNNING:
            return step(TrainAction.WAIT, f"the integration gate is running ({run_url})")
        if evidence is GateEvidence.UNRECOGNISED:
            return step(
                TrainAction.REPORT,
                f"an integration run the train does not recognise sits at the head "
                f"({_mapping(run).get('display_title')}, {run_url}) and freshness does not "
                "pass; the train dispatches no second suite — dispatch "
                + f"`{_dispatch_command(candidate.ref, scenario)}` yourself, or close this "
                "candidate",
            )
        run_id = _mapping(run).get("id")
        return step(
            TrainAction.REPORT,
            f"the integration gate concluded {_mapping(run).get('conclusion')} ({run_url}); "
            "the train does not re-dispatch it. Re-run it "
            + f"(`gh run rerun {run_id} --failed`), or close this candidate",
        )
    if candidate.draft:
        if marked_ready(candidate.body):
            return step(
                TrainAction.WAIT,
                "returned to draft after the train marked it ready; left as a draft",
            )
        return step(
            TrainAction.MARK_READY,
            "the integration evidence is green at the head; marked ready for review",
        ).model_copy(update={"reviewers": config.approvers})
    if observed.reviews is None:
        return step(TrainAction.WAIT, "the reviews could not be read")
    approval, approval_reason, approved_at = approval_state(
        observed.reviews, sha=candidate.sha, config=config
    )
    if approval is Approval.CHANGES_REQUESTED:
        return step(TrainAction.REPORT, approval_reason)
    if approval is Approval.PENDING:
        return step(TrainAction.WAIT, approval_reason)
    if pull is None or pull.get("mergeable") is not True:
        return step(
            TrainAction.WAIT, f"{approval_reason}; waiting for GitHub to compute mergeability"
        )
    if observed.quiescent is not True:
        return step(
            TrainAction.WAIT,
            f"{approval_reason}; waiting for no predict/evaluate/back-test round in flight",
        )
    if observed.registry_ok is None:
        return step(TrainAction.WAIT, "the registry gate could not be read")
    if not observed.registry_ok:
        return step(
            TrainAction.REPORT,
            "the process registry gate refuses this head against the current main",
        )
    if observed.check_runs is None:
        return step(TrainAction.WAIT, "the check runs at the head could not be read")
    checks, checks_reason = check_state(observed.check_runs, config=config)
    if checks is Checks.PENDING:
        return step(TrainAction.WAIT, checks_reason)
    if checks is Checks.FAILING:
        return step(TrainAction.REPORT, checks_reason)
    if checks is Checks.REFIRE:
        if observed.freshness_ok is not True:
            return step(
                TrainAction.REPORT,
                f"{approval_reason}; {checks_reason} and freshness does not pass at the "
                "head, so a re-fire would fail again",
            )
        failures = gate_failures_since(observed.check_runs, approved_at)
        if failures >= REFIRE_CAP:
            return step(
                TrainAction.REPORT,
                f"{approval_reason}; {PROMOTION_GATE_CHECK} failed {failures} time(s) since "
                "the approval with every other condition holding; the train re-fires it "
                "no more — read its log",
            )
        return step(
            TrainAction.REFIRE_GATE,
            f"{approval_reason}; {checks_reason}, re-fired it by a body edit",
        )
    return step(TrainAction.MERGE, f"{approval_reason}; merged with a merge commit")


def decide(observed: Observed, config: TrainConfig) -> TrainStep:
    """One tick of the promotion train."""
    if observed.open_pulls is None:
        return TrainStep(action=TrainAction.WAIT, reason="the open PRs into main could not be read")
    candidate, aside = find_candidate(observed.open_pulls, repo=observed.repo)
    if aside is not None:
        return TrainStep(action=TrainAction.WAIT, reason=aside)
    if candidate is None:
        return _cut_step(observed)
    return _candidate_step(candidate, observed, config)
