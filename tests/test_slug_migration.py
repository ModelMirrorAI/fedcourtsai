"""Entry-pinned slug convergence: detection, both halves of the rename, guards, idempotency."""

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
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent
from fedcourtsai.serialize import read_model, write_json, write_yaml
from fedcourtsai.slug_migration import converge_event_slugs

runner = CliRunner()

_CASE = "scotus/900001"
# The subject the six-word cap truncates mid-phrase: the stale id keeps the
# dangling conjunction, today's derivation trims it.
_ENTRY_TEXT = "MOTION for leave to file amicus brief and appendix out of time"
_STALE_ID = "evt-motion-leave-to-file-amicus-brief-and"
_DERIVED_ID = "evt-motion-leave-to-file-amicus-brief"


def _row(case_id: str = _CASE) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {"case_id": case_id, "court": "scotus", "docket_number": "24A1099"}
    )


def _event(event_id: str, **kw: object) -> corpus.CorpusEvent:
    base: dict[str, object] = {
        "event_id": event_id,
        "case_id": _CASE,
        "court": "scotus",
        "kind": EventKind.motion,
        "stage": "interim",
        "title": "Applicant v. Respondent",
        "description": _ENTRY_TEXT,
        "docket_entry_id": 4,
        "opened_at": date(2024, 8, 1),
        "resolved": True,
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


@contextmanager
def _seeded(tmp_path: Path, *events: corpus.CorpusEvent) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, list(events) or [_event(_STALE_ID)])
        yield conn


def _data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


def _paths(data_root: Path, event_id: str) -> EventPaths:
    return CasePaths(data_root, "scotus", 900001).event(event_id)


def _commit_ledger(data_root: Path, event_id: str) -> EventPaths:
    """The committed ledger side of an event: its definition and its outcome."""
    paths = _paths(data_root, event_id)
    paths.base.mkdir(parents=True)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=_CASE,
            kind=EventKind.motion,
            title="Applicant v. Respondent",
            description=_ENTRY_TEXT,
            docket_entry_id=4,
            resolved=True,
        ),
    )
    write_json(
        paths.outcome,
        Outcome(
            case_id=_CASE,
            event_id=event_id,
            resolved_at=date(2024, 9, 1),
            actual_disposition=Disposition.granted,
            actual_granted=1,
        ),
    )
    return paths


def test_apply_renames_both_halves(tmp_path: Path) -> None:
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    with _seeded(tmp_path) as conn:
        result = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.applied is True
    assert result.renamed == [(f"{_CASE}/{_STALE_ID}", _DERIVED_ID)]
    assert result.skipped == []
    # The corpus row moved, carrying every field and the resolved latch.
    assert event.event_id == _DERIVED_ID
    assert event.docket_entry_id == 4
    assert event.description == _ENTRY_TEXT
    assert event.stage == "interim"
    assert event.resolved is True
    # The ledger directory moved with it, and both documents name the new id.
    assert not _paths(data_root, _STALE_ID).base.exists()
    moved = _paths(data_root, _DERIVED_ID)
    assert read_model(moved.event_file, PredictableEvent).event_id == _DERIVED_ID
    assert read_model(moved.outcome, Outcome).event_id == _DERIVED_ID
    assert read_model(moved.outcome, Outcome).actual_granted == 1


def test_dry_run_reports_and_touches_nothing(tmp_path: Path) -> None:
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    with _seeded(tmp_path) as conn:
        result = converge_event_slugs(conn, data_root, apply=False)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.applied is False
    assert result.renamed == [(f"{_CASE}/{_STALE_ID}", _DERIVED_ID)]
    assert event.event_id == _STALE_ID
    assert _paths(data_root, _STALE_ID).base.is_dir()
    assert not _paths(data_root, _DERIVED_ID).base.exists()


def test_second_run_is_a_noop(tmp_path: Path) -> None:
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    with _seeded(tmp_path) as conn:
        first = converge_event_slugs(conn, data_root, apply=True)
        second = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert len(first.renamed) == 1
    assert second.renamed == []
    assert second.already_converged == 1
    assert second.skipped == []
    assert event.event_id == _DERIVED_ID


def test_existing_target_directory_refuses_the_rename(tmp_path: Path) -> None:
    # Directories under both ids: merging them is a judgement call, so the row
    # is reported for triage and neither store moves.
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    _paths(data_root, _DERIVED_ID).base.mkdir(parents=True)
    with _seeded(tmp_path) as conn:
        result = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    ((ref, reason),) = result.skipped
    assert ref == f"{_CASE}/{_STALE_ID}"
    assert "both" in reason
    assert event.event_id == _STALE_ID
    assert _paths(data_root, _STALE_ID).base.is_dir()


def test_reingest_duplicate_is_folded_not_reported(tmp_path: Path) -> None:
    # The dominant shape: a daily refresh already inserted the open duplicate
    # under the derived id, pinned to the same docket entry. That row *is* what
    # the sweep exists to clear, so the rename folds onto it — one row, the
    # resolved latch carried by rename_event's MAX, the ledger directory moved.
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    duplicate = _event(_DERIVED_ID, resolved=False)
    with _seeded(tmp_path, _event(_STALE_ID), duplicate) as conn:
        result = converge_event_slugs(conn, data_root, apply=True)
        events = corpus.events_for_case(conn, _CASE)
    assert result.renamed == [(f"{_CASE}/{_STALE_ID}", _DERIVED_ID)]
    assert result.skipped == []
    (event,) = events
    assert event.event_id == _DERIVED_ID
    assert event.resolved is True  # the stale row's latch survives the fold
    assert event.docket_entry_id == 4
    assert not _paths(data_root, _STALE_ID).base.exists()
    assert read_model(_paths(data_root, _DERIVED_ID).event_file, PredictableEvent).event_id == (
        _DERIVED_ID
    )


