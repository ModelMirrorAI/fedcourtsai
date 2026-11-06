"""When a run-pull window makes up a cron slot GitHub's scheduler dropped.

GitHub drops or delays scheduled runs under load, and the pull lane is the root
of the pipeline: predict and evaluate chain from it. So every run-pull window,
whatever started it, ends by asking whether two slots it can see went unserved,
and run-pull's `chain-predict` job dispatches what this module answers:

- **The latest pull slot** (the ``17 *`` cron). It is made up when it is at
  least :data:`PULL_GRACE` old and no pull-mode run of run-pull was created
  since it, so whichever window does arrive serves the pull a dropped tick
  owed, unless the next pull tick is under :data:`PULL_HORIZON` away, since
  that window serves the pull and a second one within the hour would stack
  two windows' CourtListener spend against the hourly ceiling. The made-up
  run is dispatched with ``mode=pull`` only, never ``live``
  or ``enrich-opinions``, and only while no corpus writer is waiting in the
  shared lock: GitHub keeps one pending run per concurrency group, so a
  dispatch would evict a waiting seed or repair run.
- **The latest predict slot.** It is made up when it is at least
  :data:`PREDICT_GRACE` old and no run of run-predict, of any event, was
  created since it. The promotion stand-down in
  :func:`~fedcourtsai.dispatch_chain.chain_step` still applies.

A late tick then arrives for a slot already made up: :func:`slot_served` tells
a scheduled pull window to skip its pull when another pull-mode run was created
between its slot and itself, so a slot costs one window's CourtListener share,
not two. Each answer reads the runs created since the slot, so a made-up run
serves its slot and no window dispatches a second one; nothing here loops. That
holds only while the run listing reaches back past the slot, so the workflow
lists :data:`LISTING_HOURS` of runs, longer than any gap between two slots plus
its grace (a test holds the two together).

A make-up for an older slot dispatched after the next slot's time serves that
next slot too, so its late tick skips: two slots then cost one window, which
errs toward spending less. A pull-titled run the run gate refused also counts
as serving, which stands the make-up down rather than guessing.

A run-pull run's mode is in its title (``run-pull pull``, ``run-pull live``),
which the workflow's ``run-name`` sets. A title without a mode is read as
serving a pull, so an unreadable run stands the make-up down rather than
doubling a window.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from .ops import parse_iso
from .schedule_delivery import slots_between
from .site_status import last_tick, parse_cron, workflow_crons

#: How long after a pull slot a window waits for its tick before making it up.
#: Healthy ticks arrive within about a quarter of an hour.
PULL_GRACE = timedelta(minutes=40)

#: A pull slot is not made up when the next pull tick is this close.
PULL_HORIZON = timedelta(hours=2)

#: How long after a predict slot before it is made up.
PREDICT_GRACE = timedelta(minutes=60)

#: How many hours of runs run-pull's chain job lists for :func:`catch_up`.
LISTING_HOURS = 26

#: The cron prefix that selects run-pull's pull job.
PULL_CRON_PREFIX = "17 "

#: The workflows that write the corpus under the one `corpus-write` lock.
CORPUS_WRITERS = frozenset({"run-pull", "run-seed", "run-repair"})

#: The titles of run-pull runs that serve a pull slot.
_PULL_TITLES = frozenset({"run-pull pull", "run-pull"})

#: Run statuses that wait for a runner or a lock (anything but running or done).
_WAITING = frozenset({"queued", "pending", "waiting", "requested"})

_DEFAULT_BRANCH = "main"


class CatchUpAction(StrEnum):
    """What run-pull's chain job does about one lane."""

    DISPATCH = "dispatch"
    NONE = "none"


class LaneCatchUp(BaseModel):
    """One lane's answer, with the line the step summary records."""

    action: CatchUpAction
    slot: datetime | None
    reason: str


class CatchUp(BaseModel):
    """Both lanes' answers for one window."""

    pull: LaneCatchUp
    predict: LaneCatchUp


class Run(BaseModel):
    """The fields of one REST workflow run this module reads."""

    id: int
    workflow: str
    title: str
    created_at: datetime
    status: str
    conclusion: str | None


