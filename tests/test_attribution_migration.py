"""Ledger repairs: the copied-outcome reopen and the two unmintable-event removals."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.attribution_migration import (
    remove_ungranted_merits_events,
    remove_unmintable_baseline_events,
    reopen_misattributed_outcomes,
)
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths, EventPaths
from fedcourtsai.pipeline.ingest import from_api_docket
from fedcourtsai.pipeline.outcome import MERITS_EVENT_ID, resolve_case
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
    event_id: str,
    kind: EventKind,
    *,
    resolved: bool,
    stage: Stage | None = None,
    decision_target: str = "disposition",
) -> corpus.CorpusEvent:
    return corpus.CorpusEvent.model_validate(
        {
            "event_id": event_id,
            "case_id": _CASE,
            "court": "scotus",
            "kind": kind,
            "stage": stage,
            "title": "Petitioner v. Respondent",
            "decision_target": decision_target,
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


def test_cli_apply_refuses_above_the_reopen_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The blast-radius cap: over-bound applies exit non-zero and write nothing.

    The population this sweep repairs is finite and non-growing, so the bound
    converts a widened predicate from an unattended mass deletion in the
    writer lane into a loud refusal the next window's log names.
    """
    _, motion = _seed_copied_motion(tmp_path)
    with _seeded(tmp_path, _copied_motion_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["reopen-misattributed-outcomes", "--apply", "--max-reopens", "0"])
    assert result.exit_code == 1
    assert "refusing to apply 1 reopens (--max-reopens 0)" in result.output
    assert motion.outcome.is_file()  # nothing was deleted
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert all(e.resolved for e in corpus.events_for_case(conn, _CASE))


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


# --- unmintable SCOTUS case-baseline events ------------------------------------


def _entry_pinned(event_id: str, kind: EventKind, *, entry: int | None) -> corpus.CorpusEvent:
    return corpus.CorpusEvent.model_validate(
        {
            "event_id": event_id,
            "case_id": _CASE,
            "court": "scotus",
            "kind": kind,
            "title": "Petitioner v. Respondent",
            "decision_target": "disposition",
            "docket_entry_id": entry,
            "resolved": True,
        }
    )


def _seed_unmintable(tmp_path: Path) -> tuple[EventPaths, EventPaths]:
    """The spurious shape: an entry-pinned appeal event beside the real baseline."""
    root = _data_root(tmp_path)
    baseline = _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    appeal = _write_event(
        root, _APPEAL, EventKind.appeal, opened_at=date(2022, 1, 31), resolved_at=_RESOLVED_AT
    )
    return baseline, appeal


def _unmintable_rows() -> list[corpus.CorpusEvent]:
    return [
        _entry_pinned(_BASELINE, EventKind.petition, entry=None),
        _entry_pinned(_APPEAL, EventKind.appeal, entry=24),
    ]


def test_removal_dry_run_finds_the_entry_pinned_baseline(tmp_path: Path) -> None:
    _, appeal = _seed_unmintable(tmp_path)
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        result = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=False)
        assert result.applied is False
        assert result.removed == [f"{_CASE}/{_APPEAL}"]
        assert result.skipped == []
        assert len(corpus.events_for_case(conn, _CASE)) == 2
    assert appeal.event_file.is_file()


def test_removal_apply_drops_the_row_and_the_ledger_directory(tmp_path: Path) -> None:
    baseline, appeal = _seed_unmintable(tmp_path)
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        result = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, _CASE)]
    assert result.removed == [f"{_CASE}/{_APPEAL}"]
    assert remaining == [_BASELINE]
    # The whole directory goes, so the copied outcome leaves with it.
    assert appeal.base.exists() is False
    # The real baseline — not entry-pinned — is untouched.
    assert baseline.outcome.is_file()


def test_removal_is_idempotent(tmp_path: Path) -> None:
    _seed_unmintable(tmp_path)
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
        again = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
    assert again.removed == []
    assert again.skipped == []


def test_removal_skips_an_event_carrying_agent_output(tmp_path: Path) -> None:
    _, appeal = _seed_unmintable(tmp_path)
    appeal.prediction_dir("claude-baseline", "20260101T000000Z").mkdir(parents=True)
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        result = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, _CASE)]
    assert result.removed == []
    assert result.skipped == [(f"{_CASE}/{_APPEAL}", "committed predict/evaluate output under it")]
    assert sorted(remaining) == sorted([_BASELINE, _APPEAL])


