"""The records a supersession or a revocation owes: the successor's disclosures,
and a revoked window's figures over its resolved slice.

A patched registry: alpha's proc-a window closes at T2 and proc-b opens; beta's
digest carries forward, so its proc-a window stays open across both.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import CellFailure, CountingWindow, ProcessVersion
from fedcourtsai.serialize import write_json
from fedcourtsai.window_records import (
    WindowRecordError,
    revoked_window_board,
    successor_disclosures,
)
from tests.conftest import set_windows
from tests.test_dataset_export import _event, _grade, _outcome, _prediction

A = "sha256:" + "a" * 64
B = "sha256:" + "b" * 64
D = "sha256:" + "d" * 64
JUDGE = "sha256:" + "9" * 64
T1 = datetime(2026, 1, 1, tzinfo=UTC)
T2 = datetime(2026, 4, 1, tzinfo=UTC)
CLOSED = CountingWindow(label="proc-a", digest=A, opens=T1, closes=T2)
SUCCESSOR = CountingWindow(label="proc-b", digest=B, opens=T2)
BETA = CountingWindow(label="proc-a", digest=D, opens=T1)
EVENT = "evt-petition-disposition"


def _pv(digest: str, when: datetime) -> ProcessVersion:
    return ProcessVersion(label="proc-x", digest=digest, stamped_at=when)


def _cell(
    data: Path, case: str, predictor: str, digest: str, when: datetime, run: str = "p1"
) -> None:
    _event(data, case)
    _prediction(data, case, predictor_id=predictor, run_id=run, stamp=_pv(digest, when))


def _failure(data: Path, case: str, predictor: str, run_id: str) -> None:
    court, _, docket = case.partition("/")
    event = CasePaths(data, court, int(docket)).event(EVENT)
    write_json(
        event.predictions_dir / predictor / run_id / "attempt.json",
        CellFailure(
            seam="predict",
            actor=predictor,
            court=court,
            docket=int(docket),
            event_id=EVENT,
            run_id=run_id,
            error_class="no_output",
        ),
    )


def _ledger(data: Path) -> None:
    """Four events, one per shape the disclosures tell apart.

    1: both engines in proc-a, resolved before the close.
    2: alpha's proc-a cell, pending at the close (resolved after it).
    3: alpha in the successor; its closed window recorded a failed attempt.
    4: alpha in the successor, beta reached it before the close, alpha's closed
       window left nothing — a missing earlier-window attempt.
    """
    _cell(data, "scotus/1", "alpha", A, T1 + timedelta(days=1))
    _cell(data, "scotus/1", "beta", D, T1 + timedelta(days=1))
    _outcome(data, "scotus/1", resolved_at=(T1 + timedelta(days=30)).date())
    _grade(data, "scotus/1", "e1", predictor_id="alpha", stamped=T1 + timedelta(days=31))
    _grade(data, "scotus/1", "e1", predictor_id="beta", stamped=T1 + timedelta(days=31))
    _cell(data, "scotus/2", "alpha", A, T1 + timedelta(days=2))
    _outcome(data, "scotus/2", resolved_at=(T2 + timedelta(days=10)).date())
    _grade(data, "scotus/2", "e1", predictor_id="alpha", stamped=T2 + timedelta(days=11))
    _cell(data, "scotus/3", "alpha", B, T2 + timedelta(days=1))
    _failure(data, "scotus/3", "alpha", "20260201T000000Z")
    _cell(data, "scotus/4", "beta", D, T1 + timedelta(days=5))
    _cell(data, "scotus/4", "alpha", B, T2 + timedelta(days=1))


def test_the_successor_disclosures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
    _ledger(data)
    report = successor_disclosures(data, closed_label="proc-a", successor_label="proc-b")
    assert report.instant == T2
    (census,) = report.closed_windows
    assert (census.predictor_ids, census.counted_events) == (["alpha"], 2)
    assert (census.resolved_at_close, census.pending_at_close) == (1, 1)
    # Beta's carried window ran beside both sides, so nothing here is split.
    assert report.split_events == 0
    (alpha,) = report.engines
    assert (alpha.predictor_id, alpha.closed_window) == ("alpha", "proc-a")
    assert not alpha.closed_window_inferred
    assert alpha.successor_counted_events == 2
    assert (alpha.failed_earlier_attempt, alpha.missing_earlier_attempt) == (1, 1)
    # Both closed-window gradings: one before the instant, one after it.
    (judge,) = report.evaluator_digests
    assert (judge.evaluator_id, judge.gradings, judge.graded_after_instant) == ("e1", 2, 1)


def test_a_split_event_is_counted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """beta's process changes too: an event with alpha's closed-window cell and
    beta's successor cell is split — those windows never ran together."""
    beta_closed = BETA.model_copy(update={"closes": T2})
    beta_successor = CountingWindow(label="proc-b", digest="sha256:" + "e" * 64, opens=T2)
    set_windows(monkeypatch, CLOSED, SUCCESSOR, beta_closed, beta_successor)
    data = tmp_path / "data"
    _cell(data, "scotus/1", "alpha", A, T1 + timedelta(days=1))
    _cell(data, "scotus/1", "beta", beta_successor.digest, T2 + timedelta(days=1))
    report = successor_disclosures(data, closed_label="proc-a", successor_label="proc-b")
    assert (report.split_events, report.split_events_resolved) == (1, 0)


