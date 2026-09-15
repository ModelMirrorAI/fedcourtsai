"""Tests for the interim amicus re-derivation and re-freeze pass.

The properties no other suite covers, and the ones a stats-reviewer checks:

- The corpus write is a **direct UPDATE** deliberately outside the upsert path's
  max latch, because the end-of-day cut moves a resolved application's count
  *down* and the latch is built to reject exactly that. The first test proves
  both halves — the sweep's write lands, the same value through ``upsert_rows``
  does not — because a silent no-op reading as convergence is the hazard.
- The re-freeze rewrites the committed outcome's ``interim_signals.amicus_briefs``
  and **leaves ``context.amicus_briefs`` on the prediction untouched**: the two
  ends of the ``amicus-increment`` claim move at different times by design.
- The dry run writes nothing, the bound refuses whole, and the frozen-value
  distribution the ledger reports matches the affected set.
- The re-grade backlog is a **dispatch input**, so it lists only cells
  ``stamp-cell --regrade`` would accept — the surviving run of each (evaluator,
  predictor), stamped. A cell the re-grade would refuse is reported with its
  reason instead, because the refusal aborts the whole paste rather than
  skipping the line.
"""

from __future__ import annotations

import random
import re
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import typer

from fedcourtsai import corpus
from fedcourtsai.cli import _echo_regrade_backlog, _refuse_unregradable
from fedcourtsai.integrity import latest_evaluation_runs
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.amicus_rederive import _regrade_cells, rederive_amicus_briefs
from fedcourtsai.schemas import (
    Disposition,
    Evaluation,
    InterimResolutionSignals,
    Outcome,
    Prediction,
    PredictionContext,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json

_EVENT = "evt-motion-disposition"

_RUN_REPAIR = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "run-repair.yml"


def _regrade_pattern() -> str:
    """The cell grammar `run-repair`'s re-grade selector greps, read from the workflow.

    The workflow carries the pattern twice — the fail-fast copy in the selector
    validation and the step of record — kept word-for-word identical so one
    mistake cannot produce two differently worded refusals. Both are read and
    required to agree, so this helper cannot quietly pick the stale one.
    """
    patterns = {str(found) for found in re.findall(r"pattern='([^']+)'", _RUN_REPAIR.read_text())}
    assert len(patterns) == 1, f"run-repair's regrade cell grammars have drifted: {patterns}"
    return patterns.pop()


def _row(case_id: str, docket: str, *, amicus_briefs: int) -> corpus.CorpusRow:
    """A live-slice, application-parsed interim docket carrying a stored count."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket,
        case_name="Marbury Power Cooperative v. Ellison",
        last_live_polled=date(2026, 8, 1),
        disposition=Disposition.granted,
        application_kind="substantive",
        response_requested=True,
        referred_to_court=True,
        amicus_briefs=amicus_briefs,
    )


def _live(*entries: tuple[str, str]) -> dict[str, object]:
    """A live-shaped snapshot — the channel the interim column is populated from."""
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


def _stored(conn: sqlite3.Connection, case_id: str) -> int | None:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row.amicus_briefs


# A resolved application whose count *falls* under the end-of-day cut: one amicus
# before the denial, one after it. Unbounded reads 2; the cut at the disposition
# day reads 1. The stored column latched the higher 2 across polls.
_CUT_SNAPSHOT = _live(
    ("2026-06-25", "Brief amicus curiae of Alpha Coalition filed."),
    ("2026-07-01", "Application (26A700) denied."),
    ("2026-07-10", "Brief amicus curiae of Beta Institute filed."),
)
# A resolved application the widened reading reads *higher* than the retired one:
# the brief is docketed in the **submitted** form, which the accepted-form-only
# reading did not count and `amicus_briefs`' second arm does. Stored 0 is what the
# old reading produced from this very snapshot, so this row exercises the widening
# itself rather than a seeded disagreement.
_RISE_SNAPSHOT = _live(
    ("2026-06-20", "Amicus brief of Gamma Trust submitted."),
    ("2026-06-22", "Application (26A701) granted."),
)


def _seed_corpus(conn: sqlite3.Connection) -> None:
    corpus.upsert_rows(
        conn,
        [
            _row("scotus/700", "26A700", amicus_briefs=2),
            _row("scotus/701", "26A701", amicus_briefs=0),
        ],
    )
    corpus.upsert_snapshot(conn, "scotus/700", date(2026, 7, 10), _CUT_SNAPSHOT)
    corpus.upsert_snapshot(conn, "scotus/701", date(2026, 6, 22), _RISE_SNAPSHOT)


def _write_outcome(data_root: Path, case_id: str, docket: int, *, amicus: int) -> Path:
    """A committed interim outcome frozen with an amicus count under the old reading."""
    paths = CasePaths(data_root, "scotus", docket).event(_EVENT)
    write_json(
        paths.outcome,
        Outcome(
            case_id=case_id,
            event_id=_EVENT,
            resolved_at=date(2026, 7, 1),
            actual_disposition=Disposition.granted,
            actual_granted=1,
            interim_signals=InterimResolutionSignals(
                response_requested=True,
                referred_to_court=True,
                amicus_briefs=amicus,
            ),
        ),
    )
    return paths.outcome


def _write_prediction(data_root: Path, case_id: str, docket: int, *, context_amicus: int) -> Path:
    """A committed prediction whose frozen context carries its own amicus count."""
    paths = CasePaths(data_root, "scotus", docket).event(_EVENT)
    path = paths.prediction("claude-baseline", "20260101T000000Z")
    write_json(
        path,
        Prediction(
            case_id=case_id,
            event_id=_EVENT,
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id="20260101T000000Z",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.4,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="replay",
                snapshot_date=date(2026, 6, 24),
                signals_observable=True,
                amicus_briefs=context_amicus,
            ),
        ),
    )
    return path


def _write_evaluation(
    data_root: Path,
    docket: int,
    run_id: str,
    *,
    evaluator: str = "claude-judge",
    predictor: str = "claude-baseline",
    stamped: bool = True,
) -> Path:
    """One committed grading under the event, as the harness leaves it.

    A schema-true record rather than a stub, because the backlog walk now reads
    these files: the collapse to a surviving run and the stamp check are both
    properties of the record, not of the directory it sits in. The harness clock
    the collapse orders on is the process stamp, so it is derived from the run id
    — the newer run is newer on both, as it is in the ledger.
    """
    stamped_at = datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    path = (
        CasePaths(data_root, "scotus", docket)
        .event(_EVENT)
        .evaluation(evaluator, predictor, run_id)
    )
    write_json(
        path,
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=_EVENT,
            predictor_id=predictor,
            evaluator_id=evaluator,
            engine="claude-code",
            run_id=run_id,
            created_at=stamped_at,
            correct=1,
            process_version=(
                ProcessVersion(label="proc-v4", digest="sha256:abc", stamped_at=stamped_at)
                if stamped
                else None
            ),
        ),
    )
    return path


def test_the_direct_update_lands_a_cut_count_the_upsert_latch_would_eat(tmp_path: Path) -> None:
    """The corpus half's whole reason for existing, shown against the path it avoids.

    ``amicus_briefs`` is max-latched on upsert so a degraded payload cannot lower
    a stored count. The end-of-day cut *is* a lower count on a resolved
    application, so the same write through ``upsert_rows`` is a silent no-op that
    reads as convergence — the control arm — while the sweep's direct UPDATE
    lands it.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        assert _stored(conn, "scotus/700") == 2
        # The control: the cut count offered to the ordinary write path. The latch
        # takes the larger of stored and incoming, so nothing moves — and nothing
        # reports that nothing moved, which is the hazard.
        corpus.upsert_rows(conn, [_row("scotus/700", "26A700", amicus_briefs=1)])
        assert _stored(conn, "scotus/700") == 2, "the latch was expected to eat the cut count"
        result = rederive_amicus_briefs(conn, tmp_path / "data", apply=True, max_changes=10)
        assert _stored(conn, "scotus/700") == 1
        # The widening reads the old-reading 0 up to 1 — an increase the latch
        # would have accepted, but written here in the same pass.
        assert _stored(conn, "scotus/701") == 1
    assert (result.applied, result.refused) == (True, False)
    assert (result.corpus_changed, result.corpus_decreased, result.corpus_increased) == (2, 1, 1)
    assert sorted(result.corpus_changed_case_ids) == ["scotus/700", "scotus/701"]
    # The magnitude beside the row count: |2-1| + |0-1|.
    assert result.amicus_shift_entries == 2
    # The per-row ledger is the procedural replacement for the latch this write
    # bypasses, so it must carry both directions with their old and new counts.
    assert {(m.case_id, m.was, m.now) for m in result.corpus_moves} == {
        ("scotus/700", 2, 1),
        ("scotus/701", 0, 1),
    }


def test_a_degraded_or_uncounted_row_is_reported_and_never_lowered(tmp_path: Path) -> None:
    """The claims that replace the bypassed max latch, exercised.

    The latch rejected any regression from any cause; what stands in its place is
    narrower, so the three arms it leaves standing are pinned here: a row with no
    live-shaped snapshot at all, a row whose snapshot discloses no entries (the
    served shell a confident 0 would otherwise be written from), and a row whose
    stored count is null — the interim family's coverage sentinel, which the pass
    reports rather than fills.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/810", "26A810", amicus_briefs=4),  # no snapshot at all
                _row("scotus/811", "26A811", amicus_briefs=5),  # snapshot, no entries
                corpus.CorpusRow(  # application-parsed, but no stored count
                    case_id="scotus/812",
                    court="scotus",
                    docket_number="26A812",
                    case_name="Doe v. Roe",
                    last_live_polled=date(2026, 8, 1),
                    disposition=Disposition.denied,
                    application_kind="substantive",
                ),
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/811", date(2026, 7, 1), _live())
        corpus.upsert_snapshot(
            conn,
            "scotus/812",
            date(2026, 7, 1),
            _live(("2026-07-01", "Application (26A812) denied.")),
        )
        result = rederive_amicus_briefs(conn, tmp_path / "data", apply=True, max_changes=10)
        # Every one of them keeps exactly what it carried.
        assert _stored(conn, "scotus/810") == 4
        assert _stored(conn, "scotus/811") == 5
        assert _stored(conn, "scotus/812") is None
    assert (result.corpus_changed, result.corpus_moves) == (0, [])
    # The two unreadable rows are counted apart from the never-counted one, so the
    # ledger's denominators stay honest.
    assert result.unobservable == 2
    assert result.no_stored_count == 1
    assert result.eligible == 3


def test_the_refreeze_rewrites_interim_signals_but_leaves_context_untouched(
    tmp_path: Path,
) -> None:
    """The scope constraint a stats-reviewer checks: the resolution end moves, the
    prediction end does not, and the two flags in the block are left alone."""
    data_root = tmp_path / "data"
    outcome_path = _write_outcome(data_root, "scotus/700", 700, amicus=2)
    prediction_path = _write_prediction(data_root, "scotus/700", 700, context_amicus=2)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=True, max_changes=10)

    refrozen = read_model(outcome_path, Outcome)
    assert refrozen.interim_signals is not None
    # The amicus count moved to the re-derived value...
    assert refrozen.interim_signals.amicus_briefs == 1
    # ...and the two flags the widened reading does not touch are exactly as frozen.
    assert refrozen.interim_signals.response_requested is True
    assert refrozen.interim_signals.referred_to_court is True

    # The prediction end is never re-derived: context.amicus_briefs is frozen by
    # design, and no prediction.json is opened.
    prediction = read_model(prediction_path, Prediction)
    assert prediction.context is not None
    assert prediction.context.amicus_briefs == 2
    assert result.context_amicus_untouched is True
    assert (result.outcomes_refrozen, result.cases_refrozen) == (1, 1)
    assert result.refrozen[0].ref == "scotus/700/evt-motion-disposition"
    assert (result.refrozen[0].was, result.refrozen[0].now) == (2, 1)


def test_the_refreeze_names_the_regrade_cells_it_puts_in_the_backlog(tmp_path: Path) -> None:
    """The re-grade debt is emitted in the grammar the selector parses.

    The re-freeze moves a value a committed grade was computed from, so it owes a
    `regrade-stale` dispatch. Emitting the cells here is what lets that dispatch be
    copied off the ledger rather than reconstructed by hand — and the cells are
    per (evaluator, run), not per predictor, since one evaluator cell grades the
    predictions under it.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    for evaluator in ("claude-judge", "codex-judge"):
        for predictor in ("claude-baseline", "gemini-baseline"):
            _write_evaluation(
                data_root, 700, "20260825T024608Z", evaluator=evaluator, predictor=predictor
            )
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    # Two evaluators x one run: the two predictor directories under each collapse
    # to one cell, and the grammar is court/docket/event/run_id/actor.
    assert entry.regrade_cells == [
        f"scotus/700/{_EVENT}/20260825T024608Z/claude-judge",
        f"scotus/700/{_EVENT}/20260825T024608Z/codex-judge",
    ]
    # And the grammar is the workflow's own, read out of it rather than retyped:
    # these cells are emitted so a maintainer can paste them into `repair_target`,
    # and the selector greps every line against this pattern. The two surfaces are
    # written in different languages and nothing at runtime holds them together, so
    # a cell this pass emits that the dispatch would refuse is the drift to catch.
    pattern = _regrade_pattern()
    for cell in entry.regrade_cells:
        assert re.match(pattern, cell), f"{cell!r} is not a cell run-repair would accept"


def test_a_twice_graded_cell_names_only_the_surviving_run(tmp_path: Path) -> None:
    """The backlog is a dispatch input, so it collapses re-runs the way scoring does.

    A judge that graded this cell twice leaves two run directories describing one
    observation. `stamp-cell --regrade` refuses the superseded one — recomputing
    it moves no published number while reading as landed — and the first refusal
    aborts the whole dispatch, so naming both runs makes the list unusable rather
    than merely long. Only the surviving run is named, on the same collapse
    `integrity.latest_evaluation_runs` applies everywhere else.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    for run_id in ("20260824T231401Z", "20260825T024608Z"):
        for predictor in ("claude-baseline", "gemini-baseline"):
            _write_evaluation(data_root, 700, run_id, predictor=predictor)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    assert entry.regrade_cells == [f"scotus/700/{_EVENT}/20260825T024608Z/claude-judge"]
    # The superseded run is not reported either: the surviving run beside it is
    # listed, and that dispatch is the whole of the debt this event owes.
    assert entry.regrade_blocked == []


def test_an_unstamped_grading_is_reported_rather_than_listed(tmp_path: Path) -> None:
    """A cell with no process stamp is debt the ledger names and no dispatch pays.

    `stamp-cell --regrade` preserves the stamp of the process that produced the
    record, so a cell carrying none has nothing for it to preserve and the
    re-grade refuses. Listing it would abort the paste; dropping it silently
    would hide a number standing against a moved resolution end — so it is
    reported, with the reason, beside the dispatchable list.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    _write_evaluation(data_root, 700, "20260825T024608Z", stamped=False)
    _write_evaluation(data_root, 700, "20260825T024608Z", evaluator="codex-judge")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    # The stamped judge is dispatchable; the unstamped one is not, and the two
    # are kept apart rather than pooled into a list that would refuse whole.
    assert entry.regrade_cells == [f"scotus/700/{_EVENT}/20260825T024608Z/codex-judge"]
    assert entry.regrade_blocked == [
        f"scotus/700/{_EVENT}/20260825T024608Z/claude-judge — unstamped, not re-gradable: "
        + "it takes the ordinary stamp instead"
    ]


def test_a_run_superseded_for_one_predictor_only_is_reported_not_listed(
    tmp_path: Path,
) -> None:
    """A partly superseded run is the one exclusion that leaves a debt unpayable.

    One `--regrade` dispatch writes every `evaluations/<judge>/*/<run>/` record
    under the cell, so a run that survives for one predictor while a later run
    supersedes it for another is refused whichever of the two is named. The
    surviving half is therefore not dispatchable through either run, and the
    ledger says so instead of emitting a line that would abort the paste.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    _write_evaluation(data_root, 700, "20260824T231401Z", predictor="claude-baseline")
    _write_evaluation(data_root, 700, "20260824T231401Z", predictor="gemini-baseline")
    # Only `claude-baseline` was re-graded, so the earlier run still wins for
    # `gemini-baseline` and loses for `claude-baseline`.
    _write_evaluation(data_root, 700, "20260825T024608Z", predictor="claude-baseline")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    assert entry.regrade_cells == [f"scotus/700/{_EVENT}/20260825T024608Z/claude-judge"]
    assert entry.regrade_blocked == [
        f"scotus/700/{_EVENT}/20260824T231401Z/claude-judge — superseded in part, not "
        + "re-gradable: this judge's run survives for one predictor and is superseded "
        + "for another, so no dispatch reaches it"
    ]


def test_an_empty_evaluation_directory_names_no_cell(tmp_path: Path) -> None:
    """A leftover directory holding no record is not a re-grade the ledger owes.

    `stamp-cell --regrade` globs for the `evaluation.json` files under the cell
    and exits non-zero when it finds none, so a provisioned-but-empty directory
    is a refusal rather than a cell — naming it costs the dispatch it rides in.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    leftover = (
        CasePaths(data_root, "scotus", 700)
        .event(_EVENT)
        .evaluation("claude-judge", "claude-baseline", "20260825T024608Z")
    )
    leftover.parent.mkdir(parents=True, exist_ok=True)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    assert (entry.regrade_cells, entry.regrade_blocked) == ([], [])


def test_an_unparseable_grading_costs_a_line_and_not_the_ledger(tmp_path: Path) -> None:
    """A record that does not parse is `validate`'s to fail on and this pass's to survive.

    The ledger is the reading the apply's `--max-changes` bound comes from, and
    the corpus half of it rides in the same report, so one unreadable committed
    record must not take the whole reading with it.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    _write_evaluation(data_root, 700, "20260825T024608Z", evaluator="codex-judge")
    broken = _write_evaluation(data_root, 700, "20260825T024608Z")
    broken.write_text("{not json")
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)

    # The corpus half of the reading is intact, which is the point of surviving.
    assert result.corpus_changed == 2
    (entry,) = [e for e in result.refrozen if e.ref.startswith("scotus/700/")]
    assert entry.regrade_cells == [f"scotus/700/{_EVENT}/20260825T024608Z/codex-judge"]
    assert entry.regrade_blocked == [
        f"scotus/700/{_EVENT}/20260825T024608Z/claude-judge — unreadable, not re-gradable: "
        + "the record does not parse"
    ]


def test_every_listed_cell_is_one_the_regrade_accepts(tmp_path: Path) -> None:
    """The property the whole split exists for, checked against the gate itself.

    Two surfaces in two modules decide this — the ledger that names a cell and
    the command that admits one — and nothing at runtime holds them together, so
    the coupling is asserted over a randomized ledger rather than argued in two
    docstrings. `_refuse_unregradable` is the gate `stamp-cell --regrade` runs
    before its first write: a listed cell must pass it, a reported one must not,
    and no surviving grading may fall out of both lists.
    """
    runs = ("20260824T231401Z", "20260825T024608Z")
    evaluators = ("claude-judge", "codex-judge")
    predictors = ("claude-baseline", "gemini-baseline")
    slots = [(e, p, r) for e in evaluators for p in predictors for r in runs]
    rng = random.Random(7)
    for trial in range(40):
        data_root = tmp_path / f"trial-{trial}" / "data"
        present = [slot for slot in slots if rng.random() < 0.5]
        if not present:
            continue
        for evaluator, predictor, run_id in present:
            _write_evaluation(
                data_root,
                700,
                run_id,
                evaluator=evaluator,
                predictor=predictor,
                stamped=rng.random() < 0.75,
            )
        event_paths = CasePaths(data_root, "scotus", 700).event(_EVENT)
        backlog = _regrade_cells(event_paths.base, "scotus/700", _EVENT)
        reported = {line.split(" — ")[0] for line in backlog.blocked}
        for evaluator in evaluators:
            for run_id in runs:
                targets = sorted(
                    (event_paths.base / "evaluations" / evaluator).glob(
                        f"*/{run_id}/evaluation.json"
                    )
                )
                if not targets:
                    continue
                line = f"scotus/700/{_EVENT}/{run_id}/{evaluator}"
                try:
                    _refuse_unregradable(targets, event_paths, evaluator, run_id)
                except typer.Exit:
                    assert line not in backlog.cells, f"{line} is listed and would refuse"
                else:
                    assert line in backlog.cells, f"{line} would be accepted and is not listed"
        # And nothing a scoring surface still reads is dropped without a word:
        # every surviving grading is either dispatchable or reported.
        graded = [
            (path, read_model(path, Evaluation))
            for path in sorted(event_paths.base.glob("evaluations/*/*/*/evaluation.json"))
        ]
        for path, _ in latest_evaluation_runs(graded, lambda item: item[1]):
            run_dir = path.parent
            line = f"scotus/700/{_EVENT}/{run_dir.name}/{run_dir.parent.parent.name}"
            assert line in backlog.cells or line in reported, f"{line} is silently dropped"


def test_the_ledger_prints_the_two_halves_apart(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The run summary is where this lands, so the separation is pinned as text.

    A blocked line pasted into `repair_target` refuses the whole dispatch, so it
    must never appear under the header a maintainer copies from — and it must
    appear somewhere, since an unpayable debt that prints nowhere is one nobody
    triages.
    """
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    _write_evaluation(data_root, 700, "20260824T231401Z")
    _write_evaluation(data_root, 700, "20260825T024608Z")
    _write_evaluation(data_root, 700, "20260825T024608Z", evaluator="codex-judge", stamped=False)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)
    _echo_regrade_backlog(result)

    printed = capsys.readouterr().out
    listed, _, reported = printed.partition("regrade-stale: ")
    assert "1 dispatchable evaluator cell(s)" in listed
    assert f"  scotus/700/{_EVENT}/20260825T024608Z/claude-judge\n" in listed
    # The superseded run is named nowhere, and the unstamped judge only below.
    assert "20260824T231401Z" not in printed
    assert "codex-judge" not in listed
    assert "1 further cell(s) a re-grade would refuse" in reported
    assert "codex-judge — unstamped, not re-gradable" in reported


