"""The ex-post spend backstop: measured cost as a gate, not just a report.

Every other inference-cost control in the pipeline is **ex ante** — it bounds one
decision or one run: the salience gate's capacity ``N``, the per-run cell cap
(:func:`fedcourtsai.matrix.cap_predict_cells`), the live cycle's sweep cap, the
per-cell attempt cap. None of them reads what has actually been spent, so they
compose into a per-run limit with no per-period limit above it: with several
scheduled windows a day, a day's spend is bounded only by how many cells happen
to be owed — exactly the quantity that becomes large at a long conference.

This module closes that: it sums the committed spend ledger over a
trailing window and answers whether a configured ceiling has been reached. The
plan seams consult it before minting a matrix, so a breach **defers** work
(the queue is untouched and re-runs next cycle) rather than destroying it —
the same posture as the volume cap.

Two properties worth stating, because they bound what this can promise:

- **The ledger lags.** A cell's ``usage.json`` reaches ``data/`` only when its
  run's collect PR merges (a summary's or a labeler run's record when its
  reviewed PR does), so spend already incurred but not yet committed is
  invisible here. The ceiling is therefore a floor on what has been spent, and
  should be set with that lag in mind rather than read as real-time.
- **It is deliberately blunt.** It does not attribute, forecast, or pro-rate; it
  is the control that holds when a *different* control has failed, which is the
  one job it has to do reliably.

A breach defers rather than destroys, but deferral is not free. Two
consequences are worth stating here, because neither is visible in the verdict:

- **A deferred forward cell can lose its stratum.** Whether a cell is
  ``forward`` or ``retrospective`` is decided by its harness clock against the
  outcome's ``resolved_at`` (:func:`fedcourtsai.integrity.classify_stratum`),
  so a cell deferred past its event's resolution re-mints as a *retrospective*
  cell — still worth having, since retrospective cells measure calibration and
  label-mapping fit, but never evidence of forecasting skill, which only the
  forward stratum carries (``metrics/README.md``, *Forward vs retrospective*).
  The work is recoverable; the claim is not.
- **Every committed campaign draws on this same ceiling.** The window sums the
  whole committed ledger (:func:`fedcourtsai.store.iter_usage` walks every
  ``usage.json`` under ``data/cases``), so a re-forecast or re-grade campaign
  competes with the scheduled lanes for the same dollars rather than carrying a
  budget of its own. The back-test's replay is the one exception, and only
  because it writes to a scratch tree instead of ``data/`` — which makes its
  spend invisible here rather than exempt.

**One measured total, three sources.** What the backstop sums and what the
review hold's auto-release budget projects over are the same figure
(:func:`measured_spend`): every committed ``usage.json`` (the agent cells), the
usage each committed case summary's front matter records, and every topic
labeler run's spend record under ``data/qp-topics/spend/`` — refused and
incomplete runs included, since they spend as much as one that publishes. Each
is windowed on its own stamp: a cell's ``created_at``, a summary's
``generated_at``, a labeler run's ``recorded_at``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .config import SpendConfig
from .pipeline.qp_topics import run_spend_dir
from .schemas import ModelUsage, QpTopicRunSpend
from .serialize import read_model
from .store import iter_usage
from .summaries import parse_summary


@dataclass(frozen=True)
class SpendVerdict:
    """What the trailing ledger says, and whether it bars minting new cells.

    ``enforced`` is ``False`` when no ceiling is configured, which is the default:
    the backstop then reports nothing and blocks nothing, so adopting it is opt-in
    and a missing config can never wedge the pipeline. ``breached`` is only ever
    ``True`` when a ceiling is actually in force. ``spent_usd`` is the one
    measured total (:func:`measured_spend`); ``cells`` counts the agent-cell
    records inside it, the one source with a natural unit.
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


def spend_over(
    usage: Iterable[ModelUsage],
    *,
    window_days: int,
    now: datetime | None = None,
    since: datetime | None = None,
) -> tuple[float, int]:
    """Estimated cost and cell count among ``usage`` inside the window.

    The pure half of :func:`trailing_spend`, for a caller that has already read
    the ledger and would otherwise walk it again — the weekly digest prices
    several windows and counts a census over the same records, and a walk per
    figure over a growing tree is that many times the work and that many more
    chances for the figures to disagree about what they cover.

    ``since`` pins the cutoff to an instant instead of deriving it from
    ``window_days``, for a window whose start is a calendar boundary rather than
    a count of days back: an October Term opens at midnight on 1 October, and a
    cutoff taken as *N* days before a mid-morning digest would drop the Term's
    own first morning. ``window_days`` still names the span the caller reports.
    """
    cutoff = (
        since if since is not None else (now or datetime.now(UTC)) - timedelta(days=window_days)
    )
    total = 0.0
    cells = 0
    for record in usage:
        created = record.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        if created >= cutoff:
            total += record.estimated_cost_usd
            cells += 1
    return total, cells


