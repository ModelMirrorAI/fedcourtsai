"""The copied-outcome repair: detection, the reopen, guards, convergence, idempotency."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.attribution_migration import reopen_misattributed_outcomes
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.ingest import from_api_docket
from fedcourtsai.pipeline.outcome import resolve_case
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent, Stage
from fedcourtsai.serialize import read_model, write_json, write_yaml

runner = CliRunner()

_CASE = "scotus/900001"
_DOCKET = 900001
_BASELINE = "evt-petition-disposition"
_MOTION = "evt-motion-construe-the-application"
_APPEAL = "evt-appeal-disposition"

# The disposition the copy reproduces from its sibling baseline.
_DISPOSITION = Disposition.granted
_RESOLVED_AT = date(2018, 6, 25)


def _write_event(
    data_root: Path,
    event_id: str,
    kind: EventKind,
    *,
    opened_at: date,
    resolved_at: date | None,
    disposition: Disposition = _DISPOSITION,
) -> EventPaths:
    """One committed event, with an outcome when ``resolved_at`` is given."""
    paths = CasePaths(data_root, "scotus", _DOCKET).event(event_id)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=_CASE,
            kind=kind,
            title="Petitioner v. Respondent",
            opened_at=opened_at,
            resolved=resolved_at is not None,
        ),
    )
    if resolved_at is not None:
        write_json(
            paths.outcome,
            Outcome(
                case_id=_CASE,
                event_id=event_id,
                resolved_at=resolved_at,
                actual_disposition=disposition,
                actual_granted=1 if disposition is _DISPOSITION else 0,
            ),
        )
    return paths


def _event_row(
    event_id: str, kind: EventKind, *, resolved: bool, stage: Stage | None = None
) -> corpus.CorpusEvent:
    return corpus.CorpusEvent.model_validate(
        {
            "event_id": event_id,
            "case_id": _CASE,
            "court": "scotus",
            "kind": kind,
            "stage": stage,
            "title": "Petitioner v. Respondent",
            "decision_target": "disposition",
            "resolved": resolved,
        }
    )


@contextmanager
def _seeded(
    tmp_path: Path, events: list[corpus.CorpusEvent], **row_fields: object
) -> Iterator[sqlite3.Connection]:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow.model_validate({"case_id": _CASE, "court": "scotus", **row_fields})],
        )
        corpus.upsert_events(conn, events)
        yield conn


def _data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


def _seed_copied_motion(tmp_path: Path) -> tuple[EventPaths, EventPaths]:
    """The stay-motion shape: a non-baseline event holding a copy of the baseline's outcome."""
    root = _data_root(tmp_path)
    baseline = _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2018, 3, 14), resolved_at=_RESOLVED_AT
    )
    motion = _write_event(
        root, _MOTION, EventKind.motion, opened_at=date(2018, 1, 23), resolved_at=_RESOLVED_AT
    )
    return baseline, motion


def _copied_motion_rows() -> list[corpus.CorpusEvent]:
    return [
        _event_row(_BASELINE, EventKind.petition, resolved=True),
        _event_row(_MOTION, EventKind.motion, resolved=True),
    ]


def test_dry_run_finds_the_copy_and_writes_nothing(tmp_path: Path) -> None:
    _, motion = _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        result = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=False)
        assert result.applied is False
        assert result.reopened == [f"{_CASE}/{_MOTION}"]
        assert result.skipped == []
        assert all(e.resolved for e in corpus.events_for_case(conn, _CASE))
    assert motion.outcome.is_file()


def test_apply_deletes_the_outcome_and_reopens_both_stores(tmp_path: Path) -> None:
    baseline, motion = _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        result = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
        assert result.applied is True
        assert result.reopened == [f"{_CASE}/{_MOTION}"]
        rows = {e.event_id: e.resolved for e in corpus.events_for_case(conn, _CASE)}
    assert motion.outcome.exists() is False
    assert rows == {_BASELINE: True, _MOTION: False}
    assert read_model(motion.event_file, PredictableEvent).resolved is False
    # The true baseline keeps its outcome and stays closed.
    assert baseline.outcome.is_file()


def test_the_repair_converges_against_the_resolution_pass(tmp_path: Path) -> None:
    """The pipeline must not rewrite what the repair deleted.

    The claim the module docstring makes is about the *pipeline*, not about the
    migration repeating itself: a reopened non-baseline event is no longer any
    attribution target, so the next resolution pass leaves it alone.
    """
    _, motion = _seed_copied_motion(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with _seeded(tmp_path, _copied_motion_rows(), disposition=_DISPOSITION.value) as conn:
        reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    # `resolve_case` takes the ingest-stage row, a distinct seam from the stored one.
    row = from_api_docket(
        {
            "id": _DOCKET,
            "court_id": "scotus",
            "docket_number": "17-1295",
            "date_cert_granted": _RESOLVED_AT.isoformat(),
        }
    )
    resolution = resolve_case(db, _data_root(tmp_path), row, "scotus", _DOCKET)
    assert _MOTION not in resolution.outcomes
    assert motion.outcome.exists() is False
    # The baseline already carries the case-level disposition, so the pass is a
    # no-op rather than a re-attribution — quiet, and nothing to triage.
    assert not resolution.unrecorded


def test_a_decided_docket_surfaces_the_reopened_event_for_triage(tmp_path: Path) -> None:
    """Where the row carries a decided date, the open event is reported, not rewritten."""
    _, motion = _seed_copied_motion(tmp_path)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    row = from_api_docket(
        {
            "id": _DOCKET,
            "court_id": "scotus",
            "docket_number": "17-1295",
            "date_terminated": _RESOLVED_AT.isoformat(),
            "disposition": "Petition denied",
        }
    )
    resolution = resolve_case(db, _data_root(tmp_path), row, "scotus", _DOCKET)
    assert resolution.outcomes == {}
    assert [entry.event_id for entry in resolution.unrecorded] == [_MOTION]
    assert motion.outcome.exists() is False


def test_apply_is_idempotent(tmp_path: Path) -> None:
    _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
        again = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    assert again.reopened == []
    assert again.skipped == []


def test_a_distinct_non_baseline_outcome_is_left_alone(tmp_path: Path) -> None:
    """Only a duplicate is evidence of a copy; an event's own outcome is not."""
    root = _data_root(tmp_path)
    _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2018, 3, 14), resolved_at=_RESOLVED_AT
    )
    motion = _write_event(
        root,
        _MOTION,
        EventKind.motion,
        opened_at=date(2018, 1, 23),
        resolved_at=date(2018, 2, 1),
        disposition=Disposition.denied,
    )
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        result = reopen_misattributed_outcomes(conn, root, apply=True)
    assert result.reopened == []
    assert motion.outcome.is_file()


