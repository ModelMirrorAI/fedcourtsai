"""Whether a spend round may skip the `review` hold, and whether to chain another.

The `review` hold is the per-round spend gate: every predict, evaluate,
summarize and topic-label round renders its plan and waits for a maintainer to
release it.
Two decisions read that same plan, and both are made here so the workflow only
routes on their answers:

- **Auto-release.** A round skips the hold when its priced plan is under the
  per-round cap, fewer than the daily number of rounds have been
  auto-released in the trailing 24 hours across the lanes, and the
  round's projected spend keeps the trailing-window total under the
  auto-release budget (below). It fails closed: an unknown count, an unread
  ledger, a missing estimate, a matrix that disagrees with the plan, a budget
  that does not sit below the spend backstop's ceiling, or a disabled knob all
  keep the hold. A label round also keeps it when the newest gated labeling
  run of its frame was refused at the reference gate — a retry of a refused
  batch waits for a maintainer's release — and while the frame's open labels
  PR holds an unmerged published batch, which another round would re-label.
- **Drain.** A predict round that left owed work behind because a cap stopped
  it — the per-round cell cap, or the reconciliation's case cap — asks for
  another round as soon as its own output has landed, rather than waiting for
  the next scheduled slot. A drained backlog, a round stopped by anything else,
  or a round of another lane asks for nothing.

**The budget is a projection over measured spend.** A round is released only
when ``measured + in_flight + estimate <= auto_release_budget_usd``, where
*measured* is the committed spend over the spend backstop's trailing window
(``tracking.yaml``'s ``spend.window_days``) — the same total the backstop sums
(:func:`fedcourtsai.spend.measured_spend`): every ``usage.json`` on the ledger,
the usage every committed case summary's front matter records, and every
topic-labeler run's spend record; *in_flight* is the rounds auto-released in the
last 24 hours times the per-round cap, an allowance for the *estimated* spend
of released rounds that have not reached the ledger yet (a collect PR lands
only once its checks pass) — not a bound on actual spend, which can exceed a
round's planning-rate price with its engine mix, nor on a round released
earlier whose collect PR is still open; and *estimate* is this round's price.
The ledger is a floor on what was spent — a manually released round still in
flight, an auto-released round whose collect PR is still open more than 24
hours on, a summary run whose review PR has not merged (outside the summarize
plan, which carries the open refresh PR's summaries and so counts them), and a
rejected summary response's tokens, and a labeler run's record whose
reviewed PR has not merged (outside that frame's next label round, whose
extract job carries the open PR's records in and so counts them) are all
invisible to it — so the budget sits below the backstop's ceiling, which
stops minting outright, and a budget at or above that ceiling keeps every
round on the hold rather than being adopted silently.

**What is priced is what runs.** A predict or evaluate plan document is a
second walk of the backlog; the cells that actually spend are the matrix the
first walk minted. The two are built by the same helpers but nothing forces
them to agree, so such a round auto-releases only when the matrix holds exactly
the plan's would-mint cell count, and its price is the larger of the plan's
estimate and the matrix's own cells priced at the same planning rates
(:mod:`fedcourtsai.planning_rates`). A summarize or label round has no
matrix: its spend job runs the plan document itself, so the price is the
plan's upper estimate.

**The daily count has two sources.** Each auto-released round leaves a
deployment to the `review-auto` environment, which every lane shares, and its
collect or publish commit carries the auto-released mark in its subject
(:data:`fedcourtsai.collect.AUTO_RELEASED_MARKER`) on its way to `main`. A
write holder can prune the deployment list; `main`'s history is append-only.
The count is the larger of the two, and an unreadable source keeps the hold.

The decision is pure: the counts, the matrix, the measured spend and the
commit subjects come in as arguments, so the rule is testable without the
Actions API, and the workflow is responsible only for reading them. The caps'
model and loader, and the glue that turns the files the workflow read into
those arguments (:func:`decide_from_files`), live here too, so everything that
decides whether a round spends unattended sits in one code-owned module and
the CLI only parses options.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, get_args

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .collect import AUTO_RELEASED_MARKER
from .config import SpendConfig, load_spend_config
from .pipeline.qp_topics import run_spend_dir
from .planning_rates import price_cells
from .schemas import QpTopicFrame, QpTopicRunSpend
from .serialize import read_model
from .spend import MeasuredSpend, iter_labeler_runs
from .spend import measured_spend as _measured_spend

__all__ = ["SEAMS", "MeasuredSpend"]

#: The lanes whose rounds the review hold may auto-release. The back-test is
#: not one: its replay always waits on a maintainer's release.
Seam = Literal["predict", "evaluate", "summarize", "label"]
SEAMS: tuple[Seam, ...] = get_args(Seam)

#: The seams priced from a plan document alone: no matrix, no drain.
_PLAN_PRICED: frozenset[str] = frozenset({"summarize", "label"})


class ReviewHoldConfig(BaseModel):
    """When a spend round may skip the `review` hold (``config/review-hold.yaml``).

    The hold is the per-round spend gate: a maintainer releases each round's plan
    before a cell spends. Auto-release lets a predict, evaluate, summarize or
    label round skip that wait, so the lanes drain without a human releasing every
    cycle. It is bounded three times — per round by estimated spend, per day by
    the number of rounds released this way, and over the spend backstop's
    trailing window by projected total spend — and anything past any bound
    still waits on the hold. The ex-post backstop (`spend`) stands behind all
    three.
    """

    model_config = ConfigDict(extra="ignore")

    # A round whose plan estimates at most this much spend, USD, is released
    # without the hold. `0` DISABLES auto-release (the convention the other caps
    # use), which is the default: every round waits on the hold until a
    # maintainer adopts a value. It is also the in-flight allowance per round
    # released in the last 24 hours in the budget projection.
    # At most $250: a sanity bound above the largest committed round, so a
    # slipped decimal ("750" for "7.50") is refused at load rather than adopted.
    auto_release_usd_per_round: float = Field(default=0.0, ge=0.0, le=250.0, allow_inf_nan=False)
    # At most this many rounds, across the predict, evaluate, summarize and
    # label lanes together, are auto-released in any trailing 24 hours; the next one
    # waits on the hold. `0` disables auto-release too. The daily bound on
    # unattended *estimated* spend is therefore at most this times the
    # per-round cap.
    # At most 100: the plan jobs read one page of the deployments they count.
    auto_release_rounds_per_day: int = Field(default=0, ge=0, le=100)
    # The trailing-window budget on total model spend, USD, over the spend
    # backstop's window (`tracking.yaml` `spend.window_days`). A round is
    # released only when measured spend plus the in-flight bound plus its own
    # estimate stays within it. `0` disables auto-release too. A budget at or
    # above the backstop's ceiling keeps every round on the hold.
    auto_release_budget_usd: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)


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


_MARK = re.escape(AUTO_RELEASED_MARKER)

#: An auto-released round's commit subject on `main`, one pattern per form.
#: A predict or evaluate collect PR lands as a merge commit whose subject is
#: the PR title — ``evaluate: N evaluation(s) (run <id>) [auto-released] (#N)``
#: — over the ready commit it merges, whose subject is the collect commit
#: message — ``predict(run <id>): N prediction(s) [auto-released]``. The
#: workflows read every commit reachable from `main` whose committer date is
#: within the window, second parents included. The merge commit is dated when
#: the PR landed and anchors the window; the ready commit, dated when it was
#: built, counts on its own only beneath a merge subject that carries no mark.
#: One run id is one round either way, and it is read wherever it sits,
#: before the mark. A summarize publish commit names its Actions run —
#: ``data(summaries): N plain-language case summaries (run <n>) [auto-released]``
#: — and its review PR is merged by hand, under the repository's default merge
#: subject, which is the PR title (docs/security.md) so the mark lands dated at
#: the merge as the unattended lanes' does. A topic-label publish commit has the
#: same shape under its own scope — ``data(qp-topics): batch N — … (run <n>)
#: [auto-released]`` for a labels PR, or a spend record's title for a run that
#: published nothing — and is merged by hand the same way.
_AUTO_RELEASED_SUBJECTS = (
    re.compile(
        r"^(?P<lane>predict|evaluate)\b.*?\brun (?P<run>\d{8}T\d{6}Z)\b.*" + _MARK,
    ),
    re.compile(r"^data\((?P<scope>summaries|qp-topics)\):.*?\(run (?P<run>\d+)\).*" + _MARK),
)

#: The lane a ``data(<scope>):`` publish subject belongs to.
_SCOPE_LANES = {"summaries": "summarize", "qp-topics": "label"}


class HoldDecision(BaseModel):
    """The answers a round's plan job routes on, with the figures behind them."""

    seam: Seam
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
    #: The budget arithmetic: ``None`` wherever a figure could not be read.
    budget_usd: float
    window_days: int | None
    measured_cells_usd: float | None
    measured_summaries_usd: float | None
    measured_labeler_usd: float | None = None
    in_flight_bound_usd: float | None
    projected_spend_usd: float | None


