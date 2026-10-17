"""The promotion train: one decision per tick about the staging→main promotion.

`promotion-prep` runs hourly and asks this module what to do next. The answer
is a single :class:`TrainStep`, derived only from what the workflow read — the
open PRs into `main`, the existing `promote/*` branches and their heads,
staging's relation to `main`, and, for the one open candidate, its integration
runs, reviews, check runs and the gate stages read live — so the rule is
testable without the Actions API and the workflow only routes on the answer.

A **candidate** is a frozen release branch, ``promote/<UTC date>`` (``-2``,
``-3`` … when the date is taken), cut at staging's tip and never moved again,
with a PR from it into `main`. Freezing the head is the point: staging keeps
taking merges and syncs while the maintainer takes hours or days to read the
batch, and neither the integration evidence nor the approval — both bound to
one SHA — is invalidated by them. The steps:

====================  ================================================  =========================
action                when                                              does
====================  ================================================  =========================
``cut``               no open promotion PR; staging contains `main`     create the branch at the
                      and its tree differs from `main`'s; no            staging tip read, open a
                      ``promote/`` branch already sits at that tip      draft PR into `main`
``dispatch_gate``     the candidate has no integration ``gate`` run     dispatch integration-test
                      at its head (queued, running or concluded) and    ``scenario=gate`` at the
                      the registry gate passes                          branch (dispatch App)
``mark_ready``        the ``gate`` run at the head succeeded and the    mark ready, request the
                      PR is a draft the train has not marked before     approvers' review; the
                                                                        body edit re-fires CI
``refire_gate``       approved at the head, quiescent, registry clean,  edit the body, which
                      every required check concluded, and only          re-runs ci.yml's
                      ``promotion-gate`` failed or is missing           ``promotion-gate``
``merge``             approved at the head with no changes requested,   merge commit, pinned to
                      quiescent now, registry clean, every required     the head SHA (dev App)
                      check green
``wait``              something will change without anyone acting       nothing (body refresh)
``report``            a human has to act                                nothing (body refresh)
====================  ================================================  =========================

Everything unreadable resolves to ``wait``, never to an act. A failed ``gate``
run is reported and never re-dispatched: the paid suite runs at most once per
candidate unless the maintainer re-runs it. Candidate branches are never
deleted, so a branch already at the staging tip means that tip was cut before:
a candidate the maintainer closed unmerged is not re-cut, and the next one
waits for staging to move (reopening the PR, or opening one from the branch,
puts it back on the train). A hand-opened ``staging`` → `main` PR makes the
train stand aside, so there is one promotion in flight at a time.
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
from pydantic import BaseModel, ConfigDict, field_validator

#: The train's configuration file, under the config root (``config/``).
CONFIG_FILENAME = "promotion-train.yaml"

#: Every candidate branch lives under this prefix.
BRANCH_PREFIX = "promote/"

#: The only branch names the train cuts and acts on: the UTC date, and a
#: numeric suffix from 2 when that date is already taken.
BRANCH_NAME = re.compile(r"promote/\d{4}-\d{2}-\d{2}(?:-(?:[2-9]|[1-9]\d+))?")

#: The integration-test run titles that are whole-suite promotion evidence.
#: A `promote/*` dispatch resolves the `staging` environment, so the titles are
#: the staging branch's; the branch itself is pinned by the run's head_branch.
GATE_TITLE = "integration-test: gate @ staging"
OFFLINE_GATE_TITLE = "integration-test: offline-gate @ staging"

#: The label under which the promotion gate accepts an `offline-gate` run.
WAIVER_LABEL = "promote:skip-engine-smoke"

#: Written once into a candidate's body, outside the generated block, when the
#: train marks it ready. A draft carrying it was returned to draft by a
#: maintainer, and the train leaves it there.
READY_MARKER = "<!-- promotion-train:marked-ready -->"

#: The required check the train may re-fire by a body edit.
PROMOTION_GATE_CHECK = "promotion-gate"

#: The app every counted check run must come from.
_ACTIONS_APP = "github-actions"

_IN_FLIGHT = frozenset({"queued", "in_progress", "waiting", "pending", "requested"})
_HUMAN_LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
_SHA = re.compile(r"[0-9a-f]{40}")


class TrainConfigError(ValueError):
    """The train's configuration is missing or malformed; the train acts on nothing."""


class TrainConfig(BaseModel):
    """``config/promotion-train.yaml``: whose approval the train merges on, and on
    which required checks.

    ``approvers`` are the GitHub logins whose approving review of a candidate's
    head is the merge decision. The dev App bypasses `main`'s approval rule, so
    this list — not the ruleset — is what binds the train's merge to a person.
    ``required_checks`` are the check contexts `main`'s ruleset requires; the
    platform enforces them on the merge too, and the train waits for them so it
    never asks for a merge it knows will be refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    approvers: tuple[str, ...]
    required_checks: tuple[str, ...]

    @field_validator("approvers")
    @classmethod
    def _logins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("names no approver: the train could never merge")
        for login in value:
            if not _HUMAN_LOGIN.fullmatch(login):
                raise ValueError(f"{login!r} is not a GitHub user login")
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
    staging_contains_main: bool | None = None
    staging_differs_from_main: bool | None = None
    # The candidate's own reads; unused when no candidate is open.
    head_on_staging: bool | None = None
    runs: Sequence[Mapping[str, Any]] | None = None
    reviews: Sequence[Mapping[str, Any]] | None = None
    check_runs: Sequence[Mapping[str, Any]] | None = None
    quiescent: bool | None = None
    registry_ok: bool | None = None


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
    """Where the candidate's whole-suite integration run stands."""

    NONE = "none"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def gate_evidence(
    runs: Iterable[Mapping[str, Any]], *, ref: str, sha: str, waived: bool
) -> tuple[GateEvidence, Mapping[str, Any] | None]:
    """The state of the candidate's gate runs, and the run that decides it.

    Only a dispatched run at exactly ``sha`` from exactly ``ref`` counts. A
    green ``gate`` run (or, under the waiver label, a green ``offline-gate``
    run) is evidence; otherwise one in flight is waited for; otherwise a
    concluded one is a failure the train reports; otherwise there is none.
    """
    titles = {GATE_TITLE, OFFLINE_GATE_TITLE} if waived else {GATE_TITLE}
    mine = [
        run
        for run in runs
        if run.get("head_sha") == sha
        and run.get("head_branch") == ref
        and run.get("event") == "workflow_dispatch"
        and run.get("display_title") in titles
    ]
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
    return GateEvidence.NONE, None