def test_a_different_entry_holding_the_derived_id_is_reported(tmp_path: Path) -> None:
    # The genuine collision: two *filings* whose subjects now derive one id.
    # Folding would write one filing's latch and entry pin onto another, so the
    # pair needs the uniqueness suffix re-assigned — a maintainer's call.
    other_filing = _event(_DERIVED_ID, docket_entry_id=9, resolved=False)
    with _seeded(tmp_path, _event(_STALE_ID), other_filing) as conn:
        result = converge_event_slugs(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    ((ref, reason),) = result.skipped
    assert ref == f"{_CASE}/{_STALE_ID}"
    assert "different docket entry" in reason
    # Both rows survive untouched for triage.
    assert [(e.event_id, e.docket_entry_id) for e in events] == [(_DERIVED_ID, 9), (_STALE_ID, 4)]


def test_committed_cell_output_refuses_the_rename(tmp_path: Path) -> None:
    # A prediction names the event id inside its own files, which this sweep
    # does not rewrite.
    data_root = _data_root(tmp_path)
    paths = _commit_ledger(data_root, _STALE_ID)
    paths.prediction_dir("p1", "20260101T000000Z").mkdir(parents=True)
    with _seeded(tmp_path) as conn:
        result = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    ((_, reason),) = result.skipped
    assert "predictions" in reason
    assert event.event_id == _STALE_ID


def test_collision_suffix_reads_as_converged(tmp_path: Path) -> None:
    # The within-case uniqueness suffix is not part of the derivation: the
    # second of two entries deriving one id carries its entry number, and that
    # is the converged form, not a stale one.
    suffixed = f"{_DERIVED_ID}-54"
    with _seeded(tmp_path, _event(suffixed)) as conn:
        result = converge_event_slugs(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    assert result.already_converged == 1
    assert event.event_id == suffixed


def test_interrupted_move_finishes_the_restamp_and_the_row(tmp_path: Path) -> None:
    # The ledger half leads and is itself two steps. A run that died between
    # them leaves the directory already at the target with its documents still
    # naming the old id — a shape validate's path/declaration check fails. The
    # next run must finish *both* the restamp and the corpus row, so the
    # rewrite cannot hang off the source directory still existing.
    data_root = _data_root(tmp_path)
    stranded = _commit_ledger(data_root, _STALE_ID)
    stranded.base.rename(_paths(data_root, _DERIVED_ID).base)
    with _seeded(tmp_path) as conn:
        result = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == [(f"{_CASE}/{_STALE_ID}", _DERIVED_ID)]
    assert event.event_id == _DERIVED_ID
    moved = _paths(data_root, _DERIVED_ID)
    assert read_model(moved.event_file, PredictableEvent).event_id == _DERIVED_ID
    assert read_model(moved.outcome, Outcome).event_id == _DERIVED_ID


def test_case_level_rows_are_never_scanned(tmp_path: Path) -> None:
    # Only entry-pinned rows carry a derived slug; a case-level baseline's id
    # comes from `default_event`, so it is outside this sweep entirely.
    baseline = _event("evt-motion-disposition", docket_entry_id=None, description=None)
    with _seeded(tmp_path, baseline) as conn:
        result = converge_event_slugs(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    assert result.skipped == []
    assert result.already_converged == 0
    assert event.event_id == "evt-motion-disposition"


def test_row_without_entry_text_is_reported(tmp_path: Path) -> None:
    with _seeded(tmp_path, _event(_STALE_ID, description=None)) as conn:
        result = converge_event_slugs(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == []
    ((_, reason),) = result.skipped
    assert "no entry text" in reason
    assert event.event_id == _STALE_ID


def test_unreadable_kind_is_reported_without_aborting_the_pass(tmp_path: Path) -> None:
    # One row outside the event vocabulary must not abort a pass that has
    # already written: it is reported and the sweep carries on.
    other_case = "scotus/900002"
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    with _seeded(tmp_path) as conn:
        corpus.upsert_rows(conn, [_row(other_case)])
        corpus.upsert_events(conn, [_event(_STALE_ID, case_id=other_case)])
        conn.execute("UPDATE events SET kind = 'sanction' WHERE case_id = ?", (other_case,))
        result = converge_event_slugs(conn, data_root, apply=True)
        (event,) = corpus.events_for_case(conn, _CASE)
    assert result.renamed == [(f"{_CASE}/{_STALE_ID}", _DERIVED_ID)]
    ((ref, reason),) = result.skipped
    assert ref == f"{other_case}/{_STALE_ID}"
    assert "vocabulary" in reason
    assert event.event_id == _DERIVED_ID


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    data_root = _data_root(tmp_path)
    _commit_ledger(data_root, _STALE_ID)
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, [_event(_STALE_ID)])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))

    result = runner.invoke(app, ["converge-event-slugs"])
    assert result.exit_code == 0, result.output
    assert "dry-run" in result.output
    assert f"{_STALE_ID} -> {_DERIVED_ID}" in result.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _CASE)
        assert event.event_id == _STALE_ID

    applied = runner.invoke(app, ["converge-event-slugs", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _CASE)
        assert event.event_id == _DERIVED_ID


def test_cli_refuses_above_the_blast_radius_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, [_event(_STALE_ID)])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))

    result = runner.invoke(app, ["converge-event-slugs", "--apply", "--max-renames", "0"])
    assert result.exit_code == 1
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _CASE)
        assert event.event_id == _STALE_ID


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["converge-event-slugs"])
    assert result.exit_code == 1
