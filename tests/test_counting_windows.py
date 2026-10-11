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
from fedcourtsai.process_version import PooledWindowsError
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.release_sensitivity import _cert_events
from fedcourtsai.schemas import (
    BigCaseAssessment,
    ClaimScoreBoard,
    CountingWindow,
    Evaluation,
    Leaderboard,
    Prediction,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import (
    event_has_claimable_prediction,
    predictor_holds_no_counted_prediction,
    scored_prediction,
    stratify,
)
from fedcourtsai.tool_usage import _correlate, _JoinedCell, _segments
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


def test_proc_v9_closes_claude_and_carries_codex_and_gemini_forward() -> None:
    """proc-v9's registry shape, as the freeze record's proc-v9 entry registers it.

    proc-v9 re-blesses claude-baseline alone on the predictor half. So the live
    codex-baseline and gemini-baseline digests must still be proc-v8's bytes —
    a predictor-prompt or engine-default edit that moved them would silently
    break the one unbroken window this label promises them — and their proc-v8
    windows stay open. claude-baseline's proc-v8 window closes at the proc-v9
    instant and its new digest's window opens there, labelled proc-v9.
    """
    claude_v8, codex_v8, gemini_v8 = PROC_V8_PREDICTOR_DIGESTS
    since = process_version.FROZEN_SINCE
    assert since is not None
    live = {
        entry.id: process_version.digest_for_actor(REPO, CONFIG, "predictor", entry.id)
        for entry in enabled_predictors(CONFIG / "predictors.yaml")
    }
    assert live["codex-baseline"] == codex_v8
    assert live["gemini-baseline"] == gemini_v8
    assert live["claude-baseline"] != claude_v8
    by_digest = {w.digest: w for w in process_version.COUNTING_WINDOWS}
    for carried in (codex_v8, gemini_v8):
        window = by_digest[carried]
        assert (window.label, window.opens, window.closes) == ("proc-v8", PROC_V8_INSTANT, None)
        # Carried forward byte-identical: proc-v8's audited bless moment, verbatim.
        assert process_version.FROZEN_PROCESS_DIGESTS[carried] == PROC_V8_INSTANT
    assert by_digest[claude_v8].closes == since
    successor = by_digest[live["claude-baseline"]]
    assert (successor.label, successor.opens, successor.closes) == ("proc-v9", since, None)
    assert len(process_version.COUNTING_WINDOWS) == 4


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


def test_a_predictor_keyed_pass_still_refuses_two_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The default pass refuses: a caller keyed on ``predictor_id`` alone gets no
    ledger it would pool. A series-keyed caller opts out and reads each cell's
    window instead."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR)
    data = tmp_path / "data"
    _graded_ledger(data)
    with pytest.raises(PooledWindowsError, match="alpha"):
        stratify(data)
    run = stratify(data, refuse_pooled_windows=False)
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
        stratify(data, refuse_pooled_windows=False)


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


def test_a_two_window_registry_builds_the_leaderboard_per_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One entry per (predictor, window), each over its own window's cells only;
    the complete grid read per window combination, the split event in none."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data, refuse_pooled_windows=False)
    board = build_leaderboard(
        run.cells,
        big_case=big_case_agreement(data),
        evaluators=evaluator_agreement(data),
        facts=cell_facts(run.cells, data),
        cell_windows=run.cell_windows,
    )
    assert sorted(_series(board.entries)) == ALL_SERIES
    scored = {(e.predictor_id, e.process_window): e.events_scored for e in board.entries}
    assert scored == {
        ("alpha", "proc-a"): 2,
        ("alpha", "proc-b"): 1,
        ("beta", "proc-a"): 3,
        ("gamma", "proc-a"): 1,
        ("gamma", "proc-b"): 2,
    }
    # Every entry's big-case agreement is its own window's, never both.
    cases = {(e.predictor_id, e.process_window): e.big_case for e in board.entries}
    assert cases[("alpha", "proc-a")] is not None and cases[("alpha", "proc-a")].cases == 2
    assert cases[("alpha", "proc-b")] is not None and cases[("alpha", "proc-b")].cases == 1
    # Cases 1 and 2 are complete under two different combinations; case 3 is split.
    assert board.complete_grid_by_band == {"(none)": 2}
    assert board.split_events_by_band == {"(none)": 1}
    assert [grid.windows for grid in board.complete_grids] == [
        {"alpha": "proc-a", "beta": "proc-a", "gamma": "proc-a"},
        {"alpha": "proc-b", "beta": "proc-a", "gamma": "proc-b"},
    ]
    assert [grid.by_band for grid in board.complete_grids] == [{"(none)": 1}, {"(none)": 1}]
    # The grader view pools the predictors' windows by design and says which.
    for agreement in board.evaluator_agreement.values():
        assert sorted((w.predictor_id, w.process_window) for w in agreement.windows) == ALL_SERIES
    # Cohorts list in the order their windows opened.
    alpha = [e.process_window for e in board.entries if e.predictor_id == "alpha"]
    assert alpha == ["proc-a", "proc-b"]


def test_a_two_window_registry_builds_the_cli_boards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The commands build rather than refuse: the wiring passes the series key."""
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    env = {"FEDCOURTS_DATA_ROOT": str(data), "FEDCOURTS_METRICS_ROOT": str(tmp_path / "m")}
    out = tmp_path / "leaderboard.json"
    result = CliRunner().invoke(app, ["leaderboard", "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    board = read_model(out, Leaderboard)
    assert sorted(_series(board.entries)) == ALL_SERIES
    assert board.split_events_by_band == {"(none)": 1}
    out = tmp_path / "claim-scores.json"
    result = CliRunner().invoke(app, ["claim-scores", "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    claims = read_model(out, ClaimScoreBoard)
    assert claims.forward_agreement is not None
    assert (
        sorted((w.predictor_id, w.process_window) for w in claims.forward_agreement.windows)
        == ALL_SERIES
    )


def test_a_two_window_registry_builds_claim_scores_and_ops_per_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_windows(monkeypatch, *TWO_LABELS)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data, refuse_pooled_windows=False)
    claims = build_claim_scores(run.cells, cell_windows=run.cell_windows)
    # No cell carries a claim block here, so no entry survives; the judge
    # validation still names the series its population spans.
    assert claims.forward_agreement is not None
    assert (
        sorted((w.predictor_id, w.process_window) for w in claims.forward_agreement.windows)
        == ALL_SERIES
    )
    substance = summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[(ev, stratum) for ev, stratum, _, _ in run.cells],
        cell_windows=run.cell_windows,
    )
    assert sorted(_series(substance.predictor_scores)) == ALL_SERIES
    rendered = render_substance(substance)
    assert "| alpha (proc-a) |" in rendered and "| alpha (proc-b) |" in rendered


def test_a_single_label_board_reads_as_it_did(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Under one label nothing is listed: no grid breakdown, no pooled-window
    list, no window in a rendered name — the registry before any successor."""
    set_windows(monkeypatch, CLOSED, BETA)
    data = tmp_path / "data"
    _two_label_ledger(data)
    run = stratify(data, refuse_pooled_windows=False)
    board = build_leaderboard(
        run.cells,
        evaluators=evaluator_agreement(data),
        facts=cell_facts(run.cells, data),
        cell_windows=run.cell_windows,
    )
    payload = board.model_dump(mode="json")
    assert "complete_grids" not in payload and "split_events_by_band" not in payload
    assert all("windows" not in agreement for agreement in payload["evaluator_agreement"].values())
    substance = summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[(ev, stratum) for ev, stratum, _, _ in run.cells],
        cell_windows=run.cell_windows,
    )
    assert "| alpha |" in render_substance(substance)


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