def count_auto_released(subjects: Iterable[str]) -> int:
    """How many distinct rounds ``subjects`` mark as auto-released, all lanes.

    ``subjects`` are commit subjects (first lines) from `main` over the trailing
    24 hours. Counted by lane and run id, so a rerun's second commit for one
    round does not count it twice.
    """
    runs: set[tuple[str, str]] = set()
    for subject in subjects:
        for pattern in _AUTO_RELEASED_SUBJECTS:
            match = pattern.match(subject.strip())
            if match:
                groups = match.groupdict()
                lane = groups.get("lane") or _SCOPE_LANES[groups["scope"]]
                runs.add((lane, match.group("run")))
                break
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


def measured_spend(
    data_root: Path, *, window_days: int, now: datetime | None = None
) -> MeasuredSpend | None:
    """The committed spend over the trailing window, or ``None`` if unreadable.

    The backstop's own total (:func:`fedcourtsai.spend.measured_spend`). A
    missing ledger reads as unreadable rather than as nothing spent: a plan job
    whose checkout lost ``data/`` must not see an empty budget.
    """
    if not (data_root / "cases").is_dir():
        return None
    try:
        measured, _ = _measured_spend(data_root, window_days=window_days, now=now)
    except (OSError, ValueError):
        return None
    return measured