def test_a_dry_run_reports_the_plan_and_writes_nothing(tmp_path: Path) -> None:
    """The dry run is the maintainer's reading, so it must not be the write —
    on either store, and the committed-side ledger is honest before the column moves."""
    data_root = tmp_path / "data"
    outcome_path = _write_outcome(data_root, "scotus/700", 700, amicus=2)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=False)
        assert _stored(conn, "scotus/700") == 2
    assert read_model(outcome_path, Outcome).interim_signals.amicus_briefs == 2  # type: ignore[union-attr]
    assert result.applied is False
    # The plan the dry run describes is exactly what an apply would write.
    assert (result.corpus_changed, result.outcomes_refrozen) == (2, 1)
    assert result.total_changes == 3


def test_the_blast_radius_bound_refuses_the_apply_and_writes_nothing(tmp_path: Path) -> None:
    """Above the bound the pass refuses whole — never a partial write across the two stores."""
    data_root = tmp_path / "data"
    outcome_path = _write_outcome(data_root, "scotus/700", 700, amicus=2)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        result = rederive_amicus_briefs(conn, data_root, apply=True, max_changes=1)
        assert _stored(conn, "scotus/700") == 2
    assert read_model(outcome_path, Outcome).interim_signals.amicus_briefs == 2  # type: ignore[union-attr]
    assert (result.applied, result.refused) == (True, True)
    assert result.total_changes == 3


