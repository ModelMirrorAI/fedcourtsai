"""A predict cell's writes held to its own run directory (`fedcourtsai.write_confinement`)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import AgentFlags, FlagSeverity, FlagSource
from fedcourtsai.write_confinement import (
    ConfinementError,
    confine_writes,
    record_baseline,
)

runner = CliRunner()

COURT = "scotus"
DOCKET = 9526000560
EVENT = "evt-brief-response-disposition"
ACTOR = "gemini-baseline"
RUN = "20261029T212853Z"
CASE = f"cases/{COURT}/{DOCKET}"
EVENT_DIR = f"{CASE}/events/{EVENT}"
OWN = f"{EVENT_DIR}/predictions/{ACTOR}/{RUN}"


def _tree(root: Path) -> dict[str, str]:
    """Every entry under ``root``: a file's bytes, a link's target, a directory's marker."""
    found: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in dirnames:
            path = base / name
            relative = path.relative_to(root).as_posix()
            found[relative] = f"-> {os.readlink(path)}" if path.is_symlink() else "<dir>"
        for name in filenames:
            path = base / name
            relative = path.relative_to(root).as_posix()
            found[relative] = (
                f"-> {os.readlink(path)}" if path.is_symlink() else path.read_text("utf-8")
            )
    return found


@pytest.fixture
def data_root(tmp_path: Path) -> Path:
    """A data tree as the agent is handed it: hidden trees out, the record provisioned."""
    root = tmp_path / "data"
    files = {
        f"{EVENT_DIR}/event.yaml": "event_id: evt-brief-response-disposition\n",
        f"{CASE}/record/context.json": '{"mode": "forward"}\n',
        f"{CASE}/record/documents/petition.txt": "QUESTION PRESENTED\n",
        "cases/scotus/1/events/evt-x/event.yaml": "event_id: evt-x\n",
        "schedule/schedule.json": "{}\n",
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (root / OWN).mkdir(parents=True)
    return root


def _stash(tmp_path: Path) -> Path:
    return tmp_path / "runner-temp" / "write-baseline"


def test_writes_inside_the_run_directory_are_left_as_written(
    data_root: Path, tmp_path: Path
) -> None:
    record_baseline(data_root, _stash(tmp_path))
    (data_root / OWN / "prediction.json").write_text("{}", encoding="utf-8")
    (data_root / OWN / "notes").mkdir()
    (data_root / OWN / "notes" / "scratch.md").write_text("x", encoding="utf-8")
    before = _tree(data_root)

    report = confine_writes(data_root, _stash(tmp_path), data_root / OWN)

    assert not report.changed
    assert _tree(data_root) == before


def test_the_observed_stray_flags_file_above_the_run_directory_is_removed(
    data_root: Path, tmp_path: Path
) -> None:
    """The real case: a flags.json one level above the run directory."""
    record_baseline(data_root, _stash(tmp_path))
    baseline = _tree(data_root)
    stray = f"{EVENT_DIR}/predictions/{ACTOR}/flags.json"
    (data_root / stray).write_text("{}", encoding="utf-8")

    report = confine_writes(data_root, _stash(tmp_path), data_root / OWN)

    assert report.removed == [stray]
    assert report.restored == report.failed == []
    assert _tree(data_root) == baseline


def test_the_tree_is_put_back_whatever_the_agent_did_outside_its_run(
    data_root: Path, tmp_path: Path
) -> None:
    record_baseline(data_root, _stash(tmp_path))
    baseline = _tree(data_root)
    # A scratch file beside the provisioned record, the restored oracle, an
    # edited event definition, a deleted record file, a new directory tree,
    # and a link where a provisioned directory stood.
    (data_root / CASE / "record/documents/petition.txt.grep").write_text("hit", encoding="utf-8")
    (data_root / "qp-topics").mkdir()
    (data_root / "qp-topics/qp-topics.json").write_text("{}", encoding="utf-8")
    (data_root / EVENT_DIR / "event.yaml").write_text("event_id: forged\n", encoding="utf-8")
    (data_root / CASE / "record/context.json").unlink()
    (data_root / "cases/scotus/1/events/evt-x/predictions/x/y").mkdir(parents=True)
    (data_root / "schedule/schedule.json").unlink()
    (data_root / "schedule").rmdir()
    (data_root / "schedule").symlink_to("/etc")

    report = confine_writes(data_root, _stash(tmp_path), data_root / OWN)

    assert report.failed == []
    assert report.removed == sorted(
        [
            f"{CASE}/record/documents/petition.txt.grep",
            "cases/scotus/1/events/evt-x/predictions/",
            "cases/scotus/1/events/evt-x/predictions/x/",
            "cases/scotus/1/events/evt-x/predictions/x/y/",
            "qp-topics/",
            "qp-topics/qp-topics.json",
            "schedule",
        ]
    )
    assert report.restored == sorted(
        [
            f"{CASE}/record/context.json",
            f"{EVENT_DIR}/event.yaml",
            "schedule/schedule.json",
        ]
    )
    assert _tree(data_root) == baseline


def test_a_link_standing_in_for_the_run_directory_is_removed(
    data_root: Path, tmp_path: Path
) -> None:
    """A link there would carry the cell's later writes, and its upload, elsewhere."""
    (data_root / OWN).rmdir()
    record_baseline(data_root, _stash(tmp_path))
    (data_root / OWN).symlink_to(data_root / CASE / "record")

    report = confine_writes(data_root, _stash(tmp_path), data_root / OWN)

    assert report.removed == [OWN]
    assert not (data_root / OWN).is_symlink()


def test_a_run_directory_created_by_the_agent_and_its_parents_are_kept(
    data_root: Path, tmp_path: Path
) -> None:
    (data_root / OWN).rmdir()
    (data_root / OWN).parent.rmdir()
    (data_root / OWN).parent.parent.rmdir()
    record_baseline(data_root, _stash(tmp_path))
    (data_root / OWN).mkdir(parents=True)
    (data_root / OWN / "prediction.json").write_text("{}", encoding="utf-8")

    report = confine_writes(data_root, _stash(tmp_path), data_root / OWN)

    assert not report.changed
    assert (data_root / OWN / "prediction.json").is_file()


def test_a_baseline_is_recorded_once(data_root: Path, tmp_path: Path) -> None:
    record_baseline(data_root, _stash(tmp_path))
    with pytest.raises(ConfinementError, match="recorded once"):
        record_baseline(data_root, _stash(tmp_path))


def test_a_missing_or_foreign_baseline_is_refused(data_root: Path, tmp_path: Path) -> None:
    with pytest.raises(ConfinementError, match="no readable baseline"):
        confine_writes(data_root, _stash(tmp_path), data_root / OWN)
    other = tmp_path / "other"
    other.mkdir()
    record_baseline(other, _stash(tmp_path))
    with pytest.raises(ConfinementError, match="recorded for"):
        confine_writes(data_root, _stash(tmp_path), data_root / OWN)


def test_a_run_directory_outside_the_data_root_is_refused(data_root: Path, tmp_path: Path) -> None:
    record_baseline(data_root, _stash(tmp_path))
    with pytest.raises(ConfinementError, match="is not under"):
        confine_writes(data_root, _stash(tmp_path), tmp_path / "elsewhere")


def test_a_path_that_cannot_be_put_back_is_reported_and_the_rest_still_are(
    data_root: Path, tmp_path: Path
) -> None:
    stash = _stash(tmp_path)
    record_baseline(data_root, stash)
    (data_root / EVENT_DIR / "event.yaml").write_text("forged\n", encoding="utf-8")
    (data_root / "schedule/schedule.json").write_text("forged\n", encoding="utf-8")
    # The kept copy of one of them is gone, so only the other can be restored.
    (stash / "files" / EVENT_DIR / "event.yaml").unlink()

    report = confine_writes(data_root, stash, data_root / OWN)

    assert report.failed == [f"{EVENT_DIR}/event.yaml"]
    assert report.restored == ["schedule/schedule.json"]
    assert (data_root / "schedule/schedule.json").read_text("utf-8") == "{}\n"


def _cli(*args: str) -> list[str]:
    return [
        *args,
        "--court",
        COURT,
        "--docket",
        str(DOCKET),
        "--event",
        EVENT,
        "--actor",
        ACTOR,
        "--run-id",
        RUN,
    ]


def test_the_commands_put_the_tree_back_and_flag_it_in_the_cells_flags(
    data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    stash = ["--stash-dir", str(_stash(tmp_path))]
    recorded = runner.invoke(app, ["record-write-baseline", *stash])
    assert recorded.exit_code == 0, recorded.output
    stray = data_root / EVENT_DIR / "predictions" / ACTOR / "flags.json"
    stray.write_text("{}", encoding="utf-8")

    result = runner.invoke(app, _cli("confine-cell-writes", *stash))

    assert result.exit_code == 0, result.output
    assert not stray.exists()
    assert f"removed data/{EVENT_DIR}/predictions/{ACTOR}/flags.json" in result.output
    flags_path = CasePaths(data_root, COURT, DOCKET).event(EVENT).prediction_flags(ACTOR, RUN)
    flags = AgentFlags.model_validate_json(flags_path.read_text("utf-8"))
    (note,) = flags.flags
    assert note.source == FlagSource.harness
    assert note.severity == FlagSeverity.warning
    assert note.event_id == EVENT
    assert "removed 1 added path(s)" in note.message
    assert f"predictions/{ACTOR}/flags.json" in note.message

    # A second pass over a tree already put back finds nothing and adds nothing.
    again = runner.invoke(app, _cli("confine-cell-writes", *stash))
    assert again.exit_code == 0, again.output
    assert "data tree unchanged" in again.output
    assert len(AgentFlags.model_validate_json(flags_path.read_text("utf-8")).flags) == 1


def test_the_note_lands_beside_a_flags_file_the_agent_mis_shaped(
    data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    stash = ["--stash-dir", str(_stash(tmp_path))]
    assert runner.invoke(app, ["record-write-baseline", *stash]).exit_code == 0
    flags_path = data_root / OWN / "flags.json"
    flags_path.write_text(json.dumps({"flags": [{"message": "hi"}]}), encoding="utf-8")
    (data_root / "schedule/schedule.json").write_text("forged\n", encoding="utf-8")

    result = runner.invoke(app, _cli("confine-cell-writes", *stash))

    assert result.exit_code == 0, result.output
    flags = AgentFlags.model_validate_json(flags_path.read_text("utf-8"))
    assert any("restored 1 changed or deleted path(s)" in item.message for item in flags.flags)


def test_a_cell_with_no_run_directory_is_put_back_without_creating_one(
    data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    (data_root / OWN).rmdir()
    stash = ["--stash-dir", str(_stash(tmp_path))]
    assert runner.invoke(app, ["record-write-baseline", *stash]).exit_code == 0
    (data_root / "schedule/stray.txt").write_text("x", encoding="utf-8")

    result = runner.invoke(app, _cli("confine-cell-writes", *stash))

    assert result.exit_code == 0, result.output
    assert not (data_root / "schedule/stray.txt").exists()
    assert not (data_root / OWN).exists()


def test_the_command_exits_non_zero_when_something_stays_out(
    data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    stash_dir = _stash(tmp_path)
    stash = ["--stash-dir", str(stash_dir)]
    assert runner.invoke(app, ["record-write-baseline", *stash]).exit_code == 0
    (data_root / EVENT_DIR / "event.yaml").write_text("forged\n", encoding="utf-8")
    (stash_dir / "files" / EVENT_DIR / "event.yaml").unlink()

    result = runner.invoke(app, _cli("confine-cell-writes", *stash))

    assert result.exit_code == 1
    flags_path = data_root / OWN / "flags.json"
    (note,) = AgentFlags.model_validate_json(flags_path.read_text("utf-8")).flags
    assert note.severity == FlagSeverity.blocker
    assert "could not put back 1 path(s)" in note.message


def test_the_confine_command_exits_non_zero_with_no_baseline(
    data_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    result = runner.invoke(app, _cli("confine-cell-writes", "--stash-dir", str(_stash(tmp_path))))
    assert result.exit_code == 1
    assert "write confinement failed" in result.output
