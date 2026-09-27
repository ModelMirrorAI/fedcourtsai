"""Per-blessing counting windows: a superseded predictor process is closed, not revoked.

A window belongs to one blessing of one predictor digest. It opens at the
counting instant of the label that blessed the digest and closes at the
successor's; a closed window's cells keep counting, a revoked one's do not.
Where one predictor holds cells from several windows on one event, the earliest
still-counting window's cell counts and a later one's counts nowhere — never
staged for grading in its place. A grading is gated on its prediction's window,
not a successor's instant, and a supersession re-owes nothing.

The first block pins the live registry (the tripwire on ``proc-v8``'s three
predictor digests among it); the rest exercise the rule on a patched registry
with a closed window and its successor beside it.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path

import pytest

from fedcourtsai import process_version
from fedcourtsai.blinding import latest_prediction_dirs
from fedcourtsai.dataset_export import build_tables
from fedcourtsai.paths import CasePaths
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import CountingWindow, ProcessVersion
from fedcourtsai.store import (
    PooledWindowsError,
    event_has_claimable_prediction,
    predictor_holds_no_counted_prediction,
    scored_prediction,
    stratify,
)
from tests.conftest import set_windows
from tests.test_dataset_export import _event, _grade, _outcome, _prediction

CONFIG = Path("config")
REPO = Path(".")

# proc-v8's counting instant and its three predictor digests (claude, codex,
# gemini), as the freeze record's 2026-09-16 cutover entry registers them.
PROC_V8_INSTANT = datetime(2026, 9, 16, 0, 26, 4, tzinfo=UTC)
PROC_V8_PREDICTOR_DIGESTS = (
    "sha256:1a0b2bef2e367cd589e4800fa04de5b5110b41bf1ea159b3c51669ccc722e89a",
    "sha256:70fee158526caa6870d43ace70c3781db39f644379c86c363538ebdefa57547c",
    "sha256:a9033e56819e775e561b802dec24bae437c17c751e5a7f5fa4b3eeb31383951f",
)


def test_proc_v8_predictor_digests_never_leave_the_registry_without_a_close() -> None:
    """The tripwire that makes "binding until built" mechanical.

    The freeze record's 2026-09-26 entry registers that a successor closes
    ``proc-v8``'s windows and de-counts nothing. So each of the three predictor
    digests keeps exactly one ``proc-v8`` window, opening at the proc-v8
    instant and never revoked; and a successor that stops blessing one (drops
    it from the bless map) must have closed its window rather than deleted it.
    A revocation is the one legitimate way to break this, and it lands with its
    own dated freeze-record entry — edit this test in that same commit.
    """
    for digest in PROC_V8_PREDICTOR_DIGESTS:
        windows = [
            window
            for window in process_version.COUNTING_WINDOWS
            if window.digest == digest and window.label == "proc-v8"
        ]
        assert len(windows) == 1, (
            f"{digest}: proc-v8's window left the counting registry — a successor "
            "closes it (sets `closes`), it never removes it"
        )
        (window,) = windows
        assert window.opens == PROC_V8_INSTANT
        assert window.revoked_at is None, (
            f"{digest}: revoking proc-v8 needs its own dated freeze-record entry"
        )
        if digest not in process_version.FROZEN_PROCESS_DIGESTS:
            assert window.closes is not None, (
                f"{digest} is no longer blessed but its proc-v8 window is still open"
            )


def test_the_counting_registry_is_well_formed() -> None:
    """Windows are aware, ordered, non-overlapping per digest, and predictor-only.

    Every window the current label opened opens at ``FROZEN_SINCE``; no window
    opens after it; an open window's digest is still blessed; and every
    enabled predictor's live digest has an open window, so today's fleet counts.
    """
    windows = process_version.COUNTING_WINDOWS
    since = process_version.FROZEN_SINCE
    assert bool(windows) == (since is not None)
    for window in windows:
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", window.digest), window.digest
        assert window.opens.tzinfo is not None
        if window.closes is not None:
            assert window.closes.tzinfo is not None
            assert window.closes > window.opens
        if since is not None:
            assert window.opens <= since
        if window.label == process_version.CURRENT_PROCESS_LABEL:
            assert window.opens == since
        if window.closes is None and window.revoked_at is None:
            assert window.digest in process_version.FROZEN_PROCESS_DIGESTS
    by_digest: dict[str, list[CountingWindow]] = {}
    for window in windows:
        by_digest.setdefault(window.digest, []).append(window)
    for digest, spans in by_digest.items():
        spans.sort(key=lambda w: w.opens)
        for earlier, later in pairwise(spans):
            assert earlier.closes is not None and earlier.closes <= later.opens, (
                f"{digest}: two windows overlap"
            )
    evaluator_digests = {
        process_version.digest_for_actor(REPO, CONFIG, "evaluator", entry.id)
        for entry in enabled_evaluators(CONFIG / "evaluators.yaml")
    }
    assert not evaluator_digests & set(by_digest), "an evaluator digest records, never counts"
    if windows:
        for entry in enabled_predictors(CONFIG / "predictors.yaml"):
            digest = process_version.digest_for_actor(REPO, CONFIG, "predictor", entry.id)
            assert any(
                w.digest == digest and w.closes is None and w.revoked_at is None for w in windows
            ), f"{entry.id}: its live digest has no open counting window"


def test_the_board_record_carries_the_windows() -> None:
    record = process_version.frozen_process_record()
    assert record.windows == list(process_version.COUNTING_WINDOWS)


# A closed window (proc-a, digest A) and the successor that closed it (proc-b).
A = "sha256:" + "a" * 64
B = "sha256:" + "b" * 64
T1 = datetime(2026, 1, 1, tzinfo=UTC)
T2 = datetime(2026, 4, 1, tzinfo=UTC)
CLOSED = CountingWindow(label="proc-a", digest=A, opens=T1, closes=T2)
SUCCESSOR = CountingWindow(label="proc-b", digest=B, opens=T2)


def _pv(digest: str, when: datetime) -> ProcessVersion:
    return ProcessVersion(label="proc-x", digest=digest, stamped_at=when)


def test_a_closed_windows_cells_keep_counting(monkeypatch: pytest.MonkeyPatch) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    assert process_version.is_frozen(_pv(A, T1 + timedelta(days=1)))
    assert process_version.window_of(_pv(A, T1)) == CLOSED
    # Past the close the digest counts nowhere; the successor counts from T2.
    assert not process_version.is_frozen(_pv(A, T2))
    assert process_version.is_frozen(_pv(B, T2))
    assert not process_version.is_frozen(_pv(B, T2 - timedelta(seconds=1)))


def test_a_revoked_windows_cells_do_not_count(monkeypatch: pytest.MonkeyPatch) -> None:
    revoked = CLOSED.model_copy(update={"revoked_at": T2 + timedelta(days=10)})
    set_windows(monkeypatch, revoked, SUCCESSOR)
    cell = _pv(A, T1 + timedelta(days=1))
    assert process_version.window_of(cell) == revoked
    assert not process_version.is_frozen(cell)
    assert not process_version.counted_on_event(cell, lambda: [cell])


def test_a_grading_is_gated_on_its_predictions_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Not on the successor's instant: a closed window keeps its gradings."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    prediction = _pv(A, T1 + timedelta(days=1))
    assert process_version.FROZEN_SINCE == T2
    assert process_version.graded_in_window(_pv("sha256:judge", T1 + timedelta(days=2)), prediction)
    assert not process_version.graded_in_window(
        _pv("sha256:judge", T1 - timedelta(days=1)), prediction
    )
    assert not process_version.graded_in_window(None, prediction)
    # A prediction in no window has no gate to pass.
    assert not process_version.graded_in_window(_pv("sha256:judge", T2), _pv("sha256:c", T2))


def test_the_earliest_windows_cell_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    early = _pv(A, T1 + timedelta(days=1))
    late = _pv(B, T2 + timedelta(days=1))
    siblings = [early, late]
    assert process_version.counted_on_event(early, lambda: siblings)
    assert not process_version.counted_on_event(late, lambda: siblings)
    assert process_version.staging_excluded(late, lambda: siblings)
    assert not process_version.staging_excluded(early, lambda: siblings)
    # Alone on its event, the successor's cell counts.
    assert process_version.counted_on_event(late, lambda: [late])


def test_a_revocation_never_promotes_a_forecast_already_made(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    revoked_at = T2 + timedelta(days=10)
    set_windows(monkeypatch, CLOSED.model_copy(update={"revoked_at": revoked_at}), SUCCESSOR)
    early = _pv(A, T1 + timedelta(days=1))
    before = _pv(B, T2 + timedelta(days=1))
    fresh = _pv(B, revoked_at + timedelta(days=1))
    siblings = [early, before, fresh]
    assert not process_version.counted_on_event(before, lambda: siblings)
    assert process_version.counted_on_event(fresh, lambda: siblings)


def _seed(data: Path, *, run_id: str, stamp: ProcessVersion, case: str = "scotus/1") -> None:
    _event(data, case)
    _prediction(data, case, predictor_id="alpha", run_id=run_id, stamp=stamp)


def test_staging_and_the_fallback_join_pick_the_earliest_windows_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _seed(data, run_id="p1", stamp=_pv(A, T1 + timedelta(days=1)))
    _seed(data, run_id="p2", stamp=_pv(B, T2 + timedelta(days=1)))
    event = CasePaths(data, "scotus", 1).event("evt-petition-disposition")
    assert latest_prediction_dirs(event)["alpha"].name == "p1"
    scored = scored_prediction(event.base, "alpha", None)
    assert scored is not None and scored.run_id == "p1"
    assert event_has_claimable_prediction(data, "scotus", 1, "evt-petition-disposition")


def test_a_supersession_re_owes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A closed window's counted cell keeps its event covered; a revoked one's does not."""
    data = tmp_path / "data"
    _seed(data, run_id="p1", stamp=_pv(A, T1 + timedelta(days=1)))
    args = (data, "scotus", 1, "evt-petition-disposition", "alpha")
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    assert not predictor_holds_no_counted_prediction(*args)
    set_windows(monkeypatch, CLOSED.model_copy(update={"revoked_at": T2}), SUCCESSOR)
    assert predictor_holds_no_counted_prediction(*args)


