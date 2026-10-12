"""Whether a predict round may skip the `review` hold, and whether to chain another.

The `review` hold is the per-round spend gate: every round renders its plan and
waits for a maintainer to release it. Two decisions read that same plan, and
both are made here so the workflow only routes on their answers:

- **Auto-release.** A round whose priced fan-out is under the per-round cap,
  while fewer than the daily number of rounds have been auto-released in the
  trailing 24 hours, skips the hold. It fails closed: an unknown count, a
  missing estimate, a matrix that disagrees with the plan, or a disabled cap
  all keep the hold.
- **Drain.** A round that left owed work behind because a cap stopped it — the
  per-round cell cap, or the reconciliation's case cap — asks for another round
  as soon as its own output has landed, rather than waiting for the next
  scheduled slot. A drained backlog, or a round stopped by anything else, asks
  for nothing.

**What is priced is what runs.** The plan document is a second walk of the
backlog; the cells that actually spend are the matrix the first walk minted.
The two are built by the same helpers but nothing forces them to agree, so a
round auto-releases only when the matrix holds exactly the plan's would-mint
cell count, and its price is the larger of the plan's estimate and the
matrix's own cells priced at the same planning rates
(:mod:`fedcourtsai.planning_rates`).

**The daily count has two sources.** Each auto-released round leaves a
deployment to the `review-auto` environment, and its ready collect commit lands
on `main` with the auto-released mark in its subject
(:data:`fedcourtsai.collect.AUTO_RELEASED_MARKER`). A write holder can prune
the deployment list; `main`'s history is append-only. The count is the larger
of the two, and an unreadable source keeps the hold.

The decision is pure: the counts, the matrix and the commit subjects come in as
arguments, so the rule is testable without the Actions API, and the workflow is
responsible only for reading them. The caps' model and loader, and the glue
that turns the files the workflow read into those arguments
(:func:`decide_from_files`), live here too, so everything that decides whether
a round spends unattended sits in one code-owned module and the CLI only
parses options.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .collect import AUTO_RELEASED_MARKER
from .planning_rates import price_cells


class ReviewHoldConfig(BaseModel):
    """When a predict round may skip the `review` hold (``config/review-hold.yaml``).

    The hold is the per-round spend gate: a maintainer releases each round's plan
    before a cell spends. Auto-release lets a round whose *estimated* spend is
    small skip that wait, so a backlog drains without a human releasing every
    cycle. It is bounded twice — per round by estimated spend, per day by the
    number of rounds released this way — and anything above either bound still
    waits on the hold. The ex-post backstop (`spend`) stands behind both.
    """

    model_config = ConfigDict(extra="ignore")

    # A round whose plan estimates at most this much spend, USD, is released
    # without the hold. `0` DISABLES auto-release (the convention the other caps
    # use), which is the default: every round waits on the hold until a
    # maintainer adopts a value.
    # At most $50: a sanity bound, so a slipped decimal ("500" for "5.00")
    # is refused at load rather than adopted as a cap.
    auto_release_usd_per_round: float = Field(default=0.0, ge=0.0, le=50.0, allow_inf_nan=False)
    # At most this many rounds are auto-released in any trailing 24 hours; the
    # next one waits on the hold. `0` disables auto-release too. The daily bound
    # on unattended *estimated* spend is therefore at most this times the
    # per-round cap; the `spend` backstop bounds what is actually spent.
    # At most 100: the plan job reads one page of the deployments it counts.
    auto_release_rounds_per_day: int = Field(default=0, ge=0, le=100)


#: The auto-release caps' own file, apart from ``tracking.yaml`` because it is
#: spend authority the maintainer owns (``.github/CODEOWNERS``).
REVIEW_HOLD_FILENAME = "review-hold.yaml"


def load_review_hold_config(config_root: Path) -> ReviewHoldConfig:
    """Read the auto-release caps from ``config_root/review-hold.yaml``.

    Falls back to the defaults — **disabled**, every round held — if the file is
    absent.
    """
    path = config_root / REVIEW_HOLD_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return ReviewHoldConfig.model_validate(data or {})


#: A ready predict commit's subject on `main`, carrying the auto-released mark.
#: The squash takes the commit message for a one-commit PR —
#: ``predict(run <id>): N prediction(s) [auto-released] (#N)`` — and the PR
#: title otherwise — ``predict: N prediction(s) (run <id>) [auto-released] (#N)``
#: — so the run id is read wherever it sits, before the mark.
_AUTO_RELEASED_SUBJECT = re.compile(
    r"^predict\b.*?\brun (?P<run>\d{8}T\d{6}Z)\b.*" + re.escape(AUTO_RELEASED_MARKER)
)


class HoldDecision(BaseModel):
    """The two answers a predict round's plan job routes on, with their inputs."""

    auto_release: bool
    auto_release_reason: str
    drain_more: bool
    drain_reason: str
    estimated_spend_usd: float | None
    #: The rounds counted against the daily cap: the larger of the deployment
    #: count and the committed count, or ``None`` when either is unreadable.
    released_last_day: int | None
    plan_cells: int | None
    matrix_cells: int | None


