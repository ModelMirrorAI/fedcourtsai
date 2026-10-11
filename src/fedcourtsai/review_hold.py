"""Whether a predict round may skip the `review` hold, and whether to chain another.

The `review` hold is the per-round spend gate: every round renders its plan and
waits for a maintainer to release it. Two decisions read that same plan, and
both are made here so the workflow only routes on their answers:

- **Auto-release.** A round whose estimated spend is under the per-round cap,
  while fewer than the daily number of rounds have been auto-released in the
  trailing 24 hours, skips the hold. It fails closed: an unknown count, a
  missing estimate, or a disabled cap all keep the hold.
- **Drain.** A round that left owed work behind because a cap stopped it — the
  per-round cell cap, or the reconciliation's case cap — asks for another round
  as soon as its own output has landed, rather than waiting for the next
  scheduled slot. A drained backlog, or a round stopped by anything else, asks
  for nothing.

The decision is pure: the counts come in as arguments, so the rule is testable
without the Actions API, and the workflow is responsible only for reading them.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from .config import ReviewHoldConfig


class HoldDecision(BaseModel):
    """The two answers a predict round's plan job routes on."""

    auto_release: bool
    auto_release_reason: str
    drain_more: bool
    drain_reason: str
    estimated_spend_usd: float | None


def _estimated_spend(plan: Mapping[str, Any]) -> float | None:
    """The plan's spend estimate, or ``None`` when it is not a usable number.

    A boolean, a string, a non-finite value (``json.loads`` accepts ``NaN`` and
    ``Infinity``) or a negative one is no estimate at all, so it keeps the hold
    rather than comparing as under the cap.
    """
    value = plan.get("estimated_spend_usd")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    estimate = float(value)
    if not math.isfinite(estimate) or estimate < 0:
        return None
    return estimate


def _auto_release(
    estimate: float | None,
    config: ReviewHoldConfig,
    released_last_day: int | None,
) -> tuple[bool, str]:
    if config.auto_release_usd_per_round <= 0 or config.auto_release_rounds_per_day <= 0:
        return False, "auto-release is disabled (review_hold caps are 0)"
    if released_last_day is None:
        return False, "the count of rounds auto-released in the last 24h could not be read"
    if released_last_day >= config.auto_release_rounds_per_day:
        return False, (
            f"{released_last_day} round(s) already auto-released in the last 24h "
            f"(daily cap {config.auto_release_rounds_per_day})"
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
        f"${config.auto_release_usd_per_round:,.2f}, round {released_last_day + 1} of "
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
) -> HoldDecision:
    """Decide auto-release and drain for one round's ``predict-plan`` document.

    ``released_last_day`` is how many rounds were auto-released in the trailing
    24 hours, or ``None`` when it could not be read — which keeps the hold.
    """
    estimate = _estimated_spend(plan)
    release, release_reason = _auto_release(estimate, config, released_last_day)
    drain, drain_reason = _drain(plan)
    return HoldDecision(
        auto_release=release,
        auto_release_reason=release_reason,
        drain_more=drain,
        drain_reason=drain_reason,
        estimated_spend_usd=estimate,
    )
