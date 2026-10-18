"""When the dispatch chain starts a predict round without waiting for the schedule.

Two jobs dispatch an input-less `run-predict` on `main` with the dispatch App's
token: run-pull's `chain-predict`, after a pull window, and run-predict's own
`chain`, after a round a cap stopped short of the backlog. Both decisions are
made here, from documents the workflow reads, so the jobs only route on the
answer and the rule is testable without the Actions API.

- **A pull window chains only on a forecast-relevant change**
  (:func:`forecast_relevance`): a window whose commit added or changed an
  event record, or moved the scope manifest. Every window commits a corpus
  pointer, so "the window committed" would chain every window; the event
  records are where a newly opened moment or a new forecastable event shows,
  and they are what the predict backlog is derived from. A change the proxy
  misses is still picked up by the scheduled rounds.
- **No chained round starts while a promotion is about to merge**
  (:func:`chain_step`). The promotion gate's quiescence check fails on any
  queued, running or waiting predict round, so a chain running beside a
  promotion that is waiting to merge would keep it from ever settling. For a
  hand-opened `staging` promotion that moment is the PR being ready for
  review; for a promotion train candidate (`promote/`), which is marked ready
  as soon as its integration gate is green and may then wait days for review,
  it is the candidate being ready *and* approved at its head by a listed
  approver (an unread review list counts as approved, so the chain stands
  down rather than guessing). The chain stands down until that PR merges,
  returns to draft or loses its approval; the schedule covers the gap.
- **A drained round waits for its own collect PR** before dispatching the
  next: the next round's already-predicted gate reads committed state, so an
  earlier dispatch would plan a narrower round. A draft, a closed PR, or no PR
  at all stops the chain; so does running out of attempts.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from .promotion_train import Approval, TrainConfig, approval_state

#: Changed-path statuses (``git diff --name-status``) that add or change a record.
_ADDS_OR_CHANGES = frozenset({"A", "M", "R", "C"})


class Relevance(BaseModel):
    """Whether a pull window's commit should start a predict round."""

    relevant: bool
    reason: str
    events_added: int
    events_changed: int
    scope_changed: bool


def _is_event_record(path: str) -> bool:
    # data/cases/<court>/<docket>/events/<event>/event.yaml
    parts = path.split("/")
    return (
        len(parts) == 7
        and parts[0] == "data"
        and parts[1] == "cases"
        and parts[4] == "events"
        and parts[6] == "event.yaml"
    )


def forecast_relevance(changes: Iterable[tuple[str, str]]) -> Relevance:
    """Read a window commit's ``(status, path)`` changes for a forecast-relevant one.

    ``status`` is ``git diff --name-status``'s first letter. A rename or copy
    counts as a change to its destination path.
    """
    added = changed = 0
    scope = False
    for status, path in changes:
        kind = status[:1]
        if path.startswith("data/scope/"):
            scope = True
        if kind in _ADDS_OR_CHANGES and _is_event_record(path):
            if kind == "A":
                added += 1
            else:
                changed += 1
    if added or changed or scope:
        parts = []
        if added:
            parts.append(f"{added} event record(s) added")
        if changed:
            parts.append(f"{changed} event record(s) changed")
        if scope:
            parts.append("the scope manifest moved")
        reason = ", ".join(parts)
        return Relevance(
            relevant=True,
            reason=reason,
            events_added=added,
            events_changed=changed,
            scope_changed=scope,
        )
    return Relevance(
        relevant=False,
        reason="the window changed no event record and no scope manifest",
        events_added=0,
        events_changed=0,
        scope_changed=False,
    )


class ChainMode(StrEnum):
    """Which chain job is asking."""

    PULL = "pull"
    DRAIN = "drain"


class ChainAction(StrEnum):
    """What the asking job does next."""

    DISPATCH = "dispatch"
    WAIT = "wait"
    STOP = "stop"


class ChainStep(BaseModel):
    """One answer for a chain job, with the line its step summary records."""

    action: ChainAction
    reason: str


