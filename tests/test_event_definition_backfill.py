"""The event-definition back-fill: committed event.yaml against the corpus event row."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.event_definition_backfill import backfill_event_definitions
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import EventKind, Moment, PredictableEvent, Stage
from fedcourtsai.serialize import read_model, write_yaml

runner = CliRunner()

_BASELINE = "evt-petition-disposition"
_ARRIVAL = "evt-motion-disposition"
_DOCKETED = date(2025, 11, 25)
_SUBMITTED = date(2025, 11, 18)


def _row(
    docket: int,
    event_id: str,
    *,
    kind: EventKind = EventKind.petition,
    stage: Stage | None = Stage.cert,
    moment: Moment | None = Moment.distribution,
    opened_at: date | None = date(2025, 10, 1),
    resolved: bool = True,
) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id=f"scotus/{docket}",
        court="scotus",
        kind=kind,
        stage=stage,
        moment=moment,
        title="A v. B",
        opened_at=opened_at,
        resolved=resolved,
    )


def _commit(data_root: Path, row: corpus.CorpusEvent, **fields: object) -> Path:
    """Commit a definition that agrees with ``row`` except where ``fields`` say."""
    docket = int(row.case_id.partition("/")[2])
    path = CasePaths(data_root, "scotus", docket).event(row.event_id).event_file
    definition = PredictableEvent.model_validate(
        {
            "event_id": row.event_id,
            "case_id": row.case_id,
            "kind": row.kind,
            "stage": row.stage,
            "moment": row.moment,
            "title": row.title,
            "opened_at": row.opened_at,
            "resolved": row.resolved,
            **fields,
        }
    )
    write_yaml(path, definition)
    return path


def _evaluate(data_root: Path, docket: int, event_id: str) -> None:
    """Leave a committed evaluation directory under one event of the case."""
    paths = CasePaths(data_root, "scotus", docket).event(event_id)
    (paths.evaluations_dir / "claude-judge" / "20260101T000000Z").mkdir(parents=True)


@contextmanager
def _corpus(tmp_path: Path, rows: list[corpus.CorpusEvent]) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow.model_validate({"case_id": case_id, "court": "scotus"})
                for case_id in sorted({row.case_id for row in rows})
            ],
        )
        corpus.upsert_events(conn, rows)
        yield conn


def test_fills_a_pre_moment_petition_baseline(tmp_path: Path) -> None:
    data = tmp_path / "data"
    row = _row(1, _BASELINE)
    path = _commit(data, row, stage=None, moment=None)
    before = path.read_text()
    original = read_model(path, PredictableEvent)
    with _corpus(tmp_path, [row]) as conn:
        dry = backfill_event_definitions(conn, data)
        assert path.read_text() == before, "a dry run writes nothing"
        assert [r.fields for r in dry.rewrites] == [("stage", "moment")]
        assert dry.fill_populations() == {("petition", "cert", "distribution", "resolved"): 1}
        applied = backfill_event_definitions(conn, data, apply=True, max_rewrites=1)
    assert applied.applied
    written = read_model(path, PredictableEvent)
    assert (written.stage, written.moment) == (Stage.cert, Moment.distribution)
    # Nothing but the filled fields moved.
    assert written.model_dump(exclude={"stage", "moment"}) == original.model_dump(
        exclude={"stage", "moment"}
    )
    with _corpus(tmp_path, [row]) as conn:
        assert backfill_event_definitions(conn, data).rewrites == [], "idempotent"


def test_neutral_fill_on_a_scored_case_still_moves(tmp_path: Path) -> None:
    """A petition baseline already reads as cert@distribution, so no figure moves."""
    data = tmp_path / "data"
    row = _row(2, _BASELINE)
    _commit(data, row, stage=None, moment=None)
    _evaluate(data, 2, _BASELINE)
    with _corpus(tmp_path, [row]) as conn:
        result = backfill_event_definitions(conn, data)
    assert [r.fields for r in result.rewrites] == [("stage", "moment")]
    assert result.held == []


def test_fill_that_rekeys_a_scored_cell_is_held(tmp_path: Path) -> None:
    """A motion-kind event with no stage reads as no stage; filling interim re-keys it."""
    data = tmp_path / "data"
    row = _row(3, _ARRIVAL, kind=EventKind.motion, stage=Stage.interim, moment=Moment.arrival)
    _commit(data, row, stage=None, moment=None)
    _evaluate(data, 3, _ARRIVAL)
    with _corpus(tmp_path, [row]) as conn:
        result = backfill_event_definitions(conn, data)
    assert result.rewrites == []
    assert {(h.change.name, h.reason) for h in result.held} == {
        ("stage", "re-keys-scored"),
        ("moment", "re-keys-scored"),
    }


def test_recorded_stage_or_moment_is_never_overwritten(tmp_path: Path) -> None:
    data = tmp_path / "data"
    row = _row(4, _BASELINE)
    path = _commit(data, row, moment=Moment.arrival)
    before = path.read_text()
    with _corpus(tmp_path, [row]) as conn:
        result = backfill_event_definitions(conn, data, apply=True, max_rewrites=5)
    assert result.rewrites == []
    assert [(h.change.name, h.reason) for h in result.held] == [("moment", "conflict")]
    assert path.read_text() == before


def test_corpus_null_never_erases(tmp_path: Path) -> None:
    data = tmp_path / "data"
    row = _row(5, _BASELINE, stage=None, moment=None, opened_at=None)
    _commit(data, row, stage=Stage.cert, moment=Moment.distribution, opened_at=date(2025, 1, 2))
    with _corpus(tmp_path, [row]) as conn:
        result = backfill_event_definitions(conn, data)
    assert result.rewrites == []
    assert {h.reason for h in result.held} == {"corpus-null"}
    assert len(result.held) == 3


def test_opened_at_moves_on_a_resolved_unscored_event(tmp_path: Path) -> None:
    data = tmp_path / "data"
    row = _row(
        6,
        _ARRIVAL,
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        opened_at=_SUBMITTED,
    )
    path = _commit(data, row, opened_at=_DOCKETED)
    with _corpus(tmp_path, [row]) as conn:
        result = backfill_event_definitions(conn, data, apply=True, max_rewrites=1)
    assert [r.fields for r in result.rewrites] == [("opened_at",)]
    assert read_model(path, PredictableEvent).opened_at == _SUBMITTED


@pytest.mark.parametrize(
    ("resolved", "scored", "reason"),
    [(False, False, "open-event"), (True, True, "scored-case")],
)
def test_opened_at_is_held_on_open_or_scored_events(
    tmp_path: Path, resolved: bool, scored: bool, reason: str
) -> None:
    data = tmp_path / "data"
    row = _row(
        7,
        _ARRIVAL,
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        opened_at=_SUBMITTED,
        resolved=resolved,
    )
    path = _commit(data, row, opened_at=_DOCKETED)
    # The scored-case rule is case-wide: the set-aside reads one event's
    # opened_at for another event's cells.
    sibling = _row(7, _BASELINE, resolved=True)
    _commit(data, sibling)
    if scored:
        _evaluate(data, 7, _BASELINE)
    before = path.read_text()
    with _corpus(tmp_path, [row, sibling]) as conn:
        result = backfill_event_definitions(conn, data, apply=True, max_rewrites=5)
    assert result.rewrites == []
    assert [(h.change.name, h.reason) for h in result.held] == [("opened_at", reason)]
    assert path.read_text() == before


def test_apply_refuses_above_the_bound_and_writes_nothing(tmp_path: Path) -> None:
    data = tmp_path / "data"
    rows = [_row(10, _BASELINE), _row(11, _BASELINE)]
    paths = [_commit(data, row, stage=None, moment=None) for row in rows]
    before = [p.read_text() for p in paths]
    with _corpus(tmp_path, rows) as conn:
        result = backfill_event_definitions(conn, data, apply=True, max_rewrites=1)
    assert result.refused and not result.applied
    assert [p.read_text() for p in paths] == before


def test_apply_without_a_bound_raises(tmp_path: Path) -> None:
    with _corpus(tmp_path, [_row(12, _BASELINE)]) as conn, pytest.raises(ValueError):
        backfill_event_definitions(conn, tmp_path / "data", apply=True)


def test_definition_without_a_corpus_row_is_reported(tmp_path: Path) -> None:
    data = tmp_path / "data"
    _commit(data, _row(13, _BASELINE), stage=None, moment=None)
    with _corpus(tmp_path, [_row(14, _BASELINE)]) as conn:
        result = backfill_event_definitions(conn, data)
    assert result.no_corpus_row == [f"scotus/13 {_BASELINE}"]
    assert result.rewrites == []


def _cli_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")


def test_cli_ledger_dry_run_then_bounded_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _cli_env(tmp_path, monkeypatch)
    data = tmp_path / "data"
    rows = [
        _row(20, _BASELINE),
        _row(
            21,
            _ARRIVAL,
            kind=EventKind.motion,
            stage=Stage.interim,
            moment=Moment.arrival,
            opened_at=_SUBMITTED,
        ),
    ]
    first = _commit(data, rows[0], stage=None, moment=None)
    _commit(data, rows[1], opened_at=_DOCKETED)
    with _corpus(tmp_path, rows):
        pass
    before = first.read_text()
    dry = runner.invoke(app, ["backfill-event-definitions"])
    assert dry.exit_code == 0, dry.output
    assert "would rewrite 2 file(s): 1 stage fill(s), 1 moment fill(s), 1 opened_at" in dry.stdout
    assert "fill shape kind=petition stage=cert moment=distribution [resolved]: 1" in dry.stdout
    assert f"would rewrite scotus/21 {_ARRIVAL}: opened_at 2025-11-25 -> 2025-11-18" in dry.stdout
    # The per-file list is on stderr, so a workflow can keep it out of a summary.
    assert f"would rewrite scotus/20 {_BASELINE}: stage null -> cert" in dry.stderr
    assert first.read_text() == before

    unbounded = runner.invoke(app, ["backfill-event-definitions", "--apply"])
    assert unbounded.exit_code == 2
    refused = runner.invoke(app, ["backfill-event-definitions", "--apply", "--max-rewrites", "1"])
    assert refused.exit_code == 1
    assert "refusing to rewrite 2" in refused.stderr
    assert first.read_text() == before

    applied = runner.invoke(app, ["backfill-event-definitions", "--apply", "--max-rewrites", "2"])
    assert applied.exit_code == 0, applied.output
    assert "rewrote 2 file(s)" in applied.stdout
    again = runner.invoke(app, ["backfill-event-definitions"])
    assert "would rewrite 0 file(s)" in again.stdout


def test_cli_refuses_a_missing_local_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _cli_env(tmp_path, monkeypatch)
    result = runner.invoke(app, ["backfill-event-definitions"])
    assert result.exit_code == 1
    assert "corpus database is missing" in result.stderr
