"""The ex-post spend backstop — measured cost as a gate on minting new cells.

Every other cost control bounds one decision or one run; this one reads the
committed ``usage.json`` ledger over a trailing window and defers new cells once a
configured ceiling is reached. Disabled by default, and a breach must always defer
rather than destroy: the predict queue and the evaluate backlog re-derive their
work from committed state on a later cycle.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from fedcourtsai.config import SpendConfig
from fedcourtsai.schemas import Engine, ModelUsage, UsageRole
from fedcourtsai.serialize import write_json
from fedcourtsai.spend import check_spend, trailing_spend

NOW = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


def _usage(
    data_root: Path,
    *,
    docket: int,
    cost: float,
    created_at: datetime,
    role: UsageRole = UsageRole.predictor,
    actor: str = "claude-baseline",
) -> None:
    """Commit one ``usage.json`` at the ledger path the roll-up globs."""
    seam = "predictions" if role == UsageRole.predictor else "evaluations"
    run_id = created_at.strftime("%Y%m%dT%H%M%SZ")
    record = ModelUsage(
        case_id=f"scotus/{docket}",
        event_id="evt-petition-disposition",
        run_id=run_id,
        role=role,
        actor_id=actor,
        engine=Engine.claude_code,
        model="claude-fable-5",
        created_at=created_at,
        input_tokens=1000,
        output_tokens=100,
        estimated_cost_usd=cost,
    )
    path = (
        data_root
        / "cases"
        / "scotus"
        / str(docket)
        / "events"
        / "evt-petition-disposition"
        / seam
        / actor
        / run_id
        / "usage.json"
    )
    write_json(path, record)


def test_trailing_spend_sums_inside_the_window_and_ignores_older(tmp_path: Path) -> None:
    """The window is what bounds the sum — an older cell's cost has rolled off."""
    _usage(tmp_path, docket=1, cost=4.00, created_at=NOW - timedelta(days=2))
    _usage(tmp_path, docket=2, cost=1.50, created_at=NOW - timedelta(days=29))
    _usage(tmp_path, docket=3, cost=99.00, created_at=NOW - timedelta(days=31))

    spent, cells = trailing_spend(tmp_path, window_days=30, now=NOW)
    assert cells == 2
    assert spent == 5.50


def test_trailing_spend_counts_both_stages(tmp_path: Path) -> None:
    """The ceiling governs total inference spend, so a grading counts like a forecast."""
    _usage(tmp_path, docket=1, cost=3.00, created_at=NOW - timedelta(days=1))
    _usage(
        tmp_path,
        docket=1,
        cost=4.00,
        created_at=NOW - timedelta(hours=1),
        role=UsageRole.evaluator,
        actor="claude-judge",
    )
    spent, cells = trailing_spend(tmp_path, window_days=30, now=NOW)
    assert cells == 2
    assert spent == 7.00


def test_an_empty_ledger_is_zero_not_an_error(tmp_path: Path) -> None:
    """Reading must not create the ledger, and a fresh checkout has no cells."""
    assert trailing_spend(tmp_path, window_days=30, now=NOW) == (0.0, 0)


def test_a_zero_ceiling_disables_the_backstop_without_reading_the_ledger(tmp_path: Path) -> None:
    """The default is off: nothing is enforced, and the roll-up is never spent."""
    _usage(tmp_path, docket=1, cost=10_000.0, created_at=NOW)
    verdict = check_spend(tmp_path, SpendConfig(), now=NOW)
    assert verdict.enforced is False
    assert verdict.breached is False
    assert verdict.spent_usd == 0.0  # short-circuited before the ledger was read
    assert verdict.cells == 0


def test_under_the_ceiling_reports_headroom_and_does_not_breach(tmp_path: Path) -> None:
    _usage(tmp_path, docket=1, cost=40.0, created_at=NOW - timedelta(days=1))
    verdict = check_spend(tmp_path, SpendConfig(ceiling_usd=100.0), now=NOW)
    assert verdict.enforced is True
    assert verdict.breached is False
    assert verdict.spent_usd == 40.0
    assert verdict.remaining_usd == 60.0


def test_reaching_the_ceiling_exactly_breaches(tmp_path: Path) -> None:
    """`>=`, not `>`: a ceiling is a limit reached, not one that must be exceeded."""
    _usage(tmp_path, docket=1, cost=100.0, created_at=NOW - timedelta(days=1))
    verdict = check_spend(tmp_path, SpendConfig(ceiling_usd=100.0), now=NOW)
    assert verdict.breached is True
    assert verdict.remaining_usd == 0.0


def test_spend_outside_the_window_does_not_breach(tmp_path: Path) -> None:
    """The window rolls off, which is what lets a deferred run resume on its own."""
    _usage(tmp_path, docket=1, cost=500.0, created_at=NOW - timedelta(days=45))
    verdict = check_spend(tmp_path, SpendConfig(ceiling_usd=100.0, window_days=30), now=NOW)
    assert verdict.breached is False
    assert verdict.cells == 0


def test_a_naive_created_at_is_read_as_utc(tmp_path: Path) -> None:
    """A hand-written ledger row must not crash the gate on a tz comparison."""
    _usage(
        tmp_path, docket=1, cost=5.0, created_at=datetime(2026, 7, 26, 12, 0)
    )  # naive on purpose
    spent, cells = trailing_spend(tmp_path, window_days=30, now=NOW)
    assert (spent, cells) == (5.0, 1)