def test_removal_leaves_an_entry_pinned_motion_alone(tmp_path: Path) -> None:
    """A substantive application is its own predictable thing; only baseline ids go."""
    _write_event(
        _data_root(tmp_path),
        _MOTION,
        EventKind.motion,
        opened_at=date(2018, 1, 23),
        resolved_at=None,
    )
    events = [
        _entry_pinned(_BASELINE, EventKind.petition, entry=None),
        _entry_pinned(_MOTION, EventKind.motion, entry=11),
    ]
    with _seeded(tmp_path, events) as conn:
        result = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert remaining == sorted([_BASELINE, _MOTION])


def test_delete_event_raises_when_the_row_is_absent(tmp_path: Path) -> None:
    with (
        _seeded(tmp_path, [_entry_pinned(_BASELINE, EventKind.petition, entry=None)]) as conn,
        pytest.raises(ValueError, match="no event"),
    ):
        corpus.delete_event(conn, _CASE, "evt-motion-nope")


def test_removal_leaves_a_circuit_entry_pinned_baseline_alone(tmp_path: Path) -> None:
    """A circuit notice-of-appeal entry legitimately mints a baseline-prefixed event.

    `evt-appeal-disposition-3` on a ca9 docket is entry-pinned *and* carries a
    case-baseline prefix; only the court leg of the predicate keeps it.
    """
    circuit_case = "ca9/900002"
    paths = CasePaths(_data_root(tmp_path), "ca9", 900002).event("evt-appeal-disposition-3")
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id="evt-appeal-disposition-3",
            case_id=circuit_case,
            kind=EventKind.appeal,
            title="Doe v. Roe",
            opened_at=date(2026, 6, 2),
        ),
    )
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow.model_validate({"case_id": circuit_case, "court": "ca9"})]
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent.model_validate(
                    {
                        "event_id": "evt-appeal-disposition-3",
                        "case_id": circuit_case,
                        "court": "ca9",
                        "kind": EventKind.appeal,
                        "title": "Doe v. Roe",
                        "docket_entry_id": 3,
                    }
                )
            ],
        )
        result = remove_unmintable_baseline_events(conn, _data_root(tmp_path), apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, circuit_case)]
    assert result.removed == []
    assert remaining == ["evt-appeal-disposition-3"]
    assert paths.event_file.is_file()


def test_removal_skips_an_event_whose_outcome_copies_nothing(tmp_path: Path) -> None:
    """A distinct outcome is a real observation, not a phantom to sweep away."""
    root = _data_root(tmp_path)
    _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    appeal = _write_event(
        root,
        _APPEAL,
        EventKind.appeal,
        opened_at=date(2022, 1, 31),
        resolved_at=date(2022, 3, 1),
        disposition=Disposition.denied,
    )
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        result = remove_unmintable_baseline_events(conn, root, apply=True)
    assert result.removed == []
    assert "copies no case-baseline sibling" in result.skipped[0][1]
    assert appeal.outcome.is_file()