def test_the_disclosures_refuse_an_unclosed_label(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED.model_copy(update={"closes": None}))
    with pytest.raises(WindowRecordError, match="no closed window"):
        successor_disclosures(tmp_path, closed_label="proc-a", successor_label="proc-b")


def test_a_revoked_windows_board_over_its_resolved_slice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The revocation lifted for the window's own cells, cut to the outcomes
    resolved by the revocation day; the registry is restored afterwards."""
    revoked = CLOSED.model_copy(update={"revoked_at": T2 + timedelta(days=5)})
    set_windows(monkeypatch, revoked, SUCCESSOR, BETA)
    data = tmp_path / "data"
    _ledger(data)
    record = revoked_window_board(data, label="proc-a", statpack=None)
    # Event 1 resolved before the revocation; event 2 resolved after it.
    assert [(e.predictor_id, e.process_window, e.events_scored) for e in record.board.entries] == [
        ("alpha", "proc-a", 1)
    ]
    assert record.board.frozen_process is not None
    assert record.board.frozen_process.windows == list(process_version.COUNTING_WINDOWS)
    assert process_version.COUNTING_WINDOWS[0].revoked_at is not None
    with pytest.raises(WindowRecordError, match="no revoked window"):
        revoked_window_board(data, label="proc-b", statpack=None)


def test_the_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
    _ledger(data)
    env = {"FEDCOURTS_DATA_ROOT": str(data), "FEDCOURTS_METRICS_ROOT": str(tmp_path / "m")}
    runner = CliRunner()
    result = runner.invoke(
        app, ["successor-disclosures", "--closed", "proc-a", "--successor", "proc-b"], env=env
    )
    assert result.exit_code == 0, result.output
    assert "1 resolved, 1 pending at close" in result.output
    revoked = CLOSED.model_copy(update={"revoked_at": T2 + timedelta(days=5)})
    set_windows(monkeypatch, revoked, SUCCESSOR, BETA)
    out = tmp_path / "revoked.json"
    argv = ["revoked-window-board", "--label", "proc-a", "--out", str(out)]
    result = runner.invoke(app, argv, env=env)
    assert result.exit_code == 0, result.output
    assert out.is_file()
    result = runner.invoke(app, [*argv[:2], "proc-z", *argv[3:]], env=env)
    assert result.exit_code == 2


def test_the_earlier_attempts_partition_the_successor_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every successor-counted event lands in exactly one bucket, and an engine
    whose closed window left only failures is read over an inferred span rather
    than reported clean."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
    # 1: failed; 2: an uncounted shakedown cell inside the span; 3: not reached
    # before the close; 4: reached (beta before the close), nothing from alpha.
    _cell(data, "scotus/1", "alpha", B, T2 + timedelta(days=1))
    _failure(data, "scotus/1", "alpha", "20260201T000000Z")
    _cell(data, "scotus/2", "alpha", "sha256:" + "7" * 64, T1 + timedelta(days=3), run="p0")
    _cell(data, "scotus/2", "alpha", B, T2 + timedelta(days=1))
    _cell(data, "scotus/3", "alpha", B, T2 + timedelta(days=1))
    _cell(data, "scotus/4", "beta", D, T1 + timedelta(days=5))
    _cell(data, "scotus/4", "alpha", B, T2 + timedelta(days=1))
    report = successor_disclosures(data, closed_label="proc-a", successor_label="proc-b")
    (alpha,) = report.engines
    buckets = (
        alpha.failed_earlier_attempt,
        alpha.uncounted_earlier_cell,
        alpha.not_reached_before_close,
        alpha.missing_earlier_attempt,
    )
    assert buckets == (1, 1, 1, 1)
    assert sum(buckets) == alpha.successor_counted_events
    # No committed cell of alpha carries the closed digest: the span is inferred.
    assert alpha.closed_window_inferred


def test_an_outcome_on_the_boundary_day_counts_as_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revoked_at = T2 + timedelta(days=5)
    set_windows(monkeypatch, CLOSED.model_copy(update={"revoked_at": revoked_at}), SUCCESSOR)
    data = tmp_path / "data"
    _cell(data, "scotus/1", "alpha", A, T1 + timedelta(days=1))
    _outcome(data, "scotus/1", resolved_at=revoked_at.date())
    _grade(data, "scotus/1", "e1", predictor_id="alpha", stamped=revoked_at + timedelta(days=1))
    record = revoked_window_board(data, label="proc-a", statpack=None)
    assert record.board.events_scored == 1
    assert record.resolved_counted_events == {A: 1}
    assert record.graded_after_revocation == 1
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    _outcome(data, "scotus/1", resolved_at=T2.date())
    (census,) = successor_disclosures(
        data, closed_label="proc-a", successor_label="proc-b"
    ).closed_windows
    assert (census.resolved_at_close, census.pending_at_close) == (1, 0)


def test_the_registry_is_restored_when_the_block_raises() -> None:
    before = process_version.COUNTING_WINDOWS
    with pytest.raises(RuntimeError), process_version.counting_windows([CLOSED]):
        assert process_version.COUNTING_WINDOWS == (CLOSED,)
        raise RuntimeError
    assert process_version.COUNTING_WINDOWS is before