def test_the_frozen_value_distribution_matches_the_affected_set(tmp_path: Path) -> None:
    """The ledger reports the frozen-amicus distribution across the committed worklist,
    the shape the freeze-record entry pre-computes so a reader can confirm the set."""
    data_root = tmp_path / "data"
    # Three committed interim outcomes carrying frozen amicus counts {0, 0, 2}.
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    _write_outcome(data_root, "scotus/701", 701, amicus=0)
    _write_outcome(data_root, "scotus/702", 702, amicus=0)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)  # 702 has no corpus row → unresolvable, left as frozen
        result = rederive_amicus_briefs(conn, data_root, apply=False)
    assert result.outcomes_with_interim == 3
    assert result.interim_amicus_distribution == {0: 2, 2: 1}
    # 702 carries no walked corpus row, so its block cannot be re-derived and is
    # reported rather than touched.
    assert result.outcomes_unresolvable == 1


def test_an_open_application_is_left_to_the_live_channel(tmp_path: Path) -> None:
    """A docket with no readable disposition date has no end-of-day cut to apply,
    so it is counted `open_no_cut` and never written — the live channel owns it."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/800", "26A800", amicus_briefs=3)])
        corpus.upsert_snapshot(
            conn,
            "scotus/800",
            date(2026, 6, 20),
            _live(("2026-06-20", "Brief amicus curiae of Delta League filed.")),
        )
        result = rederive_amicus_briefs(conn, tmp_path / "data", apply=True, max_changes=10)
        assert _stored(conn, "scotus/800") == 3
    assert (result.open_no_cut, result.corpus_changed) == (1, 0)


def test_the_pass_is_idempotent_a_re_run_reports_no_change(tmp_path: Path) -> None:
    """Re-running after an apply is the control: the reading is fixed in code, so a
    converged corpus and converged outcomes report `total_changes == 0`."""
    data_root = tmp_path / "data"
    _write_outcome(data_root, "scotus/700", 700, amicus=2)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        _seed_corpus(conn)
        first = rederive_amicus_briefs(conn, data_root, apply=True, max_changes=10)
        assert first.total_changes == 3
        second = rederive_amicus_briefs(conn, data_root, apply=True, max_changes=10)
    assert second.total_changes == 0
    assert (second.corpus_changed, second.outcomes_refrozen) == (0, 0)
