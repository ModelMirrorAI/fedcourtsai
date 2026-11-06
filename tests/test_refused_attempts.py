"""The refused-attempt removal: which named failure facts it deletes, and when it refuses."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.refused_attempts import (
    AttemptCell,
    parse_cell,
    remove_refused_attempts,
)
from fedcourtsai.schemas import CellFailure, Disposition, Outcome
from fedcourtsai.serialize import write_json, write_text

COURT, DOCKET, EVENT, RUN = (
    "scotus",
    9526000634,
    "evt-brief-response-disposition",
    "20261105T203825Z",
)


def seed_refused_attempt(
    data_root: Path,
    court: str = COURT,
    docket: int = DOCKET,
    event_id: str = EVENT,
    *,
    run_id: str = RUN,
    actor: str = "claude-baseline",
    resolved_at: date | None = None,
    **fact: str,
) -> Path:
    """Commit one predict ``no_output`` fact on an event resolved the run's day.

    ``resolved_at`` defaults to the run's own date, and ``fact`` overrides the
    record's ``seam`` or ``error_class``; returns the fact's path.
    """
    event = CasePaths(data_root, court, docket).event(event_id)
    path = event.prediction_attempt(actor, run_id)
    write_json(
        path,
        CellFailure.model_validate(
            {
                "seam": "predict",
                "actor": actor,
                "court": court,
                "docket": docket,
                "event_id": event_id,
                "run_id": run_id,
                "error_class": "no_output",
                **fact,
            }
        ),
    )
    day = resolved_at or date(int(run_id[:4]), int(run_id[4:6]), int(run_id[6:8]))
    write_json(
        event.outcome,
        Outcome(
            case_id=f"{court}/{docket}",
            event_id=event_id,
            resolved_at=day,
            actual_disposition=Disposition.denied,
            actual_granted=0,
        ),
    )
    return path


def _cell(actor: str = "claude-baseline") -> AttemptCell:
    return AttemptCell(COURT, DOCKET, EVENT, RUN, actor)


def test_a_dry_run_lists_the_named_facts_and_deletes_nothing(tmp_path: Path) -> None:
    paths = [seed_refused_attempt(tmp_path, actor=a) for a in ("claude-baseline", "codex-baseline")]
    result = remove_refused_attempts(
        tmp_path, [_cell("claude-baseline"), _cell("codex-baseline")], apply=False
    )
    assert result.removed == paths
    assert not result.refused
    assert all(p.exists() for p in paths)


def test_an_apply_deletes_the_facts_and_the_directories_they_leave_empty(tmp_path: Path) -> None:
    kept = seed_refused_attempt(tmp_path, actor="codex-baseline")
    gone = seed_refused_attempt(tmp_path, actor="claude-baseline")
    result = remove_refused_attempts(tmp_path, [_cell(), _cell()], apply=True)
    assert result.removed == [gone]
    assert not gone.parent.parent.exists()
    assert kept.exists()
    event = CasePaths(tmp_path, COURT, DOCKET).event(EVENT)
    assert event.outcome.exists()
    remove_refused_attempts(tmp_path, [_cell("codex-baseline")], apply=True)
    assert not event.predictions_dir.exists()
    assert event.outcome.exists()


@pytest.mark.parametrize(
    ("setup", "reason"),
    [
        ("sibling", "holds more than attempt.json"),
        ("evaluate", "not a predict no_output one"),
        ("partial", "not a predict no_output one"),
        ("no-outcome", "no committed outcome"),
        ("late-outcome", "after the run"),
        ("absent", "no committed run directory"),
    ],
)
def test_a_fact_that_cannot_be_a_resolved_refusal_refuses_the_whole_list(
    tmp_path: Path, setup: str, reason: str
) -> None:
    good = seed_refused_attempt(tmp_path)
    other = DOCKET + 1
    bad_cell = AttemptCell(COURT, other, EVENT, RUN, "claude-baseline")
    if setup != "absent":
        bad = seed_refused_attempt(
            tmp_path,
            docket=other,
            seam="evaluate" if setup == "evaluate" else "predict",
            error_class="partial" if setup == "partial" else "no_output",
            resolved_at=date(2026, 11, 6) if setup == "late-outcome" else None,
        )
        if setup == "sibling":
            write_text(bad.parent / "usage.json", "{}")
        if setup == "no-outcome":
            CasePaths(tmp_path, COURT, other).event(EVENT).outcome.unlink()
    result = remove_refused_attempts(tmp_path, [_cell(), bad_cell], apply=True)
    assert [ref for ref, _ in result.refused] == [bad_cell.ref]
    assert reason in result.refused[0][1]
    assert good.exists()


def test_a_fact_naming_another_cell_is_refused(tmp_path: Path) -> None:
    path = seed_refused_attempt(tmp_path)
    write_json(
        path,
        CellFailure(
            seam="predict",
            actor="gemini-baseline",
            court=COURT,
            docket=DOCKET,
            event_id=EVENT,
            run_id=RUN,
            error_class="no_output",
        ),
    )
    result = remove_refused_attempts(tmp_path, [_cell()], apply=True)
    assert "names a different cell" in result.refused[0][1]
    assert path.exists()


def test_the_cell_grammar_rejects_a_path_segment() -> None:
    assert parse_cell(_cell().ref) == _cell()
    with pytest.raises(ValueError, match="malformed cell"):
        parse_cell("scotus/1/evt-x/../claude-baseline")


def test_the_command_refuses_the_whole_list_with_exit_one(tmp_path: Path) -> None:
    kept = seed_refused_attempt(tmp_path)
    env = {"FEDCOURTS_DATA_ROOT": str(tmp_path)}
    missing = AttemptCell(COURT, DOCKET, EVENT, RUN, "codex-baseline").ref
    refused = CliRunner().invoke(
        app,
        ["remove-refused-attempts", "--cell", _cell().ref, "--cell", missing, "--apply"],
        env=env,
    )
    assert refused.exit_code == 1
    assert "refusing the whole list" in refused.output
    assert kept.exists()
    applied = CliRunner().invoke(
        app, ["remove-refused-attempts", "--cell", _cell().ref, "--apply"], env=env
    )
    assert applied.exit_code == 0, applied.output
    assert "removed 1 failure fact(s)" in applied.output
    assert not kept.exists()
