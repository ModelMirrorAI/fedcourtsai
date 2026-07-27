"""The ex-post spend backstop: measured cost as a gate, not just a report.

Every other inference-cost control in the pipeline is **ex ante** — it bounds one
decision or one run: the salience gate's capacity ``N``, the per-run cell cap
(:func:`fedcourtsai.matrix.cap_predict_cells`), the live cycle's sweep cap, the
per-cell attempt cap. None of them reads what has actually been spent, so they
compose into a per-run limit with no per-period limit above it: with several
scheduled windows a day, a day's spend is bounded only by how many cells happen
to be owed — exactly the quantity that becomes large at a long conference.

This module closes that: it sums the committed ``usage.json`` ledger over a
trailing window and answers whether a configured ceiling has been reached. The
plan seams consult it before minting a matrix, so a breach **defers** work
(the queue is untouched and re-runs next cycle) rather than destroying it —
the same posture as the volume cap.

Two properties worth stating, because they bound what this can promise:

- **The ledger lags.** A cell's ``usage.json`` reaches ``data/`` only when its
  run's collect PR merges, so spend already incurred but not yet committed is
  invisible here. The ceiling is therefore a floor on what has been spent, and
  should be set with that lag in mind rather than read as real-time.
- **It is deliberately blunt.** It does not attribute, forecast, or pro-rate; it
  is the control that holds when a *different* control has failed, which is the
  one job it has to do reliably.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .config import SpendConfig
from .store import iter_usage


@dataclass(frozen=True)
class SpendVerdict:
    """What the trailing ledger says, and whether it bars minting new cells.

    ``enforced`` is ``False`` when no ceiling is configured, which is the default:
    the backstop then reports nothing and blocks nothing, so adopting it is opt-in
    and a missing config can never wedge the pipeline. ``breached`` is only ever
    ``True`` when a ceiling is actually in force.
    """

    spent_usd: float
    ceiling_usd: float
    window_days: int
    cells: int
    enforced: bool

    @property
    def breached(self) -> bool:
        """Whether an enforced ceiling has been reached (``>=``, not ``>``)."""
        return self.enforced and self.spent_usd >= self.ceiling_usd

    @property
    def remaining_usd(self) -> float:
        """Headroom left under the ceiling, floored at zero (``0.0`` unenforced)."""
        if not self.enforced:
            return 0.0
        return max(0.0, self.ceiling_usd - self.spent_usd)


def trailing_spend(
    data_root: Path, *, window_days: int, now: datetime | None = None
) -> tuple[float, int]:
    """Estimated cost and cell count recorded in the ledger over the trailing window.

    Sums ``estimated_cost_usd`` across every ``usage.json`` whose ``created_at``
    falls within ``window_days`` of ``now`` — predict and evaluate alike, since the
    ceiling governs total inference spend rather than one stage's. A record with a
    naive ``created_at`` is read as UTC, so a hand-written ledger row cannot crash
    the gate on a comparison.
    """
    cutoff = (now or datetime.now(UTC)) - timedelta(days=window_days)
    total = 0.0
    cells = 0
    for record in iter_usage(data_root):
        created = record.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        if created >= cutoff:
            total += record.estimated_cost_usd
            cells += 1
    return total, cells


def check_spend(
    data_root: Path, config: SpendConfig, *, now: datetime | None = None
) -> SpendVerdict:
    """The gate the plan seams call: is there budget left to mint a matrix?

    A ceiling of ``0`` disables the backstop entirely (the documented convention
    the other caps use), and short-circuits before the ledger is read so the
    default path costs nothing.
    """
    if config.ceiling_usd <= 0:
        return SpendVerdict(0.0, 0.0, config.window_days, 0, enforced=False)
    spent, cells = trailing_spend(data_root, window_days=config.window_days, now=now)
    return SpendVerdict(spent, config.ceiling_usd, config.window_days, cells, enforced=True)