def _aware(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    parsed = parse_iso(value)
    if parsed is None:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def read_runs(rows: Iterable[object]) -> list[Run]:
    """The `main` runs in a REST ``workflow_runs`` list or its slurped pages."""
    out: list[Run] = []

    def visit(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                visit(child)
            return
        if not isinstance(item, Mapping):
            return
        if "workflow_runs" in item:
            visit(item["workflow_runs"])
            return
        branch = item.get("head_branch")
        if branch is not None and branch != _DEFAULT_BRANCH:
            return
        path, run_id, created = item.get("path"), item.get("id"), _aware(item.get("created_at"))
        if not isinstance(path, str) or not isinstance(run_id, int) or created is None:
            return
        conclusion = item.get("conclusion")
        out.append(
            Run(
                id=run_id,
                workflow=Path(path.split("@", 1)[0]).stem,
                title=str(item.get("display_title") or ""),
                created_at=created,
                status=str(item.get("status") or ""),
                conclusion=conclusion if isinstance(conclusion, str) else None,
            )
        )

    visit(list(rows))
    return out


def _serves_pull(run: Run) -> bool:
    return (
        run.workflow == "run-pull" and run.title in _PULL_TITLES and run.conclusion != "cancelled"
    )


def _serves_predict(run: Run) -> bool:
    return run.workflow == "run-predict" and run.conclusion != "cancelled"


def pull_crons(workflows_root: Path) -> list[str]:
    """run-pull's pull-window crons, the ones whose minute selects the pull job."""
    return [c for c in workflow_crons(workflows_root, "run-pull") if c.startswith(PULL_CRON_PREFIX)]


def _lane(
    name: str,
    *,
    crons: Sequence[str],
    grace: timedelta,
    runs: Sequence[Run],
    serves: Callable[[Run], bool],
    now: datetime,
) -> tuple[datetime | None, LaneCatchUp | None]:
    """The lane's due slot, or the answer when there is nothing to make up."""
    slot = last_tick([parse_cron(c) for c in crons], now - grace)
    if slot is None:
        return None, LaneCatchUp(
            action=CatchUpAction.NONE, slot=None, reason=f"{name}: no schedule to make up"
        )
    served = [run for run in runs if serves(run) and run.created_at >= slot]
    if served:
        first = min(served, key=lambda run: run.created_at)
        return slot, LaneCatchUp(
            action=CatchUpAction.NONE,
            slot=slot,
            reason=f"{name}: the {slot:%H:%MZ} slot was served by run {first.id}",
        )
    return slot, None


def catch_up(
    rows: Iterable[object],
    *,
    workflows_root: Path,
    now: datetime,
    run_id: int,
) -> CatchUp:
    """Whether this window makes up the latest pull slot and the latest predict slot.

    ``rows`` is the recent runs of run-pull, run-predict and the other corpus
    writers (REST pages); ``run_id`` is this window's own run, which never
    counts as a waiting writer. A naive ``now`` is read as UTC.
    """
    now = now if now.tzinfo is not None else now.replace(tzinfo=UTC)
    runs = read_runs(rows)
    slot, answer = _lane(
        "pull",
        crons=pull_crons(workflows_root),
        grace=PULL_GRACE,
        runs=runs,
        serves=_serves_pull,
        now=now,
    )
    if answer is None:
        waiting = [
            run
            for run in runs
            if run.id != run_id
            and run.workflow in CORPUS_WRITERS
            # run-repair takes the lock per job, so a running repair run may
            # hold a job waiting for it: any unfinished one counts.
            and (
                run.status in _WAITING
                or (run.workflow == "run-repair" and run.status != "completed")
            )
        ]
        coming = slots_between(
            [parse_cron(c) for c in pull_crons(workflows_root)], now, now + PULL_HORIZON
        )
        if coming:
            answer = LaneCatchUp(
                action=CatchUpAction.NONE,
                slot=slot,
                reason=(
                    f"pull: the {slot:%H:%MZ} slot went unserved, but the {coming[0]:%H:%MZ} "
                    "tick is due within two hours and serves it"
                ),
            )
        elif waiting:
            answer = LaneCatchUp(
                action=CatchUpAction.NONE,
                slot=slot,
                reason=(
                    f"pull: the {slot:%H:%MZ} slot went unserved, but run {waiting[0].id} "
                    f"({waiting[0].workflow}) waits for the corpus lock, which a dispatch "
                    "would evict; the next window asks again"
                ),
            )
        else:
            answer = LaneCatchUp(
                action=CatchUpAction.DISPATCH,
                slot=slot,
                reason=f"pull: the {slot:%H:%MZ} slot went unserved, so a pull window is "
                "dispatched",
            )
    pull = answer
    slot, answer = _lane(
        "predict",
        crons=workflow_crons(workflows_root, "run-predict"),
        grace=PREDICT_GRACE,
        runs=runs,
        serves=_serves_predict,
        now=now,
    )
    predict = answer or LaneCatchUp(
        action=CatchUpAction.DISPATCH,
        slot=slot,
        reason=f"predict: the {slot:%H:%MZ} slot went unserved",
    )
    return CatchUp(pull=pull, predict=predict)


class SlotVerdict(BaseModel):
    """Whether a scheduled pull window's slot was already served."""

    served: bool
    reason: str


def slot_served(
    rows: Iterable[object], *, schedule: str, run_id: int, created_at: datetime
) -> SlotVerdict:
    """Whether another pull-mode run served this scheduled window's slot first.

    ``schedule`` is the cron that fired this run and ``created_at`` its creation
    time (a naive one is read as UTC); the slot is that cron's newest tick at or
    before it.
    """
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    slot = last_tick([parse_cron(schedule)], created_at)
    if slot is None:
        return SlotVerdict(served=False, reason="no slot found for this window's cron")
    earlier = [
        run
        for run in read_runs(rows)
        if _serves_pull(run) and run.id != run_id and slot <= run.created_at < created_at
    ]
    if earlier:
        first = min(earlier, key=lambda run: run.created_at)
        return SlotVerdict(
            served=True,
            reason=f"run {first.id} already served the {slot:%Y-%m-%d %H:%MZ} pull slot, "
            "so this late tick skips its pull",
        )
    return SlotVerdict(
        served=False, reason=f"no other pull window served the {slot:%Y-%m-%d %H:%MZ} slot"
    )