def test_an_interim_staged_event_keeps_its_own_outcome(tmp_path: Path) -> None:
    """An application's motion baseline resolves under the interim standard.

    The exemption reads the stage off the corpus row, so the ledger's committed
    ``event.yaml`` carrying no stage must not defeat it.
    """
    root = _data_root(tmp_path)
    _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2024, 7, 1), resolved_at=_RESOLVED_AT
    )
    motion = _write_event(
        root, _MOTION, EventKind.motion, opened_at=date(2024, 8, 1), resolved_at=_RESOLVED_AT
    )
    events = [
        _event_row(_BASELINE, EventKind.petition, resolved=True),
        _event_row(_MOTION, EventKind.motion, resolved=True, stage=Stage.interim),
    ]
    with _seeded(tmp_path, events) as conn:
        result = reopen_misattributed_outcomes(conn, root, apply=True)
    assert result.reopened == []
    assert motion.outcome.is_file()


def test_a_baseline_pair_is_reported_not_repaired(tmp_path: Path) -> None:
    """Reopening a lone baseline re-arms the stage-less fallback, so it is triage."""
    root = _data_root(tmp_path)
    petition = _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    appeal = _write_event(
        root, _APPEAL, EventKind.appeal, opened_at=date(2022, 1, 31), resolved_at=_RESOLVED_AT
    )
    events = [
        _event_row(_BASELINE, EventKind.petition, resolved=True),
        _event_row(_APPEAL, EventKind.appeal, resolved=True),
    ]
    with _seeded(tmp_path, events) as conn:
        result = reopen_misattributed_outcomes(conn, root, apply=True)
    assert result.reopened == []
    assert [ref for ref, _ in result.skipped] == [f"{_CASE}/{_APPEAL}", f"{_CASE}/{_BASELINE}"]
    assert all("re-arms the stage-less fallback" in reason for _, reason in result.skipped)
    assert petition.outcome.is_file()
    assert appeal.outcome.is_file()


def test_an_event_carrying_agent_output_is_skipped(tmp_path: Path) -> None:
    """Deleting the ground truth under a scored cell would strand the evaluation."""
    _, motion = _seed_copied_motion(tmp_path)
    motion.prediction_dir("claude-baseline", "20260101T000000Z").mkdir(parents=True)
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        result = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    assert result.reopened == []
    assert result.skipped == [(f"{_CASE}/{_MOTION}", "committed predict/evaluate output under it")]
    assert motion.outcome.is_file()


def test_an_event_the_corpus_does_not_know_is_never_repaired(tmp_path: Path) -> None:
    """Its stage cannot be read and the reopen would no-op, so deleting would lose data."""
    _, motion = _seed_copied_motion(tmp_path)
    # Only the baseline is in the corpus; the motion's row is absent.
    events = [_event_row(_BASELINE, EventKind.petition, resolved=True)]
    with _seeded(tmp_path, events) as conn:
        result = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    assert result.reopened == []
    assert [ref for ref, _ in result.skipped] == [f"{_CASE}/{_MOTION}"]
    assert "no row for this event" in result.skipped[0][1]
    assert motion.outcome.is_file()


def test_a_committed_evaluation_directory_also_blocks_the_delete(tmp_path: Path) -> None:
    _, motion = _seed_copied_motion(tmp_path)
    motion.evaluation_dir("claude-judge", "claude-baseline", "20260101T000000Z").mkdir(parents=True)
    with _seeded(tmp_path, _copied_motion_rows()) as conn:
        result = reopen_misattributed_outcomes(conn, _data_root(tmp_path), apply=True)
    assert result.reopened == []
    assert result.skipped == [(f"{_CASE}/{_MOTION}", "committed predict/evaluate output under it")]
    assert motion.outcome.is_file()


def test_cli_apply_repairs_both_stores(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, motion = _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["reopen-misattributed-outcomes", "--apply"])
    assert result.exit_code == 0, result.output
    assert "reopened 1 event(s)" in result.output
    assert motion.outcome.exists() is False
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        rows = {e.event_id: e.resolved for e in corpus.events_for_case(conn, _CASE)}
    assert rows == {_BASELINE: True, _MOTION: False}


def test_cli_dry_run_reports_without_writing(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, motion = _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["reopen-misattributed-outcomes"])
    assert result.exit_code == 0, result.output
    assert "would reopen 1 event(s)" in result.output
    assert f"{_CASE}/{_MOTION}" in result.output
    assert motion.outcome.is_file()
