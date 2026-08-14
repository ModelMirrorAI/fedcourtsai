"""The mechanical integrity rules a scored cell must pass — clock and claim.

Two questions every scoring surface needs answered the same way, in one leaf
module so no join can answer them differently:

**Whose clock says when a cell ran?** The pre-registration boundary must not
rest on a clock the agent controls (:mod:`fedcourtsai.process_version` states
the rule for the freeze partition), and the stratum boundary is the same kind
of boundary: a predictor that back-dated its ``created_at`` to before a
resolution would otherwise classify as a forward forecast. :func:`cell_clock`
prefers the harness-written process stamp and falls back to the agent-written
``created_at`` only where no stamp exists — and an unstamped cell is outside
the frozen headline by construction (``is_frozen`` refuses a null), so the
fallback only ever positions cells inside diagnostic views. Never the git
commit timestamp: the stratified join is documented deterministic and offline
over committed artifacts, and a git read would break that.

**May the cell's forward claim be believed?** A cell whose harness-written
record says ``mode: forward`` while its event had already resolved when the
harness ran it is not a forecast — the claim and the record contradict each
other, and no stratum is a valid home for the observation
(:func:`forward_claim_breach`). What happens to such a cell is the
pre-registered :data:`FORWARD_CLAIM_POLICY`; the boards publish the policy and
the count beside their numbers so an exclusion can never be silent.

Everything here is derived from committed, harness-written artifacts — the
context and the stamp are the harness's fields (AGENTS.md), the outcome is the
docket record — so the rules are properties of the record, never of predictor
behavior.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from .schemas import ForwardClaimRecord, Outcome, Prediction

#: What the scoring funnel does with a cell whose forward claim its own record
#: contradicts. ``"exclude"`` (the pre-registered value) drops the cell from
#: every scored stratum: the retrospective stratum is the iteration signal,
#: measured over cells that were *told* they were retrospective and held to
#: replay etiquette, and a cell that believed it was forward degrades exactly
#: that signal. ``"retrospective"`` instead forces the cell into the
#: retrospective stratum while still counting it on the board. A maintainer
#: moves this in a reviewed commit, the ``FROZEN_*`` pattern; the boards
#: record which policy built them, so a flip is one commit plus a refresh.
ForwardClaimPolicy = Literal["exclude", "retrospective"]
FORWARD_CLAIM_POLICY: ForwardClaimPolicy = "exclude"


def cell_clock(prediction: Prediction) -> datetime:
    """When the harness ran this cell: the process stamp, else ``created_at``.

    Normalized to an aware datetime (a bare timestamp reads as UTC — the only
    zone any writer in this pipeline uses), so clocks from different writers
    always compare.
    """
    stamped = (
        prediction.process_version.stamped_at if prediction.process_version is not None else None
    )
    clock = stamped if stamped is not None else prediction.created_at
    return clock if clock.tzinfo is not None else clock.replace(tzinfo=UTC)


def forward_claim_breach(prediction: Prediction, outcome: Outcome) -> str | None:
    """Why this cell's own harness record contradicts its forward claim.

    ``None`` unless the harness-written context claims ``forward`` **and** the
    event had already resolved when the harness ran the cell
    (:func:`cell_clock`, date-resolution — the conservative same-day reading
    the stratum boundary also takes). A null-context cell cannot breach: it
    asserts nothing, and the clock alone already routes it retrospective
    wherever it ran late. A ``replay`` cell cannot breach: running after the
    resolution is its design.
    """
    context = prediction.context
    if context is None or context.mode != "forward":
        return None
    resolved_at = outcome.resolved_at
    clock_date = cell_clock(prediction).date()
    if resolved_at <= clock_date:
        return (
            f"the record claims a forward cell, but the event resolved "
            f"{resolved_at.isoformat()} — on or before the cell's harness clock "
            f"({clock_date.isoformat()})"
        )
    return None


def forward_claim_record(excluded: int) -> ForwardClaimRecord:
    """The record every scoring surface publishes beside its numbers."""
    return ForwardClaimRecord(policy=FORWARD_CLAIM_POLICY, excluded=excluded)