def label_refusal(data_root: Path, frame: str, *, now: datetime | None = None) -> str | None:
    """Why a label round of ``frame`` keeps the hold after a refusal, or ``None``.

    Reads the labeler's run records (``data/qp-topics/spend/``, with any the
    extract job carried from the frame's open, unmerged PR): when the newest
    gated run of the frame — ``published`` or ``refused``, by ``recorded_at`` —
    was refused, a retry waits for a maintainer. An ``incomplete`` run was never
    gated, so it neither sets nor clears the refusal, and neither does a
    ``replicate``: it measured the reference block and published nothing by
    design, so a replicate dispatched after a refusal cannot release the next
    labeling round. A record that will not
    read keeps the hold, and so does one of the frame's records dated after
    ``now`` (this round's plan): a record from the future is not one a run
    wrote, and a forged ``published`` one would otherwise mask a refusal.
    """
    try:
        runs = iter_labeler_runs(data_root)
    except (OSError, ValueError):
        return "the labeler's run records could not be read"
    moment = now if now is not None else datetime.now(UTC)
    if any(run.frame == frame and run.recorded_at > moment for run in runs):
        return (
            f"a {frame} labeling run record is dated after this round's plan, so the records "
            "cannot be trusted to name the last gated run"
        )
    gated = [run for run in runs if run.frame == frame and run.outcome in ("published", "refused")]
    if not gated:
        return None
    newest = max(gated, key=lambda run: (run.recorded_at, int(run.run_id), run.run_attempt))
    if newest.outcome == "refused":
        return (
            f"the last {frame} labeling run was refused at the reference gate; a retry waits "
            "for a maintainer's release"
        )
    return None


def label_pending(data_root: Path, frame: str, carried: Iterable[str]) -> str | None:
    """Why a label round of ``frame`` keeps the hold while a batch awaits review, or ``None``.

    ``carried`` names the run records the extract job carried in from the
    frame's open, unmerged labels PR. When one of them is a ``published`` run of
    the frame, that PR holds a batch ``main`` has not merged: the next batch is
    cut from ``main``'s labels file, so it would label the same rows again, pay
    for them again, and replace the PR on its fixed branch. A carried record
    that will not read keeps the hold too.
    """
    for entry in carried:
        name = Path(entry.strip()).name
        if not name:
            continue
        try:
            run = read_model(run_spend_dir(data_root) / name, QpTopicRunSpend)
        except (OSError, ValueError):
            return "a run record carried from the open labels PR could not be read"
        if run.frame == frame and run.outcome == "published":
            return (
                f"the open {frame} labels PR holds an unmerged published batch (run "
                f"{run.run_id}); another round would re-label it and replace that PR, so it "
                "waits for a maintainer's release"
            )
    return None


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0:
        return None
    return number