def test_a_successor_entry_shares_no_grid_it_does_not_cover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One combination holds every complete event, yet a successor entry sits
    beside it with an equal count over events it shares with nobody: the grids
    are listed whenever the entries carry two labels, so the successor's entry
    is visibly in no grid rather than certified against the total."""
    set_windows(monkeypatch, CLOSED, SUCCESSOR, BETA)
    data = tmp_path / "data"
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
    run = stratify(data, refuse_pooled_windows=False)
    board = build_leaderboard(
        run.cells, facts=cell_facts(run.cells, data), cell_windows=run.cell_windows
    )
    assert board.complete_grid_by_band == {"(none)": 1}
    assert [grid.windows for grid in board.complete_grids] == [
        {"alpha": "proc-a", "beta": "proc-a"}
    ]
    # Coverage is read within a label's cohort: alpha@proc-b is short of nothing.
    assert coverage_shortfalls(board.events_scored, board.entries) == []
    # Ranks restart per label: the successor's entry is ranked in its own cohort.
    assert [(e.predictor_id, e.process_window, e.rank) for e in board.entries] == [
        ("alpha", "proc-a", 1),
        ("beta", "proc-a", 2),
        ("alpha", "proc-b", 1),
    ]


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


def test_tool_usage_splits_one_engine_across_two_windows() -> None:
    """One engine's cells from two windows are two segments, never one mean; the
    coefficient row pools engines by design and names the series it pools."""
    joined = [_joined(CLOSED), _joined(CLOSED), _joined(SUCCESSOR)]
    segments = [(key[1], len(group)) for key, group in _segments(joined)]
    assert segments == [("proc-a", 2), ("proc-b", 1)]
    # Two predictors sharing an engine under one label pool as before.
    beta = [_joined(CLOSED), _joined(BETA, predictor_id="beta")]
    assert [(key[1], len(group)) for key, group in _segments(beta)] == [("proc-a", 2)]
    row = _correlate(("forward", "cert", "distribution"), joined)
    assert [(w.process_window, w.n) for w in row.windows] == [("proc-a", 2), ("proc-b", 1)]
    # Under one label nothing is listed.
    assert _correlate(("forward", "cert", "distribution"), joined[:2]).windows == []