def count_auto_released(subjects: Iterable[str]) -> int:
    """How many distinct predict rounds ``subjects`` mark as auto-released.

    ``subjects`` are commit subjects (first lines) from `main` over the trailing
    24 hours. Counted by run id, so a rerun's second commit for one round does
    not count it twice.
    """
    runs = {
        match.group("run")
        for subject in subjects
        if (match := _AUTO_RELEASED_SUBJECT.match(subject.strip()))
    }
    return len(runs)


def released_last_day(deployments: int | None, committed: int | None) -> int | None:
    """The stricter of the two daily counts, or ``None`` if either is unknown.

    Either source can undercount on its own — a pruned deployment list, or a
    round whose collect PR has not merged yet — so the larger one binds, and a
    source that could not be read keeps the hold rather than being skipped.
    """
    if deployments is None or committed is None or deployments < 0 or committed < 0:
        return None
    return max(deployments, committed)


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0:
        return None
    return number


def _plan_cells(plan: Mapping[str, Any]) -> int | None:
    counts = plan.get("counts")
    ledger = counts.get("cell_ledger") if isinstance(counts, Mapping) else None
    cells = ledger.get("would_mint_cells") if isinstance(ledger, Mapping) else None
    if isinstance(cells, bool) or not isinstance(cells, int) or cells < 0:
        return None
    return cells


def _matrix_cells(matrix: Mapping[str, Any] | None) -> list[Mapping[str, Any]] | None:
    include = matrix.get("include") if isinstance(matrix, Mapping) else None
    if not isinstance(include, list) or not all(isinstance(c, Mapping) for c in include):
        return None
    return include


def _price(plan: Mapping[str, Any], matrix: list[Mapping[str, Any]] | None) -> float | None:
    """The larger of the plan's estimate and the matrix's own priced cells.

    A missing, boolean, non-finite or negative plan estimate is no estimate at
    all, so it keeps the hold rather than comparing as under the cap.
    """
    estimate = _number(plan.get("estimated_spend_usd"))
    if estimate is None:
        return None
    if matrix is None:
        return estimate
    priced, _ = price_cells(matrix, seam="predict")
    return max(estimate, round(priced, 2))


def _auto_release(  # noqa: PLR0911 - one return per fail-closed reason, each named
    estimate: float | None,
    config: ReviewHoldConfig,
    released: int | None,
    plan_cells: int | None,
    matrix: list[Mapping[str, Any]] | None,
) -> tuple[bool, str]:
    if config.auto_release_usd_per_round <= 0 or config.auto_release_rounds_per_day <= 0:
        return False, "auto-release is disabled (the review-hold caps are 0)"
    if released is None:
        return False, "the count of rounds auto-released in the last 24h could not be read"
    if released >= config.auto_release_rounds_per_day:
        return False, (
            f"{released} round(s) already auto-released in the last 24h "
            f"(daily cap {config.auto_release_rounds_per_day})"
        )
    if matrix is None:
        return False, "the minted matrix could not be read"
    if plan_cells is None or len(matrix) != plan_cells:
        return False, (
            f"the minted matrix holds {len(matrix)} cell(s) but the plan reports "
            f"{plan_cells if plan_cells is not None else 'no'} would-mint cell(s), so the "
            "price is not the price of what runs"
        )
    if estimate is None:
        return False, "the plan carries no spend estimate"
    if estimate > config.auto_release_usd_per_round:
        return False, (
            f"estimated spend ${estimate:,.2f} is over the per-round cap "
            f"${config.auto_release_usd_per_round:,.2f}"
        )
    return True, (
        f"estimated spend ${estimate:,.2f} is within the per-round cap "
        f"${config.auto_release_usd_per_round:,.2f}, round {released + 1} of "
        f"{config.auto_release_rounds_per_day} in the last 24h"
    )