def test_removal_skips_an_unrecognized_directory_shape(tmp_path: Path) -> None:
    """An unexpected child is reported before either store is touched."""
    _, appeal = _seed_unmintable(tmp_path)
    (appeal.base / "stray").mkdir()
    with _seeded(tmp_path, _unmintable_rows()) as conn:
        result = remove_unmintable_baseline_events(conn, root := _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert root.exists()
    assert result.removed == []
    assert "unrecognized files" in result.skipped[0][1]
    assert appeal.event_file.is_file()
    assert remaining == sorted([_BASELINE, _APPEAL])


def test_cli_removal_apply_drops_both_stores(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, appeal = _seed_unmintable(tmp_path)
    with _seeded(tmp_path, _unmintable_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["remove-unmintable-events"])
    assert dry.exit_code == 0, dry.output
    assert "would remove 1 event(s)" in dry.output
    assert appeal.base.exists()
    applied = runner.invoke(app, ["remove-unmintable-events", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "removed 1 event(s)" in applied.output
    assert appeal.base.exists() is False
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert [e.event_id for e in corpus.events_for_case(conn, _CASE)] == [_BASELINE]


def test_cli_removal_refuses_above_the_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The removal cap mirrors the reopen cap: over-bound applies write nothing."""
    _, appeal = _seed_unmintable(tmp_path)
    with _seeded(tmp_path, _unmintable_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["remove-unmintable-events", "--apply", "--max-removals", "0"])
    assert result.exit_code == 1
    assert "refusing to apply 1 removals (--max-removals 0)" in result.output
    assert appeal.base.exists()  # the ledger directory survived
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert len(corpus.events_for_case(conn, _CASE)) == 2


# --- Open merits events on a docket the corpus records no cert grant --------


_GRANTED_AT = date(2021, 1, 8)


def _seed_ungranted_merits(tmp_path: Path) -> tuple[EventPaths, EventPaths]:
    """The stranded shape: an open merits event beside the case's resolved petition."""
    root = _data_root(tmp_path)
    baseline = _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    merits = _write_event(
        root, MERITS_EVENT_ID, EventKind.order, opened_at=_GRANTED_AT, resolved_at=None
    )
    return baseline, merits


def _ungranted_merits_rows(*, resolved: bool = False) -> list[corpus.CorpusEvent]:
    return [
        _event_row(_BASELINE, EventKind.petition, resolved=True, stage=Stage.cert),
        _event_row(
            MERITS_EVENT_ID,
            EventKind.order,
            resolved=resolved,
            stage=Stage.merits,
            decision_target="judgment",
        ),
    ]


def test_ungranted_merits_dry_run_finds_the_open_merits_event(tmp_path: Path) -> None:
    _, merits = _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=False)
        assert result.applied is False
        assert result.removed == [f"{_CASE}/{MERITS_EVENT_ID}"]
        assert result.skipped == []
        assert len(corpus.events_for_case(conn, _CASE)) == 2
    assert merits.event_file.is_file()


def test_ungranted_merits_apply_drops_the_row_and_the_ledger_directory(tmp_path: Path) -> None:
    baseline, merits = _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, _CASE)]
    assert result.removed == [f"{_CASE}/{MERITS_EVENT_ID}"]
    assert remaining == [_BASELINE]
    assert merits.base.exists() is False
    # The cert-stage event the case really has is untouched.
    assert baseline.outcome.is_file()


def test_ungranted_merits_leaves_a_granted_docket_alone(tmp_path: Path) -> None:
    """The grant column is the whole predicate: a real grant keeps its merits event."""
    _, merits = _seed_ungranted_merits(tmp_path)
    with _seeded(
        tmp_path, _ungranted_merits_rows(), date_cert_granted=_GRANTED_AT.isoformat()
    ) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == []
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])
    assert merits.event_file.is_file()


def test_ungranted_merits_leaves_a_resolved_merits_event_alone(tmp_path: Path) -> None:
    """A resolved merits event carries an observed judgment, whatever the row reads."""
    _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows(resolved=True)) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_leaves_an_open_cert_event_alone(tmp_path: Path) -> None:
    """Every pending petition is an open event on an ungranted row; only merits go."""
    root = _data_root(tmp_path)
    _write_event(root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=None)
    rows = [_event_row(_BASELINE, EventKind.petition, resolved=False, stage=Stage.cert)]
    with _seeded(tmp_path, rows) as conn:
        result = remove_ungranted_merits_events(conn, root, apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, _CASE)]
    assert result.removed == []
    assert remaining == [_BASELINE]


def test_ungranted_merits_leaves_a_non_scotus_merits_event_alone(tmp_path: Path) -> None:
    """`date_cert_granted` is null on every circuit row, so the court leg is load-bearing."""
    circuit_case = "ca9/900003"
    paths = CasePaths(_data_root(tmp_path), "ca9", 900003).event(MERITS_EVENT_ID)
    write_yaml(
        paths.event_file,
        PredictableEvent(
            event_id=MERITS_EVENT_ID,
            case_id=circuit_case,
            kind=EventKind.order,
            title="Doe v. Roe",
            opened_at=date(2026, 6, 2),
        ),
    )
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn, [corpus.CorpusRow.model_validate({"case_id": circuit_case, "court": "ca9"})]
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent.model_validate(
                    {
                        "event_id": MERITS_EVENT_ID,
                        "case_id": circuit_case,
                        "court": "ca9",
                        "kind": EventKind.order,
                        "stage": Stage.merits,
                        "title": "Doe v. Roe",
                        "decision_target": "judgment",
                    }
                )
            ],
        )
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = [e.event_id for e in corpus.events_for_case(conn, circuit_case)]
    assert result.removed == []
    assert remaining == [MERITS_EVENT_ID]
    assert paths.event_file.is_file()