def _plan_cells(plan: Mapping[str, Any], seam: Seam) -> int | None:
    if seam == "summarize":
        cases = plan.get("cases")
        return len(cases) if isinstance(cases, list) else None
    if seam == "label":
        rows = plan.get("rows")
        if isinstance(rows, bool) or not isinstance(rows, int) or rows <= 0:
            return None
        return rows
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


def _price(
    plan: Mapping[str, Any], matrix: list[Mapping[str, Any]] | None, seam: Seam
) -> float | None:
    """The round's price: for a summarize or label round its plan's upper
    estimate, else the larger of the plan's estimate and the matrix's own
    priced cells.

    A missing, boolean, non-finite or negative plan estimate is no estimate at
    all, so it keeps the hold rather than comparing as under the cap.
    """
    if seam in _PLAN_PRICED:
        return _number(plan.get("estimated_cost_usd_high"))
    estimate = _number(plan.get("estimated_spend_usd"))
    if estimate is None:
        return None
    if matrix is None:
        return estimate
    priced, _ = price_cells(matrix, seam=seam)
    return max(estimate, round(priced, 2))


@dataclass(frozen=True)
class _Budget:
    """The projection a round is released against, with whatever was readable."""

    window_days: int | None
    measured: MeasuredSpend | None
    in_flight: float | None
    projected: float | None


def _project(
    config: ReviewHoldConfig,
    backstop: SpendConfig | None,
    measured: MeasuredSpend | None,
    released: int | None,
    estimate: float | None,
) -> _Budget:
    in_flight = None if released is None else round(released * config.auto_release_usd_per_round, 2)
    projected = (
        None
        if measured is None or in_flight is None or estimate is None
        else round(measured.total_usd + in_flight + estimate, 2)
    )
    return _Budget(
        window_days=None if backstop is None else backstop.window_days,
        measured=measured,
        in_flight=in_flight,
        projected=projected,
    )


def _arithmetic(
    config: ReviewHoldConfig,
    budget: _Budget,
    measured: MeasuredSpend,
    projected: float,
    released: int,
    estimate: float,
) -> str:
    return (
        f"projected trailing {budget.window_days}-day spend ${projected:,.2f} = "
        f"measured ${measured.total_usd:,.2f} (agent cells ${measured.cells_usd:,.2f} + "
        f"case summaries ${measured.summaries_usd:,.2f} + labeler runs "
        f"${measured.labeler_usd:,.2f}) + in flight up to "
        f"${budget.in_flight or 0.0:,.2f} ({released} round(s) auto-released in the last "
        f"24h x ${config.auto_release_usd_per_round:,.2f}) + this round ${estimate:,.2f}"
    )


def _auto_release(  # noqa: PLR0911, PLR0912, PLR0913 - one return per fail-closed reason
    seam: Seam,
    estimate: float | None,
    config: ReviewHoldConfig,
    backstop: SpendConfig | None,
    released: int | None,
    plan_cells: int | None,
    matrix: list[Mapping[str, Any]] | None,
    budget: _Budget,
    *,
    refusal: str | None,
) -> tuple[bool, str]:
    if (
        config.auto_release_usd_per_round <= 0
        or config.auto_release_rounds_per_day <= 0
        or config.auto_release_budget_usd <= 0
    ):
        return False, (
            "auto-release is disabled (review-hold.yaml: per-round cap "
            f"${config.auto_release_usd_per_round:,.2f}, "
            f"{config.auto_release_rounds_per_day} round(s) a day, trailing budget "
            f"${config.auto_release_budget_usd:,.2f}; any 0 disables it)"
        )
    if backstop is None:
        return False, "the spend backstop's settings (tracking.yaml `spend`) could not be read"
    if backstop.ceiling_usd <= 0:
        return False, (
            "the spend backstop is off (tracking.yaml spend.ceiling_usd is 0), so nothing "
            "ex post stands behind an unattended round"
        )
    if config.auto_release_budget_usd >= backstop.ceiling_usd:
        return False, (
            f"the auto-release budget ${config.auto_release_budget_usd:,.2f} is not below the "
            f"spend backstop's ceiling ${backstop.ceiling_usd:,.2f} (tracking.yaml), so it "
            "bounds nothing the backstop does not; lower the budget below the ceiling"
        )
    if released is None:
        return False, "the count of rounds auto-released in the last 24h could not be read"
    if released >= config.auto_release_rounds_per_day:
        return False, (
            f"{released} round(s) already auto-released in the last 24h across the lanes "
            f"(daily cap {config.auto_release_rounds_per_day})"
        )
    if seam == "summarize":
        if plan_cells is None:
            return False, "the plan's case list could not be read"
    elif seam == "label":
        if plan_cells is None:
            return False, "the plan's row count could not be read"
        if refusal is not None:
            return False, refusal
    else:
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
    if budget.measured is None or budget.projected is None:
        return False, (
            "the committed spend ledger (usage.json, case-summary usage and labeler run "
            "records) could not be "
            f"read, so the trailing {backstop.window_days}-day spend is unknown"
        )
    arithmetic = _arithmetic(config, budget, budget.measured, budget.projected, released, estimate)
    if budget.projected > config.auto_release_budget_usd:
        return False, (
            f"{arithmetic} is over the ${config.auto_release_budget_usd:,.2f} auto-release budget"
        )
    return True, (
        f"estimated spend ${estimate:,.2f} is within the per-round cap "
        f"${config.auto_release_usd_per_round:,.2f}, round {released + 1} of "
        f"{config.auto_release_rounds_per_day} in the last 24h, and {arithmetic} is within "
        f"the ${config.auto_release_budget_usd:,.2f} auto-release budget"
    )


