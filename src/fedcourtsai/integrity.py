"""The mechanical integrity rules a scored cell must pass — clock, claim, stratum.

Three questions every scoring surface needs answered the same way, in one leaf
module so no join can answer them differently:

**Whose clock says when a cell ran?** The pre-registration boundary must not
rest on a clock the agent controls (:mod:`fedcourtsai.process_version` states
the rule for the freeze partition), and the stratum boundary is the same kind
of boundary: a predictor that back-dated its ``created_at`` to before a
resolution would otherwise classify as a forward forecast. :func:`cell_clock`
prefers the harness-written process stamp and falls back to the agent-written
``created_at`` only where no stamp exists — and an unstamped cell is outside
the frozen headline by construction (``is_frozen`` refuses a null), so the
fallback only ever positions cells — and adjudicates breaches — inside
diagnostic views, where an agent-movable clock costs a diagnostic row, never
a claim. Never the git
commit timestamp: the stratified join is documented deterministic and offline
over committed artifacts, and a git read would break that.

**May the cell's forward claim be believed?** A cell whose harness-written
record says ``mode: forward`` while its event had resolved before the harness
clock's day is not a forecast — the claim and the record contradict each
other, and no scored stratum is a valid home for the observation
(:func:`forward_claim_breach`). What happens to such a cell is the
pre-registered :data:`FORWARD_CLAIM_POLICY`; the boards publish the policy and
the count beside their numbers so an exclusion can never be silent.

**Which stratum does the cell belong to?** The pre-registration split is the
same question asked once more, and it rests on the same clock, so the
vocabulary lives here too: the :data:`FORWARD` / :data:`RETROSPECTIVE` /
:data:`PROCEDURAL` names, the :data:`StratifiedCell` tuple the join yields, and
:func:`classify_stratum`, the single definition of the timing boundary. The
leaderboard, the claim metrics, the ops report and the store's join all read
them from here rather than off the board, which is what lets
:mod:`fedcourtsai.store` — the module every artifact reader goes through —
stay clear of the board that is built on top of it.

Everything here is derived from committed, harness-written artifacts — the
context and the stamp are the harness's fields (AGENTS.md), the outcome is the
docket record — so the rules are properties of the record, never of predictor
behavior.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Literal

from .schemas import (
    Evaluation,
    ForwardClaimRecord,
    Moment,
    Outcome,
    Prediction,
    Stage,
    Stratum,
)

#: What the scoring funnel does with a cell whose forward claim its own record
#: contradicts. ``"exclude"`` (the registered value) drops the cell from
#: every scored stratum: the retrospective stratum is the iteration signal,
#: measured over cells the clock honestly places after their resolution —
#: replay cells held to replay etiquette, and late cells that never claimed
#: otherwise — and a cell that believed it was forward, retrieved
#: unrestricted, and asserted a false mode degrades exactly that signal.
#: ``"retrospective"`` instead forces the cell into the retrospective stratum
#: (procedural still wins for a mootness-basis outcome) while counting it on
#: the board. A maintainer
#: moves this in a reviewed commit, the ``FROZEN_*`` pattern; the boards
#: record which policy built them, so a flip is one commit plus a refresh.
ForwardClaimPolicy = Literal["exclude", "retrospective"]
FORWARD_CLAIM_POLICY: ForwardClaimPolicy = "exclude"

#: One joined cell as ``store.iter_stratified_evaluations`` yields it:
#: ``(evaluation, stratum, stage, moment)``. The stage and the moment travel
#: together because neither alone identifies the population a cell belongs to —
#: the stage names the question, the moment names the information set that
#: answered it.
StratifiedCell = tuple["Evaluation", "Stratum", "Stage | None", "Moment | None"]

FORWARD: Stratum = "forward"
RETROSPECTIVE: Stratum = "retrospective"
# Cells whose outcome was mootness practice (the outcome's disposition_basis):
# the ground-truth label tracks the Court's vacatur wording rather than
# cert-worthiness, so these aggregate separately and never enter the ranking.
PROCEDURAL: Stratum = "procedural"


def classify_stratum(prediction_clock: datetime, resolved_at: date) -> Stratum:
    """Which pre-registration stratum a scored cell belongs to.

    Retrospective when the event's resolution predates the prediction's
    **harness clock** (:func:`cell_clock` — the process stamp, else the
    unstamped cell's ``created_at``; the boundary must not rest on a clock the
    agent controls). A same-day tie also counts as retrospective — the
    conservative reading, so a cell whose ordering within the day is unknowable
    is never presented as a forward forecast.
    """
    return RETROSPECTIVE if resolved_at <= prediction_clock.date() else FORWARD


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
    event had resolved strictly before the cell's harness clock day
    (:func:`cell_clock`). A same-day tie is deliberately **not** a breach: the
    record is ambiguous there — an honest forward cell that lost a same-day
    race looks identical to a mis-provisioned one — so the tie falls to the
    stratum boundary's own conservative rule (same-day counts as
    retrospective) rather than to exclusion. A null-context cell cannot
    breach: it asserts nothing, and the clock alone already routes it
    retrospective wherever it ran late. A ``replay`` cell cannot breach:
    running after the resolution is its design.
    """
    context = prediction.context
    if context is None or context.mode != "forward":
        return None
    resolved_at = outcome.resolved_at
    clock_date = cell_clock(prediction).date()
    if resolved_at < clock_date:
        return (
            f"the record claims a forward cell, but the event resolved "
            f"{resolved_at.isoformat()} — before the cell's harness clock day "
            f"({clock_date.isoformat()})"
        )
    return None


def forward_claim_record(
    excluded: Sequence[tuple[str, str]] | int, claimed_forward: int = 0
) -> ForwardClaimRecord:
    """The record every scoring surface publishes beside its numbers.

    ``excluded`` is the exclusion ledger's ``(predictor_id, reason)`` pairs
    (a bare count is accepted where a caller has only the number and no
    per-predictor split to publish).
    """
    if isinstance(excluded, int):
        return ForwardClaimRecord(
            policy=FORWARD_CLAIM_POLICY, excluded=excluded, claimed_forward=claimed_forward
        )
    by_predictor: dict[str, int] = {}
    for predictor_id, _reason in excluded:
        by_predictor[predictor_id] = by_predictor.get(predictor_id, 0) + 1
    return ForwardClaimRecord(
        policy=FORWARD_CLAIM_POLICY,
        excluded=len(excluded),
        claimed_forward=claimed_forward,
        by_predictor=dict(sorted(by_predictor.items())),
    )