def test_ungranted_merits_skips_an_event_carrying_agent_output(tmp_path: Path) -> None:
    _, merits = _seed_ungranted_merits(tmp_path)
    merits.prediction_dir("claude-baseline", "20260101T000000Z").mkdir(parents=True)
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == [
        (f"{_CASE}/{MERITS_EVENT_ID}", "committed predict/evaluate output under it")
    ]
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_skips_a_committed_outcome(tmp_path: Path) -> None:
    """An open row beside a recorded judgment is a store disagreement, not a phantom."""
    root = _data_root(tmp_path)
    _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    merits = _write_event(
        root,
        MERITS_EVENT_ID,
        EventKind.order,
        opened_at=_GRANTED_AT,
        resolved_at=date(2022, 6, 30),
    )
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, root, apply=True)
    assert result.removed == []
    assert "disagree about a recorded judgment" in result.skipped[0][1]
    assert merits.outcome.is_file()


def test_ungranted_merits_skips_an_unrecognized_directory_shape(tmp_path: Path) -> None:
    """An unexpected child is reported before either store is touched."""
    _, merits = _seed_ungranted_merits(tmp_path)
    (merits.base / "stray").mkdir()
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert "unrecognized files" in result.skipped[0][1]
    assert merits.event_file.is_file()
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_removal_is_idempotent(tmp_path: Path) -> None:
    _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        again = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
    assert again.removed == []
    assert again.skipped == []