def trailing_spend(
    data_root: Path, *, window_days: int, now: datetime | None = None
) -> tuple[float, int]:
    """Estimated cost and cell count the agent cells recorded over the trailing window.

    Sums ``estimated_cost_usd`` across every ``usage.json`` whose ``created_at``
    falls within ``window_days`` of ``now`` — predict and evaluate alike. A
    record with a naive ``created_at`` is read as UTC, so a hand-written ledger
    row cannot crash the gate on a comparison. The cells are one of the three
    sources :func:`measured_spend` sums.
    """
    return spend_over(iter_usage(data_root), window_days=window_days, now=now)


def _cutoff(window_days: int, now: datetime | None) -> datetime:
    return (now or datetime.now(UTC)) - timedelta(days=window_days)


def _aware(moment: datetime) -> datetime:
    return moment if moment.tzinfo is not None else moment.replace(tzinfo=UTC)


def summary_spend(data_root: Path, *, window_days: int, now: datetime | None = None) -> float:
    """The usage committed case summaries record, over the trailing window.

    Read from each summary's front matter (``usage.estimated_cost_usd``, by
    ``generated_at``). A summary written without usage adds nothing; a file
    that will not parse raises.
    """
    cutoff = _cutoff(window_days, now)
    total = 0.0
    for path in sorted((data_root / "cases").glob("*/*/summaries/*.md")):
        front, _ = parse_summary(path.read_text(encoding="utf-8"))
        if front.usage is not None and _aware(front.generated_at) >= cutoff:
            total += front.usage.estimated_cost_usd
    return total


def iter_labeler_runs(data_root: Path) -> list[QpTopicRunSpend]:
    """Every committed topic-labeler run record, in file order.

    A record that will not validate raises: the caller decides whether that
    keeps a hold or fails a gate, and a silently skipped record would read as
    spend that never happened.
    """
    return [
        read_model(path, QpTopicRunSpend)
        for path in sorted(run_spend_dir(data_root).glob("*.json"))
    ]


def labeler_spend(data_root: Path, *, window_days: int, now: datetime | None = None) -> float:
    """The spend the topic labeler's run records hold over the trailing window.

    Windowed on each record's ``recorded_at``.
    """
    cutoff = _cutoff(window_days, now)
    return sum(
        run.estimated_cost_usd
        for run in iter_labeler_runs(data_root)
        if _aware(run.recorded_at) >= cutoff
    )


@dataclass(frozen=True)
class MeasuredSpend:
    """Committed spend over the trailing window: agent cells, case summaries, labeler runs."""

    cells_usd: float
    summaries_usd: float
    labeler_usd: float = 0.0

    @property
    def total_usd(self) -> float:
        """Every source together."""
        return self.cells_usd + self.summaries_usd + self.labeler_usd


def measured_spend(
    data_root: Path,
    *,
    window_days: int,
    now: datetime | None = None,
    usage: Iterable[ModelUsage] | None = None,
) -> tuple[MeasuredSpend, int]:
    """The one measured total, and the cells counted in it, over the trailing window.

    ``usage`` is the cell ledger when a caller has already read it (the weekly
    digest walks it once for every figure); otherwise it is read here. Raises
    ``OSError`` or ``ValueError`` on a ledger that will not read.
    """
    cells, counted = spend_over(
        iter_usage(data_root) if usage is None else usage, window_days=window_days, now=now
    )
    return (
        MeasuredSpend(
            cells_usd=cells,
            summaries_usd=summary_spend(data_root, window_days=window_days, now=now),
            labeler_usd=labeler_spend(data_root, window_days=window_days, now=now),
        ),
        counted,
    )


def verdict_over(
    usage: Iterable[ModelUsage],
    config: SpendConfig,
    *,
    data_root: Path,
    now: datetime | None = None,
) -> SpendVerdict:
    """:func:`check_spend` over cell records a caller has already read."""
    if config.ceiling_usd <= 0:
        return SpendVerdict(0.0, 0.0, config.window_days, 0, enforced=False)
    measured, cells = measured_spend(
        data_root, window_days=config.window_days, now=now, usage=usage
    )
    return SpendVerdict(
        measured.total_usd, config.ceiling_usd, config.window_days, cells, enforced=True
    )


def check_spend(
    data_root: Path, config: SpendConfig, *, now: datetime | None = None
) -> SpendVerdict:
    """The gate the plan seams call: is there budget left to mint a matrix?

    Sums the one measured total (:func:`measured_spend`) — cells, case summaries
    and labeler runs. A ceiling of ``0`` disables the backstop entirely (the
    documented convention the other caps use), and short-circuits before the
    ledger is read so the default path costs nothing.
    """
    if config.ceiling_usd <= 0:
        return SpendVerdict(0.0, 0.0, config.window_days, 0, enforced=False)
    return verdict_over(iter_usage(data_root), config, data_root=data_root, now=now)