class Approval(StrEnum):
    """The review state of the candidate's head."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    PENDING = "pending"


def approval_state(
    reviews: Iterable[Mapping[str, Any]], *, sha: str, config: TrainConfig
) -> tuple[Approval, str]:
    """Whether a listed approver approved exactly ``sha`` with nothing requested since.

    Each reviewer's latest decisive review counts (a comment is not one; a
    dismissal clears the earlier verdict). Any reviewer whose latest is a
    change request blocks the merge, whoever they are. An approval counts only
    from a listed approver and only at ``sha``: one at an older head is stale.
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
        return Approval.CHANGES_REQUESTED, f"changes requested by {', '.join(requested)}"
    stale: list[str] = []
    for review in latest.values():
        login = str(_mapping(review.get("user")).get("login"))
        if review.get("state") != "APPROVED" or not config.is_approver(login):
            continue
        if review.get("commit_id") == sha:
            return Approval.APPROVED, f"approved at {sha[:9]} by {login}"
        stale.append(f"{login} at {str(review.get('commit_id'))[:9]}")
    detail = f" (stale approval: {', '.join(sorted(stale))})" if stale else ""
    return (
        Approval.PENDING,
        f"awaiting approval of {sha[:9]} by {' or '.join(config.approvers)}{detail}",
    )


class Checks(StrEnum):
    """Where the required checks on the candidate's head stand."""

    GREEN = "green"
    PENDING = "pending"
    REFIRE = "refire"
    FAILING = "failing"


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
    for run in check_runs:
        name = run.get("name")
        if not isinstance(name, str) or _mapping(run.get("app")).get("slug") != _ACTIONS_APP:
            continue
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


def _dispatch_command(ref: str) -> str:
    return f"gh workflow run integration-test.yml --ref {ref} -f scenario=gate"


def _cut_step(observed: Observed) -> TrainStep:  # noqa: PLR0911 - one return per outcome
    if observed.staging_contains_main is None or observed.staging_differs_from_main is None:
        return TrainStep(
            action=TrainAction.WAIT,
            reason="staging's relation to main could not be read; nothing cut",
        )
    if not observed.staging_contains_main:
        return TrainStep(
            action=TrainAction.WAIT,
            reason="staging does not contain main yet; the next candidate waits for the sync",
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
    if observed.runs is None:
        return step(TrainAction.WAIT, "the integration runs at the head could not be read")
    waived = WAIVER_LABEL in candidate.labels
    evidence, run = gate_evidence(
        observed.runs, ref=candidate.ref, sha=candidate.sha, waived=waived
    )
    run_url = str(_mapping(run).get("html_url") or "")
    if evidence is GateEvidence.NONE:
        if observed.registry_ok is None:
            return step(TrainAction.WAIT, "the registry gate could not be read")
        if not observed.registry_ok:
            return step(
                TrainAction.REPORT,
                "the process registry gate refuses this head, so the integration gate "
                "is not dispatched (see the run's annotations); fix it on staging and "
                "close this candidate",
            )
        return step(
            TrainAction.DISPATCH_GATE,
            f"dispatched the integration gate at {candidate.sha[:9]} "
            + f"(`{_dispatch_command(candidate.ref)}`)",
        )
    if evidence is GateEvidence.RUNNING:
        return step(TrainAction.WAIT, f"the integration gate is running ({run_url})")
    if evidence is GateEvidence.FAILED:
        run_id = _mapping(run).get("id")
        return step(
            TrainAction.REPORT,
            f"the integration gate concluded {_mapping(run).get('conclusion')} ({run_url}); "
            "the train does not re-dispatch it. Re-run it "
            + f"(`gh run rerun {run_id} --failed`), or close this candidate",
        )
    if candidate.draft:
        if READY_MARKER in candidate.body:
            return step(
                TrainAction.WAIT,
                "returned to draft after the train marked it ready; left as a draft",
            )
        return step(
            TrainAction.MARK_READY,
            "the integration gate is green at the head; marked ready for review",
        ).model_copy(update={"reviewers": config.approvers})
    if observed.reviews is None:
        return step(TrainAction.WAIT, "the reviews could not be read")
    approval, approval_reason = approval_state(observed.reviews, sha=candidate.sha, config=config)
    if approval is Approval.CHANGES_REQUESTED:
        return step(TrainAction.REPORT, approval_reason)
    if approval is Approval.PENDING:
        return step(TrainAction.WAIT, approval_reason)
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