def _drain(plan: Mapping[str, Any]) -> tuple[bool, str]:
    counts = plan.get("counts")
    counts = counts if isinstance(counts, Mapping) else {}
    if not plan.get("would_mint"):
        return False, "the round mints nothing"
    ledger = counts.get("cell_ledger")
    ledger = ledger if isinstance(ledger, Mapping) else {}
    deferred = ledger.get("deferred_by_cap_cells")
    if isinstance(deferred, int) and not isinstance(deferred, bool) and deferred > 0:
        return True, f"the per-round cell cap deferred {deferred} cell(s)"
    reconciliation = counts.get("case_reconciliation")
    if isinstance(reconciliation, Mapping) and reconciliation.get("cap_reached") is True:
        return True, "the backlog's per-cycle case cap was reached"
    return False, "no cap stopped this round short of the backlog"


def decide(
    plan: Mapping[str, Any],
    config: ReviewHoldConfig,
    *,
    released_last_day: int | None,
    matrix: Mapping[str, Any] | None,
) -> HoldDecision:
    """Decide auto-release and drain for one round's plan and minted matrix.

    ``released_last_day`` is the rounds auto-released in the trailing 24 hours
    (:func:`released_last_day` over both sources), or ``None`` when it could not
    be read — which keeps the hold. ``matrix`` is the `predict-matrix` document
    the round minted; ``None`` keeps the hold.
    """
    cells = _matrix_cells(matrix)
    estimate = _price(plan, cells)
    plan_cells = _plan_cells(plan)
    release, release_reason = _auto_release(estimate, config, released_last_day, plan_cells, cells)
    drain, drain_reason = _drain(plan)
    return HoldDecision(
        auto_release=release,
        auto_release_reason=release_reason,
        drain_more=drain,
        drain_reason=drain_reason,
        estimated_spend_usd=estimate,
        released_last_day=released_last_day,
        plan_cells=plan_cells,
        matrix_cells=None if cells is None else len(cells),
    )


def render_summary(decision: HoldDecision) -> str:
    """The step-summary block a round's plan job publishes beside its plan report."""
    lines = ["", "### Hold and drain"]
    if decision.auto_release:
        lines.append(f"- **Auto-released:** {decision.auto_release_reason}.")
    else:
        lines.append(f"- **Waits on the review hold:** {decision.auto_release_reason}.")
    if decision.drain_more:
        lines.append(
            f"- **Another round is owed:** {decision.drain_reason}; it is dispatched once "
            "this round's collect PR merges, if the dispatch chain is on."
        )
    else:
        lines.append(f"- **No further round from this one:** {decision.drain_reason}.")
    return "\n".join(lines) + "\n"


def _read_matrix(matrix_file: Path | None) -> dict[str, Any] | None:
    """The minted matrix document, or ``None`` — which keeps the hold — if unread."""
    if matrix_file is None:
        return None
    try:
        loaded = json.loads(matrix_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _read_committed(main_subjects_file: Path | None) -> int | None:
    """The auto-released rounds in ``main``'s subjects, or ``None`` if unread."""
    if main_subjects_file is None:
        return None
    try:
        subjects = main_subjects_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    return count_auto_released(subjects)


def decide_from_files(
    plan: Mapping[str, Any],
    config_root: Path,
    *,
    deployments_released: int | None,
    main_subjects_file: Path | None,
    matrix_file: Path | None,
) -> HoldDecision:
    """:func:`decide` over what the plan job read: the caps file, the counts, the matrix.

    Every input the workflow could not read arrives as ``None`` (or a file that
    will not parse) and keeps the hold; the caps come from
    ``config_root/review-hold.yaml``.
    """
    return decide(
        plan,
        load_review_hold_config(config_root),
        released_last_day=released_last_day(
            deployments_released, _read_committed(main_subjects_file)
        ),
        matrix=_read_matrix(matrix_file),
    )