def test_cli_ungranted_merits_apply_drops_both_stores(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, merits = _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["remove-ungranted-merits-events"])
    assert dry.exit_code == 0, dry.output
    assert "would remove 1 event(s)" in dry.output
    assert merits.base.exists()
    applied = runner.invoke(app, ["remove-ungranted-merits-events", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "removed 1 event(s)" in applied.output
    assert merits.base.exists() is False
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert [e.event_id for e in corpus.events_for_case(conn, _CASE)] == [_BASELINE]


def test_cli_ungranted_merits_refuses_above_the_bound(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The bound mirrors the sibling sweep's: an over-bound apply writes nothing."""
    _, merits = _seed_ungranted_merits(tmp_path)
    with _seeded(tmp_path, _ungranted_merits_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(
        app, ["remove-ungranted-merits-events", "--apply", "--max-removals", "0"]
    )
    assert result.exit_code == 1
    assert "refusing to apply 1 removals (--max-removals 0)" in result.output
    assert merits.base.exists()  # the ledger directory survived
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert len(corpus.events_for_case(conn, _CASE)) == 2


# --- The failed-attempt opt-in ---------------------------------------------


_CELL_RUN = "20260816T170829Z"


def _write_cell_file(paths: EventPaths, predictor: str, filename: str) -> Path:
    """One committed file under a predict cell's own run directory."""
    run_dir = paths.prediction_dir(predictor, _CELL_RUN)
    run_dir.mkdir(parents=True, exist_ok=True)
    document = run_dir / filename
    document.write_text("{}\n", encoding="utf-8")
    return document


def test_ungranted_merits_skips_attempt_records_by_default(tmp_path: Path) -> None:
    """The opt-in is opt-in: an attempt-only phantom is skipped unless it is asked for."""
    _, merits = _seed_ungranted_merits(tmp_path)
    attempt = _write_cell_file(merits, "claude-baseline", "attempt.json")
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(conn, _data_root(tmp_path), apply=True)
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == [
        (f"{_CASE}/{MERITS_EVENT_ID}", "committed predict/evaluate output under it")
    ]
    assert attempt.is_file()
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_opt_in_removes_an_attempt_only_phantom(tmp_path: Path) -> None:
    """Under the flag the phantom goes, and the failure records go with its directory."""
    _, merits = _seed_ungranted_merits(tmp_path)
    _write_cell_file(merits, "claude-baseline", "attempt.json")
    _write_cell_file(merits, "gemini-baseline", "attempt.json")
    _write_cell_file(merits, "codex-baseline", "attempt.json")
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(
            conn, _data_root(tmp_path), apply=True, include_failed_attempts=True
        )
        remaining = [e.event_id for e in corpus.events_for_case(conn, _CASE)]
    assert result.removed == [f"{_CASE}/{MERITS_EVENT_ID}"]
    assert result.skipped == []
    assert merits.base.exists() is False
    assert remaining == [_BASELINE]


def test_ungranted_merits_opt_in_still_skips_a_predicted_event(tmp_path: Path) -> None:
    """Guard precision: one prediction.json beside the attempts keeps the event."""
    _, merits = _seed_ungranted_merits(tmp_path)
    _write_cell_file(merits, "gemini-baseline", "attempt.json")
    prediction = _write_cell_file(merits, "claude-baseline", "prediction.json")
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(
            conn, _data_root(tmp_path), apply=True, include_failed_attempts=True
        )
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == [
        (f"{_CASE}/{MERITS_EVENT_ID}", "committed predict/evaluate output under it")
    ]
    assert prediction.is_file()
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_opt_in_still_skips_a_graded_event(tmp_path: Path) -> None:
    """An evaluations/ directory blocks the opt-in even when every predict file is an attempt."""
    _, merits = _seed_ungranted_merits(tmp_path)
    _write_cell_file(merits, "claude-baseline", "attempt.json")
    merits.evaluations_dir.mkdir(parents=True)
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(
            conn, _data_root(tmp_path), apply=True, include_failed_attempts=True
        )
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == [
        (f"{_CASE}/{MERITS_EVENT_ID}", "committed predict/evaluate output under it")
    ]
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_ungranted_merits_opt_in_still_skips_a_committed_outcome(tmp_path: Path) -> None:
    """The outcome refusal is independent of the flag, so the opt-in cannot reach a judgment."""
    root = _data_root(tmp_path)
    _write_event(
        root, _BASELINE, EventKind.petition, opened_at=date(2020, 11, 5), resolved_at=_RESOLVED_AT
    )
    merits = _write_event(
        root,
        MERITS_EVENT_ID,
        EventKind.order,
        opened_at=_GRANTED_AT,
        resolved_at=date(2022, 6, 30),
    )
    _write_cell_file(merits, "claude-baseline", "attempt.json")
    with _seeded(tmp_path, _ungranted_merits_rows()) as conn:
        result = remove_ungranted_merits_events(
            conn, root, apply=True, include_failed_attempts=True
        )
    assert result.removed == []
    assert "disagree about a recorded judgment" in result.skipped[0][1]
    assert merits.outcome.is_file()


def test_ungranted_merits_opt_in_leaves_a_granted_docket_alone(tmp_path: Path) -> None:
    """The flag narrows a skip; it never widens the population the predicate selects."""
    _, merits = _seed_ungranted_merits(tmp_path)
    _write_cell_file(merits, "claude-baseline", "attempt.json")
    with _seeded(
        tmp_path, _ungranted_merits_rows(), date_cert_granted=_GRANTED_AT.isoformat()
    ) as conn:
        result = remove_ungranted_merits_events(
            conn, _data_root(tmp_path), apply=True, include_failed_attempts=True
        )
        remaining = sorted(e.event_id for e in corpus.events_for_case(conn, _CASE))
    assert result.removed == []
    assert result.skipped == []
    assert remaining == sorted([_BASELINE, MERITS_EVENT_ID])


def test_cli_ungranted_merits_opt_in_flag_drops_the_attempt_only_phantom(  # type: ignore[no-untyped-def]
    tmp_path: Path, monkeypatch
) -> None:
    _, merits = _seed_ungranted_merits(tmp_path)
    _write_cell_file(merits, "claude-baseline", "attempt.json")
    with _seeded(tmp_path, _ungranted_merits_rows()):
        pass
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(_data_root(tmp_path)))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    without = runner.invoke(app, ["remove-ungranted-merits-events"])
    assert without.exit_code == 0, without.output
    assert "would remove 0 event(s); skipped 1 for triage" in without.output
    with_flag = runner.invoke(app, ["remove-ungranted-merits-events", "--include-failed-attempts"])
    assert with_flag.exit_code == 0, with_flag.output
    assert "would remove 1 event(s); skipped 0 for triage" in with_flag.output
    assert merits.base.exists()  # still a dry run
    applied = runner.invoke(
        app, ["remove-ungranted-merits-events", "--apply", "--include-failed-attempts"]
    )
    assert applied.exit_code == 0, applied.output
    assert "removed 1 event(s)" in applied.output
    assert merits.base.exists() is False
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        assert [e.event_id for e in corpus.events_for_case(conn, _CASE)] == [_BASELINE]