def _drain(plan: Mapping[str, Any], seam: Seam) -> tuple[bool, str]:
    if seam != "predict":
        return False, "only a predict round chains another"
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
    seam: Seam,
    released_last_day: int | None,
    matrix: Mapping[str, Any] | None,
    backstop: SpendConfig | None,
    measured: MeasuredSpend | None,
    label_refusal: str | None = None,
) -> HoldDecision:
    """Decide auto-release (and, for predict, drain) for one round's plan.

    ``released_last_day`` is the rounds auto-released in the trailing 24 hours
    across the lanes (:func:`released_last_day` over both sources), or ``None``
    when it could not be read — which keeps the hold. ``matrix`` is the
    `predict-matrix` / `evaluate-matrix` document the round minted, unread for a
    summarize round; ``None`` keeps a predict or evaluate round's hold.
    ``backstop`` is ``tracking.yaml``'s `spend` section and ``measured`` the
    committed spend over its window (:func:`measured_spend`); either ``None``
    keeps the hold. ``label_refusal`` is a label round's reason to hold after
    its frame's last gated run was refused (:func:`label_refusal`), ``None``
    when there is none; other seams ignore it.
    """
    cells = None if seam in _PLAN_PRICED else _matrix_cells(matrix)
    estimate = _price(plan, cells, seam)
    plan_cells = _plan_cells(plan, seam)
    budget = _project(config, backstop, measured, released_last_day, estimate)
    release, release_reason = _auto_release(
        seam,
        estimate,
        config,
        backstop,
        released_last_day,
        plan_cells,
        cells,
        budget,
        refusal=label_refusal if seam == "label" else None,
    )
    drain, drain_reason = _drain(plan, seam)
    return HoldDecision(
        seam=seam,
        auto_release=release,
        auto_release_reason=release_reason,
        drain_more=drain,
        drain_reason=drain_reason,
        estimated_spend_usd=estimate,
        released_last_day=released_last_day,
        plan_cells=plan_cells,
        matrix_cells=None if cells is None else len(cells),
        budget_usd=config.auto_release_budget_usd,
        window_days=budget.window_days,
        measured_cells_usd=None if measured is None else round(measured.cells_usd, 2),
        measured_summaries_usd=None if measured is None else round(measured.summaries_usd, 2),
        measured_labeler_usd=None if measured is None else round(measured.labeler_usd, 2),
        in_flight_bound_usd=budget.in_flight,
        projected_spend_usd=budget.projected,
    )


def _usd(value: float | None) -> str:
    return "unknown" if value is None else f"${value:,.2f}"