def _graded_ledger(data: Path) -> None:
    """One predictor graded on one event per window: the pooling the boards refuse."""
    for case, digest, when in (("scotus/1", A, T1), ("scotus/2", B, T2)):
        _seed(data, run_id="p1", stamp=_pv(digest, when + timedelta(days=1)), case=case)
        _outcome(data, case, resolved_at=(when + timedelta(days=30)).date())
        _grade(data, case, "e1", prediction_run_id="p1", stamped=when + timedelta(days=31))


def test_no_aggregate_pools_two_windows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    with pytest.raises(PooledWindowsError, match="alpha"):
        stratify(data)
    # The all-versions pass is the named pooled view and says so in its scope.
    assert len(stratify(data, frozen_only=False).cells) == 2


def test_a_single_window_board_names_its_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED)
    data = tmp_path / "data"
    _graded_ledger(data)
    run = stratify(data)
    assert len(run.cells) == 1
    assert dict(run.windows) == {"alpha": "proc-a"}


def test_the_export_carries_each_rows_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    _seed(data, run_id="p2", stamp=_pv(B, T2 + timedelta(days=2)))  # later window, event 1
    rows = {(row.case_id, row.run_id): row for row in build_tables(data).predictions}
    assert rows[("scotus/1", "p1")].process_window == "proc-a"
    assert rows[("scotus/1", "p1")].process_frozen
    assert rows[("scotus/2", "p1")].process_window == "proc-b"
    # The later window's cell on an event the closed window already holds
    # counts nowhere, so the frozen export leaves it out ...
    assert ("scotus/1", "p2") not in rows
    everything = {
        (row.case_id, row.run_id): row for row in build_tables(data, all_versions=True).predictions
    }
    # ... and the all-versions export names its window and marks it uncounted.
    assert everything[("scotus/1", "p2")].process_window == "proc-b"
    assert not everything[("scotus/1", "p2")].process_frozen
    assert not everything[("scotus/1", "p2")].staged
