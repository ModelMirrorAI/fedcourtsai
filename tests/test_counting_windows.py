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
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Protocol

import pytest
from typer.testing import CliRunner

from fedcourtsai import process_version
from fedcourtsai.analytics import build_big_case_board
from fedcourtsai.blinding import latest_prediction_dirs
from fedcourtsai.claim_metrics import build_claim_scores
from fedcourtsai.cli import _latest_prediction_for, app
from fedcourtsai.dataset_export import build_tables
from fedcourtsai.leaderboard import (
    big_case_agreement,
    build_leaderboard,
    cell_facts,
    coverage_shortfalls,
    evaluator_agreement,
)
from fedcourtsai.ops import render_substance, summarize_substance
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.semantic import SEMANTIC_SET_V1
from fedcourtsai.process_version import PooledWindowsError
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.release_sensitivity import (
    RANKED_ARM,
    _cert_events,
    project,
    rebuild,
    render_table,
)
from fedcourtsai.schemas import (
    BigCaseAssessment,
    BigCaseLeaderboard,
    ClaimScoreBoard,
    CountingWindow,
    Evaluation,
    Leaderboard,
    Prediction,
    ProcessVersion,
    SemanticGrade,
    SemanticGradeBlock,
    SemanticSupport,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import (
    StratifiedRun,
    evaluation_key,
    event_has_claimable_prediction,
    predictor_holds_no_counted_prediction,
    scored_prediction,
    stratify,
)
from fedcourtsai.tool_usage import _correlate, _grouped, _JoinedCell, _segment, _segments
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
            assert window.closes is not None or digest in _closing_digests(), (
                f"{digest} is no longer blessed but its proc-v8 window is still open"
            )


def _closing_digests() -> set[str]:
    """Digests whose window's close is pending in the registry.

    A pending close reads as open in ``COUNTING_WINDOWS`` until the carrying
    merge stamps it, so the registry rows are what say a successor closes it.
    """
    return {
        w.digest
        for w in process_version._REGISTRY.windows
        if w.closes is not None and w.closes.at is None
    }


def _label_since(label: str) -> datetime | None:
    (entry,) = [entry for entry in process_version._REGISTRY.labels if entry.label == label]
    return entry.since.at


def _live_predictor_digests() -> dict[str, str]:
    return {
        entry.id: process_version.digest_for_actor(REPO, CONFIG, "predictor", entry.id)
        for entry in enabled_predictors(CONFIG / "predictors.yaml")
    }


def test_proc_v9_closed_claude_and_carried_codex_and_gemini_forward() -> None:
    """proc-v9's registry shape, as the freeze record's proc-v9 entry registers it.

    proc-v9 re-blessed claude-baseline alone on the predictor half: its proc-v8
    window closes at the proc-v9 instant and its new digest's window opens
    there, labelled proc-v9. The codex-baseline and gemini-baseline proc-v8
    windows ran through it unbroken, so neither closes at that instant.
    """
    claude_v8, codex_v8, gemini_v8 = PROC_V8_PREDICTOR_DIGESTS
    v9 = _label_since("proc-v9")
    assert v9 is not None
    rows = {w.digest: w for w in process_version._REGISTRY.windows if w.label == "proc-v8"}
    claude_close = rows[claude_v8].closes
    assert claude_close is not None and claude_close.at == v9
    for carried in (codex_v8, gemini_v8):
        close = rows[carried].closes
        assert close is None or close.at != v9
    (successor,) = [w for w in process_version._REGISTRY.windows if w.label == "proc-v9"]
    assert successor.predictor_id == "claude-baseline" and successor.opens.at == v9


#: The predictor digests the proc-v10 entry registers: claude-baseline's carried
#: proc-v9 window, and the two proc-v10 windows codex and gemini opened.
PROC_V10_PREDICTOR_DIGESTS = {
    "claude-baseline": "sha256:605201bd8358473bcb8e7d59ee2d236d7be099756241333eec0f386b3400b734",
    "codex-baseline": "sha256:7ab92dd4fb4d5e0889c4269bb2921676ad3917b6f86f71c8b26d3ac34a6574a4",
    "gemini-baseline": "sha256:bee46e92d923594056bdb6c9770521ef5251b0d065c5957262d7f5a55dd7b434",
}


def test_proc_v10_closed_codex_and_gemini_and_carried_claude_forward() -> None:
    """proc-v10's registry shape, as the freeze record's proc-v10 entry registers it.

    proc-v10 re-blessed codex-baseline and gemini-baseline on the predictor half,
    their engines' default models having moved. So their proc-v8 windows close
    at the proc-v10 instant and a proc-v10 window opens there for each new
    digest. claude-baseline's proc-v9 window ran through it unbroken, so it does
    not close at that instant.
    """
    _, codex_v8, gemini_v8 = PROC_V8_PREDICTOR_DIGESTS
    v10 = _label_since("proc-v10")
    assert v10 is not None
    rows = process_version._REGISTRY.windows
    by_label = {(w.label, w.predictor_id): w for w in rows}
    for predictor, closed in (("codex-baseline", codex_v8), ("gemini-baseline", gemini_v8)):
        assert by_label[("proc-v8", predictor)].digest == closed
        close = by_label[("proc-v8", predictor)].closes
        assert close is not None and close.at == v10
        opened = by_label[("proc-v10", predictor)]
        assert opened.digest == PROC_V10_PREDICTOR_DIGESTS[predictor] != closed
        assert opened.opens.at == v10
    claude = by_label[("proc-v9", "claude-baseline")]
    assert claude.digest == PROC_V10_PREDICTOR_DIGESTS["claude-baseline"]
    assert claude.closes is None or claude.closes.at != v10


#: The predictor digests the proc-v11 entry registers, one proc-v11 window each.
PROC_V11_PREDICTOR_DIGESTS = {
    "claude-baseline": "sha256:d1487fc0280716c03c4f119b557b1579b0bb65df0fa4efa158a88ae02a6e5e54",
    "codex-baseline": "sha256:a711152d3e0082a9f5311e40348116c753247aba102ddc60e5979c7d292abe64",
    "gemini-baseline": "sha256:c4213d78e7a7a6fc5f13d070a3bda326254c0189b7979f5e7b91a23d5608ad66",
}


def test_proc_v11_closed_every_predictor_window_and_opened_one_for_each() -> None:
    """proc-v11's registry shape, as the freeze record's proc-v11 entry registers it.

    proc-v11 edited the predict prompt, which every predictor's digest reads, so
    all three moved on the predictor half and no evaluator digest moved. Each
    predictor's open window (claude-baseline's proc-v9, codex-baseline's and
    gemini-baseline's proc-v10) closed at the proc-v11 instant, and a proc-v11
    window opened there for each new digest.
    """
    v11 = _label_since("proc-v11")
    assert v11 is not None
    rows = process_version._REGISTRY.windows
    by_label = {(w.label, w.predictor_id): w for w in rows}
    for predictor, closing_label in (
        ("claude-baseline", "proc-v9"),
        ("codex-baseline", "proc-v10"),
        ("gemini-baseline", "proc-v10"),
    ):
        closed = by_label[(closing_label, predictor)]
        assert closed.digest == PROC_V10_PREDICTOR_DIGESTS[predictor]
        assert closed.closes is not None and closed.closes.at == v11
        opened = by_label[("proc-v11", predictor)]
        assert opened.digest == PROC_V11_PREDICTOR_DIGESTS[predictor] != closed.digest
        assert opened.opens.at == v11


#: The predictor digests the proc-v12 entry registers, one proc-v12 window each.
PROC_V12_PREDICTOR_DIGESTS = {
    "claude-baseline": "sha256:457d3e0e44be5ed4d2a5da50b0078129a08c0cd4d35108569ee058c53759513f",
    "codex-baseline": "sha256:87e57da6f663878435c82b1f527cb13eea1017130fcdb13b134e759583db60f4",
    "gemini-baseline": "sha256:8057aacc92139d6caed4284137fd96ec5c008ddd60fa0c75a0752793369e07c9",
}


def test_proc_v12_closed_every_predictor_window_and_opened_one_for_each() -> None:
    """proc-v12's registry shape, as the freeze record's proc-v12 entry registers it.

    proc-v12 edited the predict prompt to elicit the authorship forecasts, so all
    three predictor digests moved and no evaluator digest moved. Each
    predictor's proc-v11 window closed at the proc-v12 instant, and a proc-v12
    window opened there for each new digest.
    """
    v12 = _label_since("proc-v12")
    assert v12 is not None
    rows = process_version._REGISTRY.windows
    by_label = {(w.label, w.predictor_id): w for w in rows}
    for predictor, digest in PROC_V11_PREDICTOR_DIGESTS.items():
        closed = by_label[("proc-v11", predictor)]
        assert closed.digest == digest
        assert closed.closes is not None and closed.closes.at == v12
        opened = by_label[("proc-v12", predictor)]
        assert opened.digest == PROC_V12_PREDICTOR_DIGESTS[predictor] != closed.digest
        assert opened.opens.at == v12


def test_proc_v13_closes_every_predictor_window_and_opens_one_for_each() -> None:
    """proc-v13's registry shape, as the freeze record's proc-v13 entry registers it.

    proc-v13 edits the predict prompt to describe the inputs it releases, so all
    three predictor digests move and no evaluator digest moves. Each
    predictor's proc-v12 window closes at the proc-v13 instant, and a proc-v13
    window opens there for each live digest. Pending rows compare by their null
    instants until the merge stamps them.
    """
    v13 = _label_since("proc-v13")
    live = _live_predictor_digests()
    rows = process_version._REGISTRY.windows
    by_label = {(w.label, w.predictor_id): w for w in rows}
    for predictor, digest in PROC_V12_PREDICTOR_DIGESTS.items():
        closed = by_label[("proc-v12", predictor)]
        assert closed.digest == digest
        assert closed.closes is not None and closed.closes.at == v13
        opened = by_label[("proc-v13", predictor)]
        assert opened.digest == live[predictor] != closed.digest
        assert opened.opens.at == v13 and opened.closes is None
    assert len(rows) == 15


def test_the_counting_registry_is_well_formed() -> None:
    """Windows are aware, ordered, non-overlapping per digest, and predictor-only.

    Every window the current label opened opens at ``FROZEN_SINCE``; no window
    opens after it; an open window's digest is still blessed, or its close is
    pending; and every enabled predictor's live digest has an open window, or
    one pending its opening, so today's fleet counts once its label is carried.
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
            # A window whose successor's close is pending still reads open.
            assert (
                window.digest in process_version.FROZEN_PROCESS_DIGESTS
                or window.digest in _closing_digests()
            )
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
            # A window whose opening is pending is registered but not yet built.
            assert any(
                w.digest == digest and w.closes is None and w.revoked_at is None for w in windows
            ) or any(
                w.digest == digest and w.opens.at is None for w in process_version._REGISTRY.windows
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
    """One predictor graded on one event per window: a record the boards pool."""
    for case, digest, when in (("scotus/1", A, T1), ("scotus/2", B, T2)):
        _seed(data, run_id="p1", stamp=_pv(digest, when + timedelta(days=1)), case=case)
        _outcome(data, case, resolved_at=(when + timedelta(days=30)).date())
        _grade(data, case, "e1", prediction_run_id="p1", stamped=when + timedelta(days=31))


def test_the_frozen_pass_pools_a_predictors_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A predictor whose counted cells span two windows is one record: the pass
    yields both cells and names each one's window for the composition and cut."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    run = stratify(data)
    assert len(run.cells) == 2
    assert sorted(window.label for window in run.cell_windows.values()) == ["proc-a", "proc-b"]
    # The all-versions pass is the named pooled view and says so in its scope.
    assert len(stratify(data, frozen_only=False).cells) == 2
    assert not stratify(data, frozen_only=False).cell_windows


def test_a_single_window_board_names_its_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, CLOSED)
    data = tmp_path / "data"
    _graded_ledger(data)
    run = stratify(data)
    assert len(run.cells) == 1
    assert [window.label for window in run.cell_windows.values()] == ["proc-a"]


def test_two_windows_sharing_a_label_are_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every per-window figure is named (predictor, label), so two of one
    predictor's windows under one label could not be told apart."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR.model_copy(update={"label": "proc-a"}))
    data = tmp_path / "data"
    _graded_ledger(data)
    with pytest.raises(PooledWindowsError, match="share a label"):
        stratify(data)


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


# --- per-window boards over a two-window registry ------------------------------

# Three predictors. alpha's process changes (proc-a closes, proc-b opens at T2);
# beta's digest carries forward byte-identical, so its one proc-a window stays
# open across both; gamma changes too.
D = "sha256:" + "d" * 64
E = "sha256:" + "e" * 64
F = "sha256:" + "f" * 64
BETA = CountingWindow(label="proc-a", digest=D, opens=T1)
GAMMA_CLOSED = CountingWindow(label="proc-a", digest=E, opens=T1, closes=T2)
GAMMA_SUCCESSOR = CountingWindow(label="proc-b", digest=F, opens=T2)
TWO_LABELS = (CLOSED, SUCCESSOR, BETA, GAMMA_CLOSED, GAMMA_SUCCESSOR)
EVENT = "evt-petition-disposition"

# case -> each predictor's counted cell: (digest, stamped). Case 1 is all
# proc-a, case 2 all proc-b (beta's carried window beside the successors), and
# case 3 is a split event: alpha's cell from the closed window, gamma's from the
# successor that closed it.
_CELLS = {
    "scotus/1": {"alpha": (A, T1), "beta": (D, T1), "gamma": (E, T1)},
    "scotus/2": {"alpha": (B, T2), "beta": (D, T2), "gamma": (F, T2)},
    "scotus/3": {"alpha": (A, T1), "beta": (D, T1), "gamma": (F, T2)},
}


def _two_label_ledger(data: Path) -> None:
    """Every predictor graded by two judges on every case, big-case reads included."""
    for case, cells in _CELLS.items():
        _event(data, case)
        latest = max(when for _, when in cells.values())
        _outcome(data, case, resolved_at=(latest + timedelta(days=30)).date())
        event = CasePaths(data, "scotus", int(case.split("/")[1])).event(EVENT)
        for predictor, (digest, when) in cells.items():
            _prediction(
                data, case, predictor_id=predictor, stamp=_pv(digest, when + timedelta(days=1))
            )
            pred_path = event.prediction(predictor, "p1")
            prediction = read_model(pred_path, Prediction)
            write_json(pred_path, prediction.model_copy(update={"big_case_score": 0.5}))
            for judge, score in (("e1", 0.4), ("e2", 0.6)):
                _grade(
                    data, case, judge, predictor_id=predictor, stamped=latest + timedelta(days=31)
                )
                eval_path = event.evaluation(judge, predictor, "r1")
                evaluation = read_model(eval_path, Evaluation)
                assessment = BigCaseAssessment(evaluator_score=score)
                write_json(eval_path, evaluation.model_copy(update={"big_case": assessment}))


def _series(entries: Iterable[_Keyed]) -> list[tuple[str, str | None]]:
    return [(entry.predictor_id, entry.process_window) for entry in entries]


class _Keyed(Protocol):
    @property
    def predictor_id(self) -> str: ...
    @property
    def process_window(self) -> str | None: ...


ALL_SERIES = [
    ("alpha", "proc-a"),
    ("alpha", "proc-b"),
    ("beta", "proc-a"),
    ("gamma", "proc-a"),
    ("gamma", "proc-b"),
]


def _pooled_and_cut_big_case(data: Path) -> dict[tuple[str, str | None], BigCaseLeaderboard]:
    """The big-case map the leaderboard command hands the board: pooled and per window."""
    return {
        **big_case_agreement(data, by_window=False),
        **big_case_agreement(data, by_window=True),
    }


def test_a_two_window_registry_pools_each_predictor_and_cuts_by_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One pooled entry per predictor with its composition; the per-window
    entries as the unranked cut; the rank read over every paired event, the
    event whose cells come from a closed window and its successor included."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data)
    board = build_leaderboard(
        run.cells,
        big_case=_pooled_and_cut_big_case(data),
        evaluators=evaluator_agreement(data),
        facts=cell_facts(run.cells, data),
        cell_windows=run.cell_windows,
    )
    assert [(e.predictor_id, e.process_window, e.events_scored) for e in board.entries] == [
        ("alpha", None, 3),
        ("beta", None, 3),
        ("gamma", None, 3),
    ]
    # Two judges per cell: the composition counts gradings, in opening order.
    composition = {
        e.predictor_id: [(w.process_window, w.n) for w in e.windows] for e in board.entries
    }
    assert composition == {
        "alpha": [("proc-a", 4), ("proc-b", 2)],
        "beta": [("proc-a", 6)],
        "gamma": [("proc-a", 2), ("proc-b", 4)],
    }
    assert sorted(_series(board.by_protocol)) == ALL_SERIES
    scored = {(e.predictor_id, e.process_window): e.events_scored for e in board.by_protocol}
    assert scored == {
        ("alpha", "proc-a"): 2,
        ("alpha", "proc-b"): 1,
        ("beta", "proc-a"): 3,
        ("gamma", "proc-a"): 1,
        ("gamma", "proc-b"): 2,
    }
    assert all(e.rank is None for e in board.by_protocol)
    # The pooled entry's big-case agreement spans every window; the cut's is its own.
    pooled = {e.predictor_id: e.big_case for e in board.entries}
    assert pooled["alpha"] is not None and pooled["alpha"].cases == 3
    # The pooled correlation states the windows it spans and the judge rubrics
    # its panel means draw on, each in reads.
    assert [(w.process_window, w.n) for w in pooled["alpha"].windows] == [
        ("proc-a", 4),
        ("proc-b", 2),
    ]
    assert [(r.evaluator_id, r.n) for r in pooled["alpha"].rubrics] == [("e1", 3), ("e2", 3)]
    cut = {(e.predictor_id, e.process_window): e.big_case for e in board.by_protocol}
    assert cut[("alpha", "proc-a")] is not None and cut[("alpha", "proc-a")].cases == 2
    assert cut[("alpha", "proc-b")] is not None and cut[("alpha", "proc-b")].cases == 1
    # No window restriction on pairing: case 3 pairs a closed window's cell with
    # its successor's, so every case is paired.
    assert board.paired is not None
    assert board.paired.events == 3
    assert board.paired.by_band == {"(none)": 3}
    paired_alpha = next(e for e in board.paired.entries if e.predictor_id == "alpha")
    assert [(w.process_window, w.n) for w in paired_alpha.windows] == [
        ("proc-a", 4),
        ("proc-b", 2),
    ]
    assert sorted(e.rank for e in board.entries if e.rank is not None) == [1, 2, 3]
    assert {e.paired_events for e in board.entries} == {3}
    # The grader view pools the predictors' windows by design and says which.
    for agreement in board.evaluator_agreement.values():
        assert sorted((w.predictor_id, w.process_window) for w in agreement.windows) == ALL_SERIES


def test_a_two_window_registry_builds_the_cli_boards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The commands build rather than refuse: pooled entries, the cut beside them."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    env = {"FEDCOURTS_DATA_ROOT": str(data), "FEDCOURTS_METRICS_ROOT": str(tmp_path / "m")}
    out = tmp_path / "leaderboard.json"
    result = CliRunner().invoke(app, ["leaderboard", "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    board = read_model(out, Leaderboard)
    assert [e.predictor_id for e in board.entries] == ["alpha", "beta", "gamma"]
    assert sorted(_series(board.by_protocol)) == ALL_SERIES
    assert board.paired is not None and board.paired.events == 3
    # The command hands the pooled entries the pooled big-case agreement.
    assert {e.predictor_id: e.big_case.cases for e in board.entries if e.big_case} == {
        "alpha": 3,
        "beta": 3,
        "gamma": 3,
    }
    out = tmp_path / "claim-scores.json"
    result = CliRunner().invoke(app, ["claim-scores", "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    claims = read_model(out, ClaimScoreBoard)
    assert claims.forward_agreement is not None
    assert claims.forward_agreement.windows == []  # no cell here forms a pair


def test_a_two_window_registry_pools_claim_scores_and_ops_with_the_cut(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each predictor's score row pools its windows and lists them; the per-window
    rows are the cut beside it, and the rendered report shows both tables."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data)
    claims = build_claim_scores(run.cells, cell_windows=run.cell_windows)
    # No cell carries a claim block here, so no entry survives, and no cell forms
    # a validation pair: the validation lists only the series its pairs come from.
    assert claims.forward_agreement is not None
    assert claims.forward_agreement.pairs == 0
    assert claims.forward_agreement.windows == []
    substance = summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[(ev, stratum) for ev, stratum, _, _ in run.cells],
        cell_windows=run.cell_windows,
    )
    assert _series(substance.predictor_scores) == [
        ("alpha", None),
        ("beta", None),
        ("gamma", None),
    ]
    pooled = {row.predictor_id: row for row in substance.predictor_scores}
    # Two judges grade every cell: alpha's proc-a cells are cases 1 and 3.
    assert [(w.process_window, w.n) for w in pooled["alpha"].windows] == [
        ("proc-a", 4),
        ("proc-b", 2),
    ]
    assert [(w.process_window, w.n) for w in pooled["beta"].windows] == [("proc-a", 6)]
    assert sorted(_series(substance.predictor_scores_by_protocol)) == ALL_SERIES
    cut = {(r.predictor_id, r.process_window): r for r in substance.predictor_scores_by_protocol}
    # The pooled row is computed over the pooled cells, so its counts are the
    # cut rows' sums — never an average of them.
    assert pooled["alpha"].evaluations == (
        cut[("alpha", "proc-a")].evaluations + cut[("alpha", "proc-b")].evaluations
    )
    rendered = render_substance(substance)
    assert "| alpha | proc-a (n=4), proc-b (n=2) |" in rendered
    assert "**By protocol**" in rendered
    assert "| alpha | proc-a |" in rendered and "| alpha | proc-b |" in rendered


def test_a_pooled_score_row_is_the_cell_weighted_figure_over_both_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Three correct proc-a gradings and one wrong proc-b grading pool to 3/4, not
    to the mean of the windows' 1 and 0."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    run = stratify(data)
    stratified = []
    for ev, stratum, _, _ in run.cells:
        window = run.cell_windows[evaluation_key(ev)]
        copies = 3 if window.label == "proc-a" else 1
        for i in range(copies):
            graded = ev.model_copy(
                update={
                    "run_id": f"r{i}",
                    "correct": window.label == "proc-a",
                    "reasoning_quality": 0.5,
                }
            )
            stratified.append((graded, stratum))
    windows = {
        evaluation_key(graded): _window_of_case(run, graded.case_id) for graded, _ in stratified
    }
    substance = summarize_substance(
        cell_counts=(0, 0, 0), stratified_evaluations=stratified, cell_windows=windows
    )
    (row,) = substance.predictor_scores
    assert row.evaluations == 4 and row.accuracy == 0.75
    # The quantiles' grades name their rubric: one judge, one digest.
    assert [(r.evaluator_id, r.n) for r in row.rubrics] == [("e1", 4)]
    assert [(w.process_window, w.n) for w in row.windows] == [("proc-a", 3), ("proc-b", 1)]
    assert {r.process_window: r.accuracy for r in substance.predictor_scores_by_protocol} == {
        "proc-a": 1.0,
        "proc-b": 0.0,
    }


def _window_of_case(run: StratifiedRun, case_id: str) -> CountingWindow:
    """The one window ``run``'s cells on ``case_id`` count in."""
    (window,) = {w for key, w in run.cell_windows.items() if key[0] == case_id}
    return window


def test_evaluator_agreement_counts_only_the_reads_that_form_a_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A case only one judge read forms no leave-one-out point, so its reads list in
    neither that judge's composition nor any rubric count."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    event = CasePaths(data, "scotus", 2).event(EVENT)
    for predictor in ("alpha", "beta", "gamma"):
        evaluation = event.evaluation("e2", predictor, "r1")
        evaluation.unlink()
    agreement = evaluator_agreement(data)
    # e1 still read case 2, but alone: cases 1 and 3 are its points.
    assert agreement["e1"].events == 2
    assert sorted((w.predictor_id, w.process_window, w.n) for w in agreement["e1"].windows) == [
        ("alpha", "proc-a", 2),
        ("beta", "proc-a", 2),
        ("gamma", "proc-a", 1),
        ("gamma", "proc-b", 1),
    ]
    # Each point compares e1's three reads with e2's three, so six per case.
    assert {r.evaluator_id for r in agreement["e1"].rubrics} == {"e1", "e2"}
    assert sum(r.n for r in agreement["e1"].rubrics) == 12


def test_a_single_label_board_lists_its_one_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under one label the composition is still listed — it is part of the figure —
    but the report draws no by-protocol table, which would repeat every row."""
    set_windows(monkeypatch, CLOSED, BETA)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data)
    board = build_leaderboard(
        run.cells,
        evaluators=evaluator_agreement(data),
        facts=cell_facts(run.cells, data),
        cell_windows=run.cell_windows,
    )
    payload = board.model_dump(mode="json")
    assert "complete_grids" not in payload and "split_events_by_band" not in payload
    assert all(
        {w["process_window"] for w in agreement["windows"]} == {"proc-a"}
        for agreement in payload["evaluator_agreement"].values()
    )
    substance = summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[(ev, stratum) for ev, stratum, _, _ in run.cells],
        cell_windows=run.cell_windows,
    )
    rendered = render_substance(substance)
    assert "| alpha | proc-a (n=" in rendered
    assert "**By protocol**" not in rendered


def test_the_big_case_board_names_each_reads_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A census of stakes reads, one per predictor: not split by window, since
    nothing on it follows one forecaster — each read names its own window."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    frozen = build_big_case_board(data_root=data, process_scope="frozen")
    reads = {
        (row.case_id, read.predictor_id): read.process_window
        for row in frozen.rows
        for read in row.current_reads
    }
    assert reads[("scotus/3", "alpha")] == "proc-a"
    assert reads[("scotus/3", "gamma")] == "proc-b"
    census = build_big_case_board(data_root=data, process_scope="all")
    assert all(read.process_window is None for row in census.rows for read in row.current_reads)


def _successor_ledger(data: Path) -> None:
    """alpha on two cases across its two windows, beta on the first case only."""
    cells = {"scotus/1": {"alpha": (A, T1), "beta": (D, T1)}, "scotus/2": {"alpha": (B, T2)}}
    for case, held in cells.items():
        _event(data, case)
        latest = max(when for _, when in held.values())
        _outcome(data, case, resolved_at=(latest + timedelta(days=30)).date())
        for predictor, (digest, when) in held.items():
            _prediction(
                data, case, predictor_id=predictor, stamp=_pv(digest, when + timedelta(days=1))
            )
            _grade(data, case, "e1", predictor_id=predictor, stamped=latest + timedelta(days=31))


def test_a_successor_window_pools_into_its_predictor_and_ranks_over_paired_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """alpha's successor window pools into alpha's record; the rank is read over
    the one event both engines hold, and alpha's other event is its pairing loss."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
    _successor_ledger(data)
    run = stratify(data)
    board = build_leaderboard(
        run.cells, facts=cell_facts(run.cells, data), cell_windows=run.cell_windows
    )
    assert [(e.predictor_id, e.events_scored, e.paired_events) for e in board.entries] == [
        ("alpha", 2, 1),
        ("beta", 1, 1),
    ]
    assert board.paired is not None and board.paired.events == 1
    assert {e.predictor_id: e.unpaired_events for e in board.paired.entries} == {
        "alpha": 1,
        "beta": 0,
    }
    # One union denominates every pooled entry: beta covers one of two events.
    assert [
        (entry.predictor_id, against)
        for entry, against in coverage_shortfalls(board.events_scored, board.entries)
    ] == [("beta", 2)]
    assert [(e.predictor_id, e.process_window) for e in board.by_protocol] == [
        ("alpha", "proc-a"),
        ("alpha", "proc-b"),
        ("beta", "proc-a"),
    ]


def test_a_retired_predictor_keeps_its_record_but_leaves_the_paired_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """beta's only window closed with no successor: it keeps its pooled entry and
    its cut, unranked, and alpha pairs with itself over its own events."""
    owned = [
        CLOSED.model_copy(update={"predictor_id": "alpha"}),
        SUCCESSOR.model_copy(update={"predictor_id": "alpha"}),
        BETA.model_copy(update={"predictor_id": "beta", "closes": T2}),
    ]
    set_windows(monkeypatch, *owned)
    data = tmp_path / "data"
    _successor_ledger(data)
    run = stratify(data)
    board = build_leaderboard(
        run.cells, facts=cell_facts(run.cells, data), cell_windows=run.cell_windows
    )
    assert board.paired is not None and board.paired.predictors == ["alpha"]
    assert [(e.predictor_id, e.rank, e.paired_events) for e in board.entries] == [
        ("alpha", 1, 2),
        ("beta", None, None),
    ]
    assert board.predictors_ranked == 1
    # The all-versions board reads no registry, so beta is ranked there.
    everything = build_leaderboard(
        stratify(data, frozen_only=False).cells, process_scope="all", facts=None
    )
    assert everything.paired is not None
    assert everything.paired.predictors == ["alpha", "beta"]


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


def test_release_sensitivity_reads_only_counted_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An event's first forward cell is its counted cell's, never a later window's.

    The successor's cell sits in a live window, so a per-cell ``is_frozen``
    would admit it; it was stamped before the earlier window's revocation, so
    the event-aware rule counts it nowhere and the event carries no counted
    cell at all.
    """
    data = tmp_path / "data"
    _event(data, "scotus/1")
    _prediction(data, "scotus/1", run_id="p1", stamp=_pv(A, T1 + timedelta(days=1)), mode="forward")
    _prediction(data, "scotus/1", run_id="p2", stamp=_pv(B, T2 + timedelta(days=1)), mode="forward")

    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    (info,) = _cert_events(data)
    assert info.frozen_forward_runs == ("p1",)

    revoked = CLOSED.model_copy(update={"revoked_at": T2 + timedelta(days=10)})
    set_windows(monkeypatch, revoked, SUCCESSOR)
    assert process_version.is_frozen(_pv(B, T2 + timedelta(days=1)))
    assert _cert_events(data) == []


def test_big_case_agreement_keys_each_window_apart(
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
    frozen = big_case_agreement(data)
    assert {key: value.cases for key, value in frozen.items()} == {
        ("alpha", "proc-a"): 1,
        ("alpha", "proc-b"): 1,
    }
    assert {
        key: value.cases for key, value in big_case_agreement(data, frozen_only=False).items()
    } == {("alpha", None): 2}


def _joined(window: CountingWindow, predictor_id: str = "alpha") -> _JoinedCell:
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
        predictor_id=predictor_id,
    )


def test_tool_usage_pools_one_engine_across_two_windows_with_the_cut() -> None:
    """One engine's cells from two windows pool into one segment listing its series,
    and the cut keeps them as two; the coefficient row lists its series too, a
    single one included."""
    joined = [_joined(CLOSED), _joined(CLOSED), _joined(SUCCESSOR)]
    assert [(key[1], len(group)) for key, group in _segments(joined)] == [
        ("proc-a", 2),
        ("proc-b", 1),
    ]
    (pooled,) = [
        _segment(engine, None, mode, stage, moment, group)
        for (engine, mode, stage, moment), group in _grouped(joined, lambda c: c.pooled_key)
    ]
    assert pooled.cells == 3 and pooled.process_window is None
    assert [(w.process_window, w.n) for w in pooled.windows] == [("proc-a", 2), ("proc-b", 1)]
    # Two predictors sharing an engine under one label share a cut segment.
    beta = [_joined(CLOSED), _joined(BETA, predictor_id="beta")]
    assert [(key[1], len(group)) for key, group in _segments(beta)] == [("proc-a", 2)]
    row = _correlate(("forward", "cert", "distribution"), joined)
    assert [(w.process_window, w.n) for w in row.windows] == [("proc-a", 2), ("proc-b", 1)]
    assert [
        (w.process_window, w.n)
        for w in _correlate(("forward", "cert", "distribution"), joined[:2]).windows
    ] == [("proc-a", 2)]


def test_release_sensitivity_and_semantic_summary_pool_two_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Neither surface refuses a predictor whose cells span two windows: the
    rebuilt board projects the pooled entry with its composition and the cut, and
    the semantic census states the series it pools."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    run = stratify(data)
    board = rebuild(run.cells, data, {}, run.cell_windows)
    arm = project(board)[RANKED_ARM]
    assert arm["entries"]["alpha"]["windows"] == {"proc-a": 1, "proc-b": 1}
    assert arm["paired"]["engines"]["alpha"]["windows"] == {"proc-a": 1, "proc-b": 1}
    assert sorted(arm["by_protocol"]) == ["alpha@proc-a", "alpha@proc-b"]
    blocks = (
        "exact_pool_anchor",
        "rule_20_excluded",
        "post_conference_first_forecasts_excluded",
    )
    table = render_table(
        {
            "registered_headline": {"figures": project(board)},
            "blocks": {name: {"figures": {}} for name in blocks},
        }
    )
    assert "  alpha            pools proc-a (n=1), proc-b (n=1)" in table
    assert any("`by_protocol`" in line for line in table)
    for case in ("scotus/1", "scotus/2"):
        path = (
            CasePaths(data, "scotus", int(case.split("/")[1]))
            .event(EVENT)
            .evaluation("e1", "alpha", "r1")
        )
        evaluation = read_model(path, Evaluation)
        block = SemanticGradeBlock(
            declared_set_version=SEMANTIC_SET_V1,
            grades=[SemanticGrade(claim_id="majority-ground", grade=SemanticSupport.supported)],
        )
        write_json(path, evaluation.model_copy(update={"semantic_grades": block}))
    result = CliRunner().invoke(app, ["semantic-summary"], env={"FEDCOURTS_DATA_ROOT": str(data)})
    assert result.exit_code == 0, result.output
    assert "pooled over alpha proc-a (n=1), alpha proc-b (n=1)" in result.output


def test_a_cell_stamped_with_another_predictors_window_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A window records whose digest it counts, so a cell of another predictor
    carrying that digest is mis-attributed and the pass refuses it."""
    set_windows(monkeypatch, CLOSED.model_copy(update={"predictor_id": "beta"}))
    data = tmp_path / "data"
    _graded_ledger(data)
    with pytest.raises(ValueError, match="names another predictor"):
        stratify(data)
