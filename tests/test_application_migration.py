"""The application-baseline relabel: detection, the rename, guards, idempotency."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.application_migration import (
    MOTION_BASELINE_EVENT_ID,
    PETITION_BASELINE_EVENT_ID,
    relabel_application_baseline_events,
)
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.ingest import default_event, from_bulk_row
from fedcourtsai.schemas import EventKind

runner = CliRunner()

_APPLICATION = "scotus/900001"
_CERT = "scotus/900002"


def _row(case_id: str, docket_number: str, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "scotus",
        "docket_number": docket_number,
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _cert_shaped_baseline(case_id: str, **kw: object) -> corpus.CorpusEvent:
    """The mislabeled baseline an application docket carried before the relabel."""
    base: dict[str, object] = {
        "event_id": PETITION_BASELINE_EVENT_ID,
        "case_id": case_id,
        "court": "scotus",
        "kind": EventKind.petition,
        "stage": "cert",
        "title": "Applicant v. Respondent",
        "decision_target": "disposition",
        "opened_at": date(2024, 8, 1),
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


@contextmanager
def _seeded(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """An application docket with the cert-shaped baseline, beside a cert docket."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [_row(_APPLICATION, "24A1099"), _row(_CERT, "24-1099")],
        )
        corpus.upsert_events(
            conn,
            [
                _cert_shaped_baseline(_APPLICATION, description="stay application"),
                _cert_shaped_baseline(_CERT),
            ],
        )
        yield conn


def _data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


def test_dry_run_reports_and_writes_nothing(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        result = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=False)
        assert result.applied is False
        assert result.renamed == [_APPLICATION]
        assert result.already_relabeled == 0
        assert result.skipped == []
        events = corpus.events_for_case(conn, _APPLICATION)
    assert [e.event_id for e in events] == [PETITION_BASELINE_EVENT_ID]


def test_apply_renames_and_carries_every_field(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        result = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        assert result.applied is True
        assert result.renamed == [_APPLICATION]
        (event,) = corpus.events_for_case(conn, _APPLICATION)
    assert event.event_id == MOTION_BASELINE_EVENT_ID
    assert EventKind(event.kind) == EventKind.motion
    assert event.stage == "interim"
    assert event.title == "Applicant v. Respondent"
    assert event.description == "stay application"
    assert event.decision_target == "disposition"
    assert event.opened_at == date(2024, 8, 1)
    assert event.resolved is False


def test_apply_preserves_the_resolved_latch(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        corpus.set_event_resolved(conn, _APPLICATION, PETITION_BASELINE_EVENT_ID)
        relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _APPLICATION)
    assert event.resolved is True


def test_cert_docket_is_untouched(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        (event,) = corpus.events_for_case(conn, _CERT)
    assert event.event_id == PETITION_BASELINE_EVENT_ID
    assert event.stage == "cert"


def test_second_run_is_a_noop(tmp_path: Path) -> None:
    with _seeded(tmp_path) as conn:
        first = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        second = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _APPLICATION)
    assert first.renamed == [_APPLICATION]
    assert second.renamed == []
    assert second.already_relabeled == 1
    assert [e.event_id for e in events] == [MOTION_BASELINE_EVENT_ID]


def test_rediscovery_reproduces_exactly_the_migrated_event(tmp_path: Path) -> None:
    # A fresh `default_event` on the same docket post-migration must land on the
    # migrated identity — one row, no dual-event resurrection.
    with _seeded(tmp_path) as conn:
        relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        rediscovered = default_event(
            from_bulk_row({"id": "900001", "court_id": "scotus", "docket_number": "24A1099"})
        )
        assert rediscovered.event_id == MOTION_BASELINE_EVENT_ID
        corpus.upsert_events(conn, [rediscovered])
        events = corpus.events_for_case(conn, _APPLICATION)
    assert [e.event_id for e in events] == [MOTION_BASELINE_EVENT_ID]


def test_dual_baseline_collapses_onto_the_motion_row(tmp_path: Path) -> None:
    # The pre-migration window can leave both identities on one docket (the
    # forward fix re-extracts the motion baseline while the old petition row
    # persists); the relabel folds the pair onto the motion row.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(
            conn,
            [
                default_event(
                    from_bulk_row(
                        {"id": "900001", "court_id": "scotus", "docket_number": "24A1099"}
                    )
                )
            ],
        )
        result = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _APPLICATION)
    assert result.renamed == [_APPLICATION]
    assert [e.event_id for e in events] == [MOTION_BASELINE_EVENT_ID]


def test_committed_ledger_artifacts_block_the_rename(tmp_path: Path) -> None:
    # A rename would orphan committed judgments under the old identity against
    # the corpus (the referential validation's no-orphan-judgments check), so
    # such a case is skipped and reported, never folded.
    data_root = _data_root(tmp_path)
    ledger_dir = CasePaths(data_root, "scotus", 900001).event(PETITION_BASELINE_EVENT_ID).base
    ledger_dir.mkdir(parents=True)
    with _seeded(tmp_path) as conn:
        result = relabel_application_baseline_events(conn, data_root, apply=True)
        events = corpus.events_for_case(conn, _APPLICATION)
    assert result.renamed == []
    ((case_id, reason),) = result.skipped
    assert case_id == _APPLICATION
    assert "ledger" in reason
    assert [e.event_id for e in events] == [PETITION_BASELINE_EVENT_ID]  # untouched


def test_entry_pinned_motion_row_blocks_the_fold(tmp_path: Path) -> None:
    # An existing evt-motion-disposition row pinned to a docket entry is some
    # filing's event, not the case baseline — folding onto it would write one
    # filing's resolved latch and entry pin onto another. Skip and report.
    with _seeded(tmp_path) as conn:
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MOTION_BASELINE_EVENT_ID,
                    case_id=_APPLICATION,
                    court="scotus",
                    kind=EventKind.motion,
                    title="entry-pinned motion",
                    docket_entry_id=7,
                )
            ],
        )
        result = relabel_application_baseline_events(conn, _data_root(tmp_path), apply=True)
        events = corpus.events_for_case(conn, _APPLICATION)
    assert result.renamed == []
    ((case_id, reason),) = result.skipped
    assert case_id == _APPLICATION
    assert "entry-pinned" in reason
    # Both rows survive untouched for triage.
    assert [e.event_id for e in events] == [MOTION_BASELINE_EVENT_ID, PETITION_BASELINE_EVENT_ID]


def test_cli_dry_run_then_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(conn, [_row(_APPLICATION, "24A1099")])
        corpus.upsert_events(conn, [_cert_shaped_baseline(_APPLICATION)])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))

    result = runner.invoke(app, ["relabel-application-events"])
    assert result.exit_code == 0, result.output
    assert "dry-run" in result.output
    assert "would rename 1 baseline event(s)" in result.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _APPLICATION)
        assert event.event_id == PETITION_BASELINE_EVENT_ID

    applied = runner.invoke(app, ["relabel-application-events", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        (event,) = corpus.events_for_case(conn, _APPLICATION)
        assert event.event_id == MOTION_BASELINE_EVENT_ID


def test_cli_fails_loud_when_the_corpus_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "nowhere"))
    result = runner.invoke(app, ["relabel-application-events"])
    assert result.exit_code == 1