def render_summary(decision: HoldDecision) -> str:
    """The step-summary block a round's plan job publishes beside its plan report."""
    predict = decision.seam == "predict"
    lines = ["", "### Hold and drain" if predict else "### Hold"]
    if decision.auto_release:
        lines.append(f"- **Auto-released:** {decision.auto_release_reason}.")
    else:
        lines.append(f"- **Waits on the review hold:** {decision.auto_release_reason}.")
    measured = (
        None
        if decision.measured_cells_usd is None
        or decision.measured_summaries_usd is None
        or decision.measured_labeler_usd is None
        else decision.measured_cells_usd
        + decision.measured_summaries_usd
        + decision.measured_labeler_usd
    )
    window = "unknown" if decision.window_days is None else f"{decision.window_days}-day"
    lines.extend(
        [
            "",
            f"| Budget arithmetic (trailing {window} window) | USD |",
            "| --- | ---: |",
            f"| Measured: agent cells (`usage.json`) | {_usd(decision.measured_cells_usd)} |",
            f"| Measured: case summaries | {_usd(decision.measured_summaries_usd)} |",
            f"| Measured: topic-labeler runs | {_usd(decision.measured_labeler_usd)} |",
            f"| In flight: {_count(decision.released_last_day)} round(s) auto-released "
            f"in the last 24h x per-round cap | {_usd(decision.in_flight_bound_usd)} |",
            f"| This round's estimate | {_usd(decision.estimated_spend_usd)} |",
            f"| **Projected** | **{_usd(decision.projected_spend_usd)}** |",
            f"| Auto-release budget | {_usd(decision.budget_usd)} |",
            "",
        ]
    )
    if measured is None:
        lines.append("The measured spend could not be read, so the projection is unknown.")
        lines.append("")
    if predict:
        if decision.drain_more:
            lines.append(
                f"- **Another round is owed:** {decision.drain_reason}; it is dispatched once "
                "this round's collect PR merges, if the dispatch chain is on."
            )
        else:
            lines.append(f"- **No further round from this one:** {decision.drain_reason}.")
    return "\n".join(lines) + "\n"


def _count(value: int | None) -> str:
    return "unknown" if value is None else str(value)


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


def _read_backstop(config_root: Path) -> SpendConfig | None:
    """``tracking.yaml``'s `spend` section, or ``None`` — which keeps the hold."""
    try:
        return load_spend_config(config_root)
    except (OSError, ValueError, yaml.YAMLError):
        return None


def decide_from_files(  # noqa: PLR0913 - one argument per file the plan job read
    plan: Mapping[str, Any],
    config_root: Path,
    data_root: Path,
    *,
    seam: Seam,
    deployments_released: int | None,
    main_subjects_file: Path | None,
    matrix_file: Path | None,
    carried_file: Path | None = None,
    now: datetime | None = None,
) -> HoldDecision:
    """:func:`decide` over what the plan job read: the caps, the counts, the matrix, the ledger.

    Every input the workflow could not read arrives as ``None`` (or a file that
    will not parse) and keeps the hold; the caps come from
    ``config_root/review-hold.yaml``, the backstop's ceiling and window from
    ``config_root/tracking.yaml``, and the measured spend from the committed
    ledger under ``data_root``. A label round's frame is the plan's ``frame``,
    and the refusal rule reads that frame's run records there too;
    ``carried_file`` lists the records carried from the frame's open labels PR,
    one path per line, which the pending-batch rule reads (:func:`label_pending`).
    """
    backstop = _read_backstop(config_root)
    measured = (
        None
        if backstop is None
        else measured_spend(data_root, window_days=backstop.window_days, now=now)
    )
    return decide(
        plan,
        load_review_hold_config(config_root),
        seam=seam,
        released_last_day=released_last_day(
            deployments_released, _read_committed(main_subjects_file)
        ),
        matrix=None if seam in _PLAN_PRICED else _read_matrix(matrix_file),
        backstop=backstop,
        measured=measured,
        label_refusal=(
            _label_refusal_for(plan, data_root, carried_file=carried_file, now=now)
            if seam == "label"
            else None
        ),
    )


def _label_refusal_for(
    plan: Mapping[str, Any],
    data_root: Path,
    *,
    carried_file: Path | None = None,
    now: datetime | None = None,
) -> str | None:
    """Why a label plan's round keeps the hold on its frame's records, or ``None``.

    No frame keeps the hold; then a pending batch on the frame's open PR
    (:func:`label_pending`), then a refusal (:func:`label_refusal`).
    """
    frame = plan.get("frame")
    if frame not in get_args(QpTopicFrame):
        return "the plan names no labeling frame"
    if carried_file is not None:
        try:
            carried = carried_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            return "the list of run records carried from the open labels PR could not be read"
        pending = label_pending(data_root, str(frame), carried)
        if pending is not None:
            return pending
    return label_refusal(data_root, str(frame), now=now)
