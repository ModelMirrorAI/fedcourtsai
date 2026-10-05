"""`conference-set --counted`: the counted cohort cut by conference at the cell's cut."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.cohort_cut import cell_bound, counted_by_conference
from fedcourtsai.ids import parse_run_id
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    CountedConferenceCut,
    CountingWindow,
    Disposition,
    Engine,
    Evaluation,
    EventKind,
    ExportCorpusVintage,
    Outcome,
    PredictableEvent,
    Prediction,
    PredictionContext,
    ProcessVersion,
)
from fedcourtsai.serialize import write_json, write_yaml
from tests.conftest import bless_process, set_windows

runner = CliRunner()

BLESSED = "sha256:blessed"
EVENT = "evt-petition-disposition"

#: Distributed for a conference already past on the registration day.
PAST = {
    "CaseNumber": "25-106",
    "ProceedingsandOrder": [
        {"Date": "Jun 02 2026", "Text": "DISTRIBUTED for Conference of 6/18/2026."},
    ],
}

#: Distributed for 9/28, then relisted to 10/9 on 9/20.
RELISTED = {
    "CaseNumber": "25-100",
    "ProceedingsandOrder": [
        {"Date": "Jul 01 2026", "Text": "DISTRIBUTED for Conference of 9/28/2026."},
        {"Date": "Sep 20 2026", "Text": "DISTRIBUTED for Conference of 10/9/2026."},
    ],
}


def _stamp(digest: str, when: datetime) -> ProcessVersion:
    return ProcessVersion(
        label="proc-v1",
        digest=digest,
        stamped_at=when,
        pipeline_sha="abc123",
    )


def _event(data_root: Path, case_id: str) -> None:
    court, _, docket = case_id.partition("/")
    write_yaml(
        CasePaths(data_root, court, int(docket)).event(EVENT).event_file,
        PredictableEvent(
            event_id=EVENT, case_id=case_id, kind=EventKind.petition, title=f"P v. R ({case_id})"
        ),
    )


def _prediction(
    data_root: Path,
    case_id: str,
    *,
    predictor_id: str = "alpha",
    run_id: str = "20260917T000000Z",
    snapshot: date = date(2026, 9, 17),
    cutoff: date | None = None,
    band: str = "baseline",
    digest: str | None = BLESSED,
) -> None:
    court, _, docket = case_id.partition("/")
    write_json(
        CasePaths(data_root, court, int(docket)).event(EVENT).prediction(predictor_id, run_id),
        Prediction(
            case_id=case_id,
            event_id=EVENT,
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id=run_id,
            # The harness clock stages the newest cell, so it follows the run id.
            created_at=parse_run_id(run_id),
            input_snapshot="corpus",
            granted=0,
            probability=0.1,
            predicted_disposition=Disposition.denied,
            process_version=_stamp(digest, parse_run_id(run_id)) if digest else None,
            context=PredictionContext(
                mode="forward",
                snapshot_date=snapshot,
                cutoff=cutoff,
                cut_kind="date" if cutoff else None,
                signals_observable=True,
                band=band,
                salience_version="sal-v4",
                term=2025,
            ),
        ),
    )


CASES = tuple(f"scotus/{n}" for n in range(100, 108))


def _outcome(data_root: Path, case_id: str, resolved_at: date = date(2026, 10, 5)) -> None:
    court, _, docket = case_id.partition("/")
    write_json(
        CasePaths(data_root, court, int(docket)).event(EVENT).outcome,
        Outcome(
            case_id=case_id,
            event_id=EVENT,
            resolved_at=resolved_at,
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )


def _grade(data_root: Path, case_id: str, *, prediction_run_id: str) -> None:
    court, _, docket = case_id.partition("/")
    write_json(
        CasePaths(data_root, court, int(docket)).event(EVENT).evaluation("judge", "alpha", "e1"),
        Evaluation(
            case_id=case_id,
            event_id=EVENT,
            predictor_id="alpha",
            evaluator_id="judge",
            engine=Engine.codex,
            run_id="e1",
            prediction_run_id=prediction_run_id,
            created_at=datetime(2026, 10, 6, tzinfo=UTC),
            correct=1,
            brier_score=0.01,
            leakage_suspected=False,
            process_version=_stamp("sha256:judge", datetime(2026, 10, 6, tzinfo=UTC)),
        ),
    )


def _corpus(corpus_root: Path, payloads: dict[str, dict[str, Any]]) -> Path:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"25-{case_id.rpartition('/')[2]}",
                    # The live column has moved on: the relist's conference.
                    distributed_for_conference=date(2026, 10, 9),
                )
                for case_id in CASES
            ],
        )
        for case_id, payload in payloads.items():
            corpus.upsert_snapshot(conn, case_id, date(2026, 9, 25), payload)
        conn.commit()
    return db


@pytest.fixture
def ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.delenv("FEDCOURTS_CORPUS_SPLIT", raising=False)
    bless_process(monkeypatch, BLESSED)
    data_root = tmp_path / "data"
    # 100: re-owed (a de-counted cell beside the counted one), cut before the relist.
    _event(data_root, "scotus/100")
    _prediction(data_root, "scotus/100", run_id="20260801T000000Z", digest=None)
    _prediction(data_root, "scotus/100")
    _outcome(data_root, "scotus/100")
    # 101: one predictor cut the day before the relist entry, one on its day —
    # bounds 9/20 (the entry filed on the bound is excluded) and 9/21 (included).
    _event(data_root, "scotus/101")
    _prediction(data_root, "scotus/101", snapshot=date(2026, 9, 19))
    _prediction(
        data_root,
        "scotus/101",
        predictor_id="beta",
        snapshot=date(2026, 9, 20),
        band="elevated",
    )
    # 102: no live payload — the current column stands in, and says so.
    _event(data_root, "scotus/102")
    _prediction(data_root, "scotus/102")
    # 103: the staged (newest) cell is de-counted — not counted, though an older one is.
    _event(data_root, "scotus/103")
    _prediction(data_root, "scotus/103")
    _prediction(data_root, "scotus/103", run_id="20260920T000000Z", digest="sha256:decounted")
    # 104: de-counted cells only, made before registration — registered, never counted.
    _event(data_root, "scotus/104")
    _prediction(data_root, "scotus/104", run_id="20260801T000000Z", digest=None)
    # 105: a counted grading names an older frozen run; a newer de-counted run is staged.
    _event(data_root, "scotus/105")
    _prediction(data_root, "scotus/105")
    _prediction(data_root, "scotus/105", run_id="20260920T000000Z", digest=None)
    _outcome(data_root, "scotus/105")
    _grade(data_root, "scotus/105", prediction_run_id="20260917T000000Z")
    # 106: re-owed, but its conference was already past on the registration day.
    _event(data_root, "scotus/106")
    _prediction(data_root, "scotus/106", run_id="20260801T000000Z", digest=None)
    _prediction(data_root, "scotus/106")
    # 107: de-counted cells only, on an event resolved before registration.
    _event(data_root, "scotus/107")
    _prediction(data_root, "scotus/107", run_id="20260801T000000Z", digest=None)
    _outcome(data_root, "scotus/107", resolved_at=date(2026, 9, 10))
    payloads = {case_id: RELISTED for case_id in CASES if case_id != "scotus/102"}
    payloads["scotus/106"] = PAST
    db = _corpus(tmp_path / "corpus", payloads)
    return data_root, db


def _cut(data_root: Path, db: Path, registered_at: date | None = None) -> CountedConferenceCut:
    with corpus.connect_readonly(db, backend="local") as conn:
        return counted_by_conference(
            data_root,
            conn,
            vintage=ExportCorpusVintage(backend="local", latest_pull=None, latest_snapshot=None),
            corpus_sha256="",
            registered_at=registered_at,
        )


def test_the_conference_is_read_at_the_cut_not_from_the_current_column(
    ledger: tuple[Path, Path],
) -> None:
    events = {e.case_id: e for e in _cut(*ledger).events}
    first = events["scotus/100"]
    assert first.conference == "2026-09-28"
    assert first.current_conference == date(2026, 10, 9)
    assert [c.conference_source for c in first.cells] == ["asof"]
    assert first.cells[0].bound == date(2026, 9, 18)
    assert first.reowed is True
    assert first.payload_date == date(2026, 9, 25)
    assert (first.resolved, first.resolved_at, first.actual_disposition, first.status) == (
        True,
        date(2026, 10, 5),
        "denied",
        "resolved_unscored",
    )
    assert first.registered is None


def test_cells_cut_either_side_of_a_relist_group_as_mixed(ledger: tuple[Path, Path]) -> None:
    event = {e.case_id: e for e in _cut(*ledger).events}["scotus/101"]
    assert event.conference == "mixed"
    assert [(c.predictor_id, c.conference) for c in event.cells] == [
        ("alpha", date(2026, 9, 28)),
        ("beta", date(2026, 10, 9)),
    ]
    assert event.band is None
    assert event.bands == ["baseline", "elevated"]
    assert event.predictors == ["alpha", "beta"]
    assert event.reowed is False


def test_no_payload_falls_back_to_the_current_column_and_says_so(
    ledger: tuple[Path, Path],
) -> None:
    cut = _cut(*ledger)
    event = {e.case_id: e for e in cut.events}["scotus/102"]
    assert event.conference == "2026-10-09"
    assert [c.conference_source for c in event.cells] == ["current"]
    assert cut.conference_fallbacks == 1


def test_a_counted_grading_names_the_counted_cell(ledger: tuple[Path, Path]) -> None:
    event = {e.case_id: e for e in _cut(*ledger).events}["scotus/105"]
    assert [(c.predictor_id, c.run_id) for c in event.cells] == [("alpha", "20260917T000000Z")]
    assert event.scored_predictors == ["alpha"]
    assert event.status == "scored"
    # The de-counted run postdates the counted one: not a re-forecast.
    assert event.reowed is False


def test_registration_membership_is_fixed_at_the_registration_day(
    ledger: tuple[Path, Path],
) -> None:
    cut = _cut(*ledger, registered_at=date(2026, 9, 15))
    events = {e.case_id: e for e in cut.events}
    # Rescheduled after registration: still registered, and the move is visible.
    assert events["scotus/100"].registered is True
    assert events["scotus/100"].conference_at_registration == date(2026, 9, 28)
    # Forecast first by the frozen process: not registered.
    assert events["scotus/101"].registered is False
    # Every engine failed: listed anyway, with no counted cell.
    failed = events["scotus/104"]
    assert (failed.registered, failed.predictors, failed.conference, failed.status) == (
        True,
        [],
        "none",
        "unforecast",
    )
    # Its conference was already past on the registration day.
    assert events["scotus/106"].registered is False
    assert events["scotus/106"].conference_at_registration == date(2026, 6, 18)
    # Resolved before registration, and never counted: absent.
    assert "scotus/107" not in events
    # The de-counted staged cell postdates registration: neither counted nor registered.
    assert "scotus/103" not in events
    # 102 has no payload: its registration reading falls back too.
    assert cut.conference_fallbacks == 2


def test_only_a_staged_frozen_cell_counts(ledger: tuple[Path, Path]) -> None:
    assert "scotus/103" not in {e.case_id for e in _cut(*ledger).events}


def test_totals_split_by_conference_band_and_resolution(ledger: tuple[Path, Path]) -> None:
    totals = {
        (t.conference, t.band): (t.events, t.scored, t.resolved_unscored, t.pending)
        for t in _cut(*ledger).totals
    }
    assert totals == {
        ("2026-09-28", "baseline"): (2, 1, 1, 0),
        ("2026-10-09", "baseline"): (1, 0, 0, 1),
        ("mixed", None): (1, 0, 0, 1),
        ("2026-06-18", "baseline"): (1, 0, 0, 1),
    }


def test_the_bound_is_the_cutoff_where_one_was_fixed() -> None:
    def _with(cutoff: date | None) -> Prediction:
        return Prediction(
            case_id="scotus/1",
            event_id=EVENT,
            predictor_id="alpha",
            engine=Engine.claude_code,
            run_id="r",
            created_at=datetime(2026, 9, 17, tzinfo=UTC),
            input_snapshot="corpus",
            granted=0,
            probability=0.1,
            predicted_disposition=Disposition.denied,
            context=PredictionContext(
                mode="forward",
                snapshot_date=date(2026, 9, 1),
                cutoff=cutoff,
                cut_kind="date" if cutoff else None,
                signals_observable=True,
            ),
        )

    assert cell_bound(_with(date(2026, 8, 15))) == date(2026, 8, 15)
    assert cell_bound(_with(None)) == date(2026, 9, 2)


def test_cli_prints_the_cut_on_stdout_and_the_totals_on_stderr(
    ledger: tuple[Path, Path],
) -> None:
    data_root, db = ledger
    result = runner.invoke(
        app,
        ["conference-set", "--counted", "--registered-at", "2026-09-15"],
        env={
            "FEDCOURTS_DATA_ROOT": str(data_root),
            "FEDCOURTS_CORPUS_ROOT": str(db.parent),
            "FEDCOURTS_CORPUS_BACKEND": "local",
        },
    )
    assert result.exit_code == 0, result.output
    cut = CountedConferenceCut.model_validate(json.loads(result.stdout))
    assert cut.corpus.backend == "local"
    assert cut.corpus_sha256
    assert cut.registered_at == date(2026, 9, 15)
    assert {e.case_id for e in cut.events} == set(CASES) - {"scotus/103", "scotus/107"}
    assert (
        "registered, conference 2026-09-28: 1 event(s) — 0 scored, 1 resolved unscored, "
        "0 pending, 0 unforecast" in result.stderr
    )
    assert "registered as at 2026-09-15" in result.stderr
    assert "2 conference reading(s) fell back" in result.stderr


def test_registered_at_needs_counted(ledger: tuple[Path, Path]) -> None:
    result = runner.invoke(app, ["conference-set", "--registered-at", "2026-09-15"])
    assert result.exit_code == 2


def test_a_malformed_registration_day_is_refused(ledger: tuple[Path, Path]) -> None:
    result = runner.invoke(app, ["conference-set", "--counted", "--registered-at", "9/15"])
    assert result.exit_code == 2


_W1, _W2 = "sha256:window-one", "sha256:window-two"
_OPENS = datetime(2026, 9, 16, tzinfo=UTC)
_SUCCESSOR = datetime(2026, 9, 25, tzinfo=UTC)


def _two_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, revoked_at: datetime | None
) -> tuple[Path, Path]:
    """One predictor holding a cell in each of two windows on one event.

    The earlier cell is stamped in the first window, the later one in its
    successor; ``revoked_at`` revokes the first window.
    """
    monkeypatch.delenv("FEDCOURTS_CORPUS_SPLIT", raising=False)
    set_windows(
        monkeypatch,
        CountingWindow(
            label="proc-a", digest=_W1, opens=_OPENS, closes=_SUCCESSOR, revoked_at=revoked_at
        ),
        CountingWindow(label="proc-b", digest=_W2, opens=_SUCCESSOR),
    )
    data_root = tmp_path / "data"
    _event(data_root, "scotus/100")
    _prediction(data_root, "scotus/100", run_id="20260917T000000Z", digest=_W1)
    _prediction(data_root, "scotus/100", run_id="20260926T000000Z", digest=_W2)
    return data_root, _corpus(tmp_path / "corpus", {"scotus/100": RELISTED})


def test_a_closed_windows_cell_is_the_counted_one_not_its_successors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cut = _cut(*_two_windows(tmp_path, monkeypatch, revoked_at=None), date(2026, 9, 30))
    (event,) = cut.events
    # The earliest window's cell counts; the successor's is never staged in its place.
    assert [(c.run_id, c.process_digest) for c in event.cells] == [("20260917T000000Z", _W1)]
    # A later window's cell behind a counted one is a duplicate, not a de-count:
    # the event is neither a re-forecast nor re-owed.
    assert (event.reowed, event.registered) == (False, False)


def test_a_revoked_windows_cell_is_de_counted_and_its_successor_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revoked = datetime(2026, 9, 25, 12, tzinfo=UTC)
    cut = _cut(*_two_windows(tmp_path, monkeypatch, revoked_at=revoked))
    (event,) = cut.events
    # The successor's cell, stamped after the revocation, is the counted one,
    # and the revoked window's earlier cell makes it a re-forecast.
    assert [(c.run_id, c.process_digest) for c in event.cells] == [("20260926T000000Z", _W2)]
    assert event.reowed is True


def test_a_cell_stamped_before_its_predecessors_revocation_counts_nowhere(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A successor's cell stamped before the earlier window's revocation, with no
    fresh forecast after it: no counted cell, so the event is listed only as a
    registered one, through the revoked window's de-counted cell."""
    ledger = _two_windows(tmp_path, monkeypatch, revoked_at=datetime(2026, 9, 28, tzinfo=UTC))
    assert _cut(*ledger).events == []
    (event,) = _cut(*ledger, registered_at=date(2026, 9, 20)).events
    assert (event.registered, event.predictors, event.status) == (True, [], "unforecast")
