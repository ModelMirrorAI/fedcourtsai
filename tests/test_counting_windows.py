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
from fedcourtsai.cli import _latest_prediction_for
from fedcourtsai.dataset_export import build_tables
from fedcourtsai.leaderboard import big_case_agreement
from fedcourtsai.paths import CasePaths
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import (
    BigCaseAssessment,
    CountingWindow,
    Evaluation,
    Prediction,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import (
    PooledWindowsError,
    event_has_claimable_prediction,
    predictor_holds_no_counted_prediction,
    scored_prediction,
    stratify,
)
from fedcourtsai.tool_usage import _JoinedCell, _refuse_pooled_windows
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


# --- binding until built ---------------------------------------------------------


def test_no_window_closes_until_the_boards_are_per_window() -> None:
    """The "binding until built" clause, made mechanical.

    The aggregate boards (leaderboard, claim scores, ops, semantic summary,
    big-case agreement, tool usage) key on ``predictor_id`` or the engine and
    *refuse* a ledger in which one of them spans two windows. A successor that
    closes a window before they key on (predictor, window) would take every
    frozen-scope board down — the proc-v8 release figures included — the first
    time a predictor holds graded cells in both. So no window may close yet.
    Remove this test in the same change that builds per-window strata.
    """
    closed = [w for w in process_version.COUNTING_WINDOWS if w.closes is not None]
    assert not closed, (
        "a counting window closed before the aggregate boards key on (predictor, "
        "window) — build per-window strata first (docs/process-version.md, the "
        "third supersession shape): " + process_version.describe_windows(closed)
    )


def test_no_window_opens_after_the_earliest_until_the_boards_are_per_window() -> None:
    """The same hold, for the bless that closes nothing.

    A predictor-half bless that adds a window for a new predictor id leaves
    every existing window open, so the close tripwire never fires and no
    predictor spans two windows — yet the boards would rank an engine whose
    window opened later beside the earlier ones, over a different span of
    events. Every window opening at one instant is also what keeps the event
    half of the counting rule a no-op on the live registry. Remove this test in
    the same change that builds per-window strata.
    """
    windows = process_version.COUNTING_WINDOWS
    earliest = min((w.opens for w in windows), default=None)
    later = [w for w in windows if w.opens != earliest]
    assert not later, (
        "a counting window opens after the earliest before the aggregate boards key "
        "on (predictor, window) — build per-window strata first (docs/process-version.md, "
        "the per-window hold): " + process_version.describe_windows(later)
    )


def test_every_close_is_a_successors_opening_instant() -> None:
    """A window closes at the counting instant of the successor that stopped
    blessing it, so every ``closes`` is some window's ``opens``; and a revocation
    falls at or after the window opened."""
    windows = process_version.COUNTING_WINDOWS
    openings = {w.opens for w in windows}
    for window in windows:
        if window.closes is not None:
            assert window.closes in openings, f"{window.digest}: closes at no window's opening"
        if window.revoked_at is not None:
            assert window.revoked_at >= window.opens


def test_only_a_closed_window_can_be_revoked() -> None:
    with pytest.raises(ValueError, match="only a closed window"):
        CountingWindow(label="x", digest=A, opens=T1, revoked_at=T2)
    with pytest.raises(ValueError, match="revoked at or after"):
        CountingWindow(label="x", digest=A, opens=T1, closes=T2, revoked_at=T1 - timedelta(days=1))
    with pytest.raises(ValueError, match="closes after it opens"):
        CountingWindow(label="x", digest=A, opens=T1, closes=T1)


# --- three windows: a revocation behind a stale later-window cell ----------------

C = "sha256:" + "c" * 64
T3 = datetime(2026, 7, 1, tzinfo=UTC)
REVOKED_AT = T3 + timedelta(days=5)
THREE = (
    CountingWindow(label="proc-a", digest=A, opens=T1, closes=T2, revoked_at=REVOKED_AT),
    CountingWindow(label="proc-b", digest=B, opens=T2, closes=T3),
    CountingWindow(label="proc-c", digest=C, opens=T3),
)


def test_a_stale_later_window_cell_does_not_block_the_fresh_forecast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W1 < W2 < W3, W1 revoked at r. A W2 cell stamped before r is uncounted
    (the revocation must not promote it); the fresh W3 cell stamped after r
    counts, because an uncounted earlier-window sibling takes nothing from it —
    so the event is not re-owed until the attempt cap."""
    set_windows(monkeypatch, *THREE)
    early = _pv(A, T1 + timedelta(days=1))
    stale = _pv(B, T2 + timedelta(days=1))
    fresh = _pv(C, REVOKED_AT + timedelta(days=1))
    siblings = [early, stale, fresh]
    assert not process_version.counted_on_event(early, lambda: siblings)
    assert not process_version.counted_on_event(stale, lambda: siblings)
    assert process_version.counted_on_event(fresh, lambda: siblings)


def test_the_fresh_forecast_ends_the_re_owe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, *THREE)
    data = tmp_path / "data"
    args = (data, "scotus", 1, "evt-petition-disposition", "alpha")
    _seed(data, run_id="p1", stamp=_pv(A, T1 + timedelta(days=1)))
    _seed(data, run_id="p2", stamp=_pv(B, T2 + timedelta(days=1)))
    assert predictor_holds_no_counted_prediction(*args)
    _seed(data, run_id="p3", stamp=_pv(C, REVOKED_AT + timedelta(days=1)))
    assert not predictor_holds_no_counted_prediction(*args)


# --- the other resolvers and refusals --------------------------------------------


def test_the_stamp_resolver_never_names_a_later_windows_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The stamp's ``prediction_run_id`` is read off this resolver, so it must
    name the earliest window's cell, as evaluation staging does."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _seed(data, run_id="p1", stamp=_pv(A, T1 + timedelta(days=1)))
    _seed(data, run_id="p2", stamp=_pv(B, T2 + timedelta(days=1)))
    event = CasePaths(data, "scotus", 1).event("evt-petition-disposition")
    resolved = _latest_prediction_for(event, "alpha")
    assert resolved is not None and resolved.run_id == "p1"


def test_big_case_agreement_refuses_two_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    for docket in (1, 2):
        event = CasePaths(data, "scotus", docket).event("evt-petition-disposition")
        pred_path = event.prediction("alpha", "p1")
        prediction = read_model(pred_path, Prediction)
        write_json(pred_path, prediction.model_copy(update={"big_case_score": 0.5}))
        eval_path = event.evaluation("e1", "alpha", "r1")
        evaluation = read_model(eval_path, Evaluation)
        assessment = BigCaseAssessment(evaluator_score=0.4)
        write_json(eval_path, evaluation.model_copy(update={"big_case": assessment}))
    with pytest.raises(PooledWindowsError, match=r"alpha .*proc-a.*proc-b"):
        big_case_agreement(data)
    assert "alpha" in big_case_agreement(data, frozen_only=False)


def _joined(window: CountingWindow) -> _JoinedCell:
    return _JoinedCell(
        engine="claude-code",
        mode="forward",
        stage="cert",
        moment="distribution",
        calls=1,
        mcp_calls=0,
        at_call_cap=False,
        briers=[0.1],
        evaluations=1,
        window=window,
    )


def test_tool_usage_refuses_one_engine_across_two_windows() -> None:
    _refuse_pooled_windows([_joined(CLOSED), _joined(CLOSED)])
    with pytest.raises(PooledWindowsError, match="claude-code"):
        _refuse_pooled_windows([_joined(CLOSED), _joined(SUCCESSOR)])
