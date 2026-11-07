"""Finding the statpack build a predict cell read: ``placed_build`` and ``statpack-at``.

A metrics refresh landing between forecast and grading replaces the committed
pack, so a judge needs the build the predictor anchored on. The cell records it
at placement (``context.statpack_digest``, every stage); the lookup checks that
record against the build in force at the predict run id, the bound the stamp's
frozen-anchor check uses, and hands back that build's committed files.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline.base_rates import statpack_digest
from fedcourtsai.schemas import (
    CertAnchor,
    Disposition,
    Prediction,
    PredictionContext,
    StatPack,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.statpack_history import (
    CHECKOUT_SLACK,
    CommittedBuild,
    PlacedBuild,
    placed_build,
)

runner = CliRunner()

_RUN = "20261105T120000Z"
_PROVISIONED = datetime(2026, 11, 5, 12, tzinfo=UTC)


def _pack(rows: int) -> StatPack:
    return StatPack(corpus_rows=rows)


@dataclass
class _History:
    builds: list[CommittedBuild]

    def newest_build(self, bound: datetime) -> CommittedBuild | None:
        candidates = [build for build in self.builds if build.committed_at <= bound]
        return max(candidates, key=lambda build: build.committed_at) if candidates else None

    def build_before(self, build: CommittedBuild) -> CommittedBuild | None:
        earlier = [each for each in self.builds if each.committed_at < build.committed_at]
        return max(earlier, key=lambda each: each.committed_at) if earlier else None

    def lookback_terms_at(self, sha: str) -> int | None:
        return 10


def _history(*landings: tuple[str, datetime, StatPack]) -> _History:
    return _History([CommittedBuild(sha=s, committed_at=t, statpack=p) for s, t, p in landings])


_OLD = ("a" * 40, datetime(2026, 11, 1, tzinfo=UTC), _pack(1))
_NEW = ("b" * 40, datetime(2026, 11, 6, tzinfo=UTC), _pack(2))


def test_a_recorded_digest_names_the_build_in_force() -> None:
    found = placed_build(statpack_digest(_pack(1)), _PROVISIONED, _history(_OLD, _NEW))

    assert isinstance(found, PlacedBuild)
    assert found.build.sha == "a" * 40
    assert found.alternative is None


def test_a_refresh_after_placement_is_never_the_build_read() -> None:
    """The 26A612 case: the pack refreshed after the cell ran; a digest naming
    the refreshed build is refused, not taken as what the predictor saw."""
    found = placed_build(statpack_digest(_pack(2)), _PROVISIONED, _history(_OLD, _NEW))

    assert isinstance(found, str) and "not the build in force" in found


def test_inside_the_checkout_slack_the_digest_picks_between_two_builds() -> None:
    landed = _PROVISIONED - CHECKOUT_SLACK
    history = _history(_OLD, ("b" * 40, landed, _pack(2)))

    replaced = placed_build(statpack_digest(_pack(1)), _PROVISIONED, history)
    in_force = placed_build(statpack_digest(_pack(2)), _PROVISIONED, history)

    assert isinstance(replaced, PlacedBuild) and replaced.build.sha == "a" * 40
    assert isinstance(in_force, PlacedBuild) and in_force.build.sha == "b" * 40


def test_with_no_record_the_bound_names_the_build_and_any_it_cannot_rule_out() -> None:
    history = _history(_OLD, ("b" * 40, _PROVISIONED - timedelta(hours=1), _pack(2)))

    found = placed_build(None, _PROVISIONED, history)

    assert isinstance(found, PlacedBuild)
    assert found.build.sha == "b" * 40
    assert found.alternative is not None and found.alternative.sha == "a" * 40
    outside = placed_build(None, _PROVISIONED, _history(_OLD))
    assert isinstance(outside, PlacedBuild) and outside.alternative is None


def test_no_build_before_the_bound_is_said() -> None:
    found = placed_build(None, _PROVISIONED, _history(_NEW))

    assert isinstance(found, str) and "no committed statpack build" in found


def _git(repo: Path, *args: str, when: str | None = None) -> None:
    env = dict(os.environ)
    if when is not None:
        env |= {"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(
        ["git", "-C", str(repo), *identity, *args], check=True, capture_output=True, env=env
    )


def _repo(tmp_path: Path) -> Path:
    """Two builds on main, each with its rendered companion: one before the cell's
    run id, one refresh after it."""
    repo = tmp_path / "repo"
    (repo / "metrics").mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    for rows, when in ((1, "2026-11-01T00:00:00Z"), (2, "2026-11-06T00:00:00Z")):
        write_json(repo / "metrics" / "statpack.json", _pack(rows))
        (repo / "metrics" / "statpack.md").write_text(f"# Corpus statpack {rows}\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", f"build {rows}", when=when)
    return repo


def _cell(tmp_path: Path, context: PredictionContext | None) -> Path:
    cell = tmp_path / "predictions" / "claude-baseline" / _RUN
    write_json(
        cell / "prediction.json",
        Prediction(
            case_id="scotus/1",
            event_id="evt-application-disposition",
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id=_RUN,
            created_at=_PROVISIONED,
            input_snapshot="record/snapshots/2026-11-05.json",
            granted=0,
            probability=0.2,
            predicted_disposition=Disposition.denied,
            context=context,
        ),
    )
    return cell


def _context(**update: object) -> PredictionContext:
    base = PredictionContext(
        mode="forward",
        snapshot_date=date(2026, 11, 5),
        signals_observable=True,
        distribution_count=0,
    )
    return base.model_copy(update=update)


def test_statpack_at_writes_the_build_the_cell_read_not_the_refresh(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cell = _cell(tmp_path, _context(statpack_digest=statpack_digest(_pack(1))))
    out = tmp_path / "out"

    args = ["statpack-at", str(cell / "prediction.json"), "--repo", str(repo), "--ref", "main"]
    result = runner.invoke(app, [*args, "--out-dir", str(out)])

    assert result.exit_code == 0, result.output
    summary = json.loads(result.stdout)
    assert summary["recorded_in"] == "statpack_digest"
    assert summary["run_id_from"] == "directory"
    assert summary["digest"] == statpack_digest(_pack(1))
    assert summary["alternative_sha"] is None
    assert StatPack.model_validate_json((out / "statpack.json").read_text()) == _pack(1)
    assert (out / "statpack.md").read_text() == "# Corpus statpack 1\n"


def test_statpack_at_falls_back_to_a_cert_anchor(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    anchor = CertAnchor(rate=None, statpack_digest=statpack_digest(_pack(1)), lookback_terms=10)
    cell = _cell(tmp_path, _context(cert_anchor=anchor))

    result = runner.invoke(app, ["statpack-at", str(cell), "--repo", str(repo), "--ref", "main"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["recorded_in"] == "cert_anchor"


def test_statpack_at_refuses_a_record_naming_another_build(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cell = _cell(tmp_path, _context(statpack_digest=statpack_digest(_pack(2))))

    result = runner.invoke(app, ["statpack-at", str(cell), "--repo", str(repo), "--ref", "main"])

    assert result.exit_code == 1
    assert "not the build in force" in result.output


def test_statpack_at_on_an_unrecorded_cell_names_the_build_in_force(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    cell = _cell(tmp_path, None)

    result = runner.invoke(app, ["statpack-at", str(cell), "--repo", str(repo), "--ref", "main"])

    assert result.exit_code == 0, result.output
    summary = json.loads(result.stdout)
    assert summary["recorded_in"] is None
    assert summary["digest"] == statpack_digest(_pack(1))


@pytest.mark.parametrize("name", ["not-a-run-id", _RUN])
def test_statpack_at_refuses_an_unreadable_cell(tmp_path: Path, name: str) -> None:
    cell = tmp_path / name
    cell.mkdir()

    result = runner.invoke(app, ["statpack-at", str(cell)])

    assert result.exit_code == 1


def test_statpack_at_reads_a_judges_blinded_copy_by_its_document_run_id(tmp_path: Path) -> None:
    """The evaluate cell stages each candidate under `record/blinded/<alias>/`,
    masked (no engine, no process version): the directory is no run id, so the
    document's own run id bounds the build."""
    repo = _repo(tmp_path)
    cell = _cell(tmp_path, _context(statpack_digest=statpack_digest(_pack(1))))
    masked = json.loads((cell / "prediction.json").read_text())
    masked |= {"predictor_id": "candidate-a", "engine": None, "model": None}
    masked.pop("process_version", None)
    blinded = tmp_path / "record" / "blinded" / "candidate-a"
    blinded.mkdir(parents=True)
    (blinded / "prediction.json").write_text(json.dumps(masked))
    out = tmp_path / "out"

    args = ["statpack-at", str(blinded), "--repo", str(repo), "--ref", "main"]
    result = runner.invoke(app, [*args, "--out-dir", str(out)])

    assert result.exit_code == 0, result.output
    summary = json.loads(result.stdout)
    assert summary["run_id"] == _RUN
    assert summary["run_id_from"] == "document"
    assert summary["digest"] == statpack_digest(_pack(1))
    assert (out / "statpack.md").read_text() == "# Corpus statpack 1\n"


def test_statpack_at_writes_both_builds_where_the_slack_leaves_two(tmp_path: Path) -> None:
    """An unrecorded cell whose run id falls inside the checkout slack after a
    refresh: the judge gets both builds, since either may have been read."""
    repo = _repo(tmp_path)
    late = "20261106T020000Z"  # two hours after the 2026-11-06 refresh landed
    cell = _cell(tmp_path, None)
    moved = cell.parent / late
    cell.rename(moved)
    out = tmp_path / "out"

    args = ["statpack-at", str(moved), "--repo", str(repo), "--ref", "main"]
    result = runner.invoke(app, [*args, "--out-dir", str(out)])

    assert result.exit_code == 0, result.output
    summary = json.loads(result.stdout)
    assert summary["digest"] == statpack_digest(_pack(2))
    assert summary["alternative_sha"] is not None
    assert (out / "statpack.md").read_text() == "# Corpus statpack 2\n"
    assert (out / "alternative" / "statpack.md").read_text() == "# Corpus statpack 1\n"
