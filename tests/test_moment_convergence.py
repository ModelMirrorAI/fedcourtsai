"""The declared-moment convergence: detection in both stores, guards, the bound, the CLI."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.application_migration import MOTION_BASELINE_EVENT_ID
from fedcourtsai.cli import app
from fedcourtsai.moment_convergence import converge_event_moments
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import EventKind, Moment, PredictableEvent
from fedcourtsai.serialize import read_model, write_yaml

runner = CliRunner()

_STALE = "scotus/9526000209"
_CLEAN = "scotus/9526000210"


def _motion_baseline(case_id: str, moment: Moment | None, **kw: object) -> corpus.CorpusEvent:
    base: dict[str, object] = {
        "event_id": MOTION_BASELINE_EVENT_ID,
        "case_id": case_id,
        "court": "scotus",
        "kind": EventKind.motion,
        "stage": "interim",
        "moment": moment,
        "title": "Applicant v. Florida",
        "decision_target": "disposition",
        "opened_at": date(2026, 8, 14),
        "resolved": True,
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


def _event_file(data_root: Path, case_id: str) -> Path:
    court, _, docket = case_id.partition("/")
    return CasePaths(data_root, court, int(docket)).event(MOTION_BASELINE_EVENT_ID).event_file


def _write_ledger(data_root: Path, event: corpus.CorpusEvent) -> Path:
    path = _event_file(data_root, event.case_id)
    write_yaml(
        path,
        PredictableEvent(
            event_id=event.event_id,
            case_id=event.case_id,
            kind=event.kind,
            stage=event.stage,
            moment=event.moment,
            title=event.title or event.case_id,
            decision_target=event.decision_target,
            opened_at=event.opened_at,
            resolved=event.resolved,
        ),
    )
    return path


def _moment_of(conn: sqlite3.Connection, case_id: str) -> str | None:
    (event,) = corpus.events_for_case(conn, case_id)
    return None if event.moment is None else str(event.moment)


@contextmanager
def _seeded(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """A relabelled application carrying the cert `distribution` moment, beside a clean one."""
    stale = _motion_baseline(_STALE, Moment.distribution)
    clean = _motion_baseline(_CLEAN, Moment.arrival)
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(conn, [stale, clean])
        _write_ledger(tmp_path / "data", stale)
        _write_ledger(tmp_path / "data", clean)
        yield conn


def test_dry_run_finds_both_stores_and_writes_nothing(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with _seeded(tmp_path) as conn:
        result = converge_event_moments(conn, data_root, apply=False)
        assert _moment_of(conn, _STALE) == "distribution"
    assert result.applied is False
    assert [(r.case_id, r.was, r.now) for r in result.corpus_rows] == [
        (_STALE, "distribution", Moment.arrival)
    ]
    assert [(r.case_id, r.was) for r in result.ledger_files] == [(_STALE, "distribution")]
    assert result.skipped == []
    ledger = read_model(_event_file(data_root, _STALE), PredictableEvent)
    assert ledger.moment == Moment.distribution


def test_apply_restamps_both_stores_and_only_the_moment(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    before = _event_file(data_root, _STALE)
    with _seeded(tmp_path) as conn:
        original = read_model(before, PredictableEvent)
        result = converge_event_moments(conn, data_root, apply=True, max_rewrites=2)
        assert result.applied is True
        assert _moment_of(conn, _STALE) == "arrival"
        assert _moment_of(conn, _CLEAN) == "arrival"
        (event,) = corpus.events_for_case(conn, _STALE)
    assert event.resolved is True
    assert event.opened_at == date(2026, 8, 14)
    rewritten = read_model(before, PredictableEvent)
    assert rewritten.moment == Moment.arrival
    assert rewritten.model_dump(exclude={"moment"}) == original.model_dump(exclude={"moment"})


def test_second_run_is_a_noop(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with _seeded(tmp_path) as conn:
        converge_event_moments(conn, data_root, apply=True, max_rewrites=2)
        second = converge_event_moments(conn, data_root, apply=True, max_rewrites=0)
    assert second.total == 0
    assert second.refused is False


def test_ledger_file_is_found_when_its_corpus_row_already_converged(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(conn, [_motion_baseline(_STALE, Moment.arrival)])
        _write_ledger(data_root, _motion_baseline(_STALE, Moment.distribution))
        result = converge_event_moments(conn, data_root, apply=True, max_rewrites=1)
    assert result.corpus_rows == []
    assert [r.case_id for r in result.ledger_files] == [_STALE]
    assert read_model(_event_file(data_root, _STALE), PredictableEvent).moment == Moment.arrival


def test_a_scored_event_is_held_back_in_both_stores(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with _seeded(tmp_path) as conn:
        (_event_file(data_root, _STALE).parent / "predictions" / "p" / "r").mkdir(parents=True)
        result = converge_event_moments(conn, data_root, apply=True, max_rewrites=2)
        assert _moment_of(conn, _STALE) == "distribution"
    assert result.total == 0
    assert [ref for ref, _ in result.skipped] == [
        f"{_STALE}/{MOTION_BASELINE_EVENT_ID}",
        f"{_STALE}/{MOTION_BASELINE_EVENT_ID} (ledger)",
    ]
    assert all("scored cells" in reason for _, reason in result.skipped)
    assert read_model(_event_file(data_root, _STALE), PredictableEvent).moment == (
        Moment.distribution
    )


def test_entry_pinned_and_null_moment_rows_are_not_restamped(tmp_path: Path) -> None:
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_events(
            conn,
            [
                _motion_baseline(_STALE, Moment.distribution, docket_entry_id=7),
                _motion_baseline(_CLEAN, None),
            ],
        )
        result = converge_event_moments(conn, tmp_path / "data", apply=True, max_rewrites=5)
        assert _moment_of(conn, _STALE) == "distribution"
        assert _moment_of(conn, _CLEAN) is None
    assert result.total == 0
    ((ref, reason),) = result.skipped
    assert ref == f"{_STALE}/{MOTION_BASELINE_EVENT_ID}"
    assert "entry-pinned" in reason


def test_apply_over_the_bound_refuses_and_writes_nothing(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with _seeded(tmp_path) as conn:
        result = converge_event_moments(conn, data_root, apply=True, max_rewrites=1)
        assert _moment_of(conn, _STALE) == "distribution"
    assert result.refused is True
    assert result.applied is False
    assert read_model(_event_file(data_root, _STALE), PredictableEvent).moment == (
        Moment.distribution
    )


def test_cli_dry_run_then_bounded_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _seeded(tmp_path):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))

    dry = runner.invoke(app, ["converge-event-moments"])
    assert dry.exit_code == 0, dry.output
    assert "would re-stamp 1 corpus row(s) and 1 ledger event.yaml file(s)" in dry.output
    assert f"corpus {_STALE}/{MOTION_BASELINE_EVENT_ID}: distribution -> arrival" in dry.output

    unbounded = runner.invoke(app, ["converge-event-moments", "--apply"])
    assert unbounded.exit_code == 2

    applied = runner.invoke(app, ["converge-event-moments", "--apply", "--max-rewrites", "2"])
    assert applied.exit_code == 0, applied.output
    assert "re-stamped 1 corpus row(s)" in applied.output
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert _moment_of(conn, _STALE) == "arrival"


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["converge-event-moments"])
    assert result.exit_code == 1