def ready_promotion(
    pulls: Iterable[Mapping[str, Any]],
    *,
    repo: str,
    reviews: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
    train_config: TrainConfig | None = None,
) -> int | None:
    """The number of an open same-repo promotion PR into `main` about to merge, if any.

    ``pulls`` is the REST list of open PRs against `main`. A draft never counts.
    A ready `staging`-headed PR (a hand-opened promotion) counts. A ready
    promotion train candidate (`promote/`) counts once a listed approver has
    approved exactly its head with nothing requested since — the train merges
    only then, and the candidate may wait ready for days before it. ``reviews``
    maps a candidate's number to its full review list; a candidate missing
    from it, or no ``train_config``, counts as approved, since an unread
    approval must stand the chain down rather than let it run under a merge.
    """

    def _mapping(value: object) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    for pull in pulls:
        head = _mapping(pull.get("head"))
        base = _mapping(pull.get("base"))
        head_repo = _mapping(head.get("repo"))
        if (
            pull.get("state") == "open"
            and pull.get("draft") is False
            and base.get("ref") == "main"
            and head_repo.get("full_name") == repo
        ):
            ref = str(head.get("ref") or "")
            number = pull.get("number")
            if ref == "staging":
                return number if isinstance(number, int) else 0
            if not ref.startswith("promote/"):
                continue
            if not isinstance(number, int):
                return 0
            pull_reviews = None if reviews is None else reviews.get(number)
            if pull_reviews is None or train_config is None:
                return number
            state, _, _ = approval_state(
                pull_reviews, sha=str(head.get("sha") or ""), config=train_config
            )
            if state is Approval.APPROVED:
                return number
    return None


def _collect_state(pulls: Sequence[Mapping[str, Any]] | None) -> str:
    if pulls is None:
        return "unreadable"
    if not pulls:
        return "none"
    pull = pulls[0]
    if pull.get("merged_at"):
        return "merged"
    if pull.get("draft") is True:
        return "draft"
    state = pull.get("state")
    return state if isinstance(state, str) else "unreadable"


def chain_step(  # noqa: PLR0911 - one return per outcome, each named
    mode: ChainMode,
    *,
    repo: str,
    promotion_pulls: Sequence[Mapping[str, Any]] | None,
    promotion_reviews: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
    train_config: TrainConfig | None = None,
    collect_pulls: Sequence[Mapping[str, Any]] | None = None,
    attempt: int = 1,
    max_attempts: int = 40,
) -> ChainStep:
    """Decide one step of a chain job.

    ``promotion_pulls`` is the open PRs against `main` (``None`` when the read
    failed, which stands the chain down: a dispatch that could stall a
    promotion is not worth the guess). ``promotion_reviews`` and
    ``train_config`` decide whether a ready train candidate is approved
    (:func:`ready_promotion`). ``collect_pulls`` is the drain mode's read of
    this round's collect PR, newest first, ``None`` when unreadable.
    """
    if promotion_pulls is None:
        return ChainStep(
            action=ChainAction.STOP,
            reason="the open promotion PRs could not be read, so the chain stands down",
        )
    number = ready_promotion(
        promotion_pulls, repo=repo, reviews=promotion_reviews, train_config=train_config
    )
    if number is not None:
        return ChainStep(
            action=ChainAction.STOP,
            reason=(
                f"promotion PR #{number} is ready to merge, so the chain stands down until "
                "it merges, returns to draft or loses its approval; the schedule picks the "
                "backlog up"
            ),
        )
    if mode is ChainMode.PULL:
        return ChainStep(
            action=ChainAction.DISPATCH,
            reason="dispatched a predict round on the state this window committed",
        )
    state = _collect_state(collect_pulls)
    if state == "merged":
        return ChainStep(
            action=ChainAction.DISPATCH,
            reason="dispatched the next predict round (this round's collect PR merged)",
        )
    if state == "closed":
        return ChainStep(
            action=ChainAction.STOP,
            reason="this round's collect PR closed unmerged; nothing dispatched",
        )
    # A ready PR is pushed before `collect` finishes, so a missing one after the
    # first minutes means this round opened none (all its output went to a
    # draft or a facts-only branch), and a draft never auto-merges: either way,
    # waiting would only hold the group.
    if state == "draft" or (state == "none" and attempt >= 3):
        return ChainStep(
            action=ChainAction.STOP,
            reason=f"this round has no auto-merging collect PR ({state}); nothing dispatched",
        )
    if attempt >= max_attempts:
        return ChainStep(
            action=ChainAction.STOP,
            reason=(
                f"this round's collect PR did not merge within {max_attempts} attempts "
                f"({state}); nothing dispatched"
            ),
        )
    return ChainStep(action=ChainAction.WAIT, reason=f"collect PR is {state}; waiting")
