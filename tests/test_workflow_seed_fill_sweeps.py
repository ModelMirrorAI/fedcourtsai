"""run-seed's three fill sweeps, read back out of the workflow and held to their shape.

The walker's daily window converges three index columns no channel revisits —
the capital-case docket marking, the dated response signals, the merits decision
record — through the same commands run-repair dispatches, in their ``--sweep``
mode: sliced at a per-window cap from ``historical.sweep_caps`` rather than
refused above a maintainer's bound. Nothing at runtime ties the workflow string
to the CLI, the step's posture to its siblings', or a cap in config to a step
that reads it, so these tests do:

* **parity** — each step's argv, executed against the offline fixture corpus,
  still parses (exit 2 is the drift) and, being a sweep, never refuses;
* **posture** — each step is non-blocking and bounded, rides the daily window,
  waits on the dedupe's success, and commits the pointer alone;
* **coverage** — every configured cap has exactly one sweep step reading it.

The sweeps' own semantics (the slice, the ledger line, convergence across
windows) are pinned at their unit seams: `tests/test_docket_marking_migration.py`,
`tests/test_response_backfill.py` and `tests/test_decision_record.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from fedcourtsai.config import SweepCapsConfig, load_historical_config
from tests.workflow_argv import command_argv

ROOT = Path(__file__).resolve().parent.parent
RUN_SEED = ROOT / ".github" / "workflows" / "run-seed.yml"
FEDCOURTS = ("uv", "run", "fedcourts")
DAILY = "github.event.schedule == '31 2 * * *'"

#: Each fill sweep's step, the command it runs, and the cap it slices at.
FILL_SWEEPS: tuple[tuple[str, str, str], ...] = (
    ("Converge stored docket markings", "normalize-docket-markings", "docket_markings"),
    ("Backfill the dated response signals", "backfill-response-fields", "response_fills"),
    ("Fill the merits decision record", "backfill-decision-record", "decision_fills"),
)


def _steps() -> list[dict[str, Any]]:
    data = yaml.safe_load(RUN_SEED.read_text())
    steps = data["jobs"]["seed"]["steps"]
    assert isinstance(steps, list)
    return steps


def _step(name: str) -> dict[str, Any]:
    (step,) = [s for s in _steps() if s.get("name") == name]
    assert isinstance(step, dict)
    return step


def _norm(condition: object) -> str:
    return " ".join(str(condition).split())


@pytest.mark.parametrize(("name", "command", "cap"), FILL_SWEEPS)
def test_each_fill_sweep_runs_its_command_in_sweep_mode(name: str, command: str, cap: str) -> None:
    argvs = command_argv(str(_step(name)["run"]), FEDCOURTS)
    sweeps = [argv for argv in argvs if argv and argv[0] == command]
    assert sweeps == [[command, "--sweep", "--apply"]], (
        f"{name}: expected one `{command} --sweep --apply`, found {argvs}"
    )
    # No bound anywhere: the cap is the sweep's only instrument, and the
    # command refuses an invocation carrying both.
    assert not any(arg.startswith("--max-") for argv in argvs for arg in argv)


@pytest.mark.parametrize(("name", "command", "cap"), FILL_SWEEPS)
def test_each_fill_sweeps_argv_still_parses_against_the_cli(
    name: str, command: str, cap: str, tmp_path: Path
) -> None:
    """The step's own argv, executed offline. A sweep never refuses, so exit 0."""
    corpus_root = tmp_path / "corpus"
    fixture.build_fixture_corpus(corpus.corpus_db_path(corpus_root))
    env = {
        "FEDCOURTS_CORPUS_ROOT": str(corpus_root),
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_COURTLISTENER_API_TOKEN": "",
        "FEDCOURTS_CASESTORE_URL": "",
        "FEDCOURTS_CORPUS_BACKEND": "local",
    }
    ran = 0
    for written in command_argv(str(_step(name)["run"]), FEDCOURTS):
        # The blob push reaches the S3 remote; parse its flags without running it.
        argv = [*written, "--help"] if written[0] in {"corpus-push", "corpus-pull"} else written
        result = CliRunner().invoke(app, argv, env=env)
        assert result.exit_code == 0, f"`fedcourts {' '.join(argv)}`\n{result.output}"
        if argv[0] == command:
            assert f"sweep ledger — {command}: would fill" in result.output
            ran += 1
    assert ran == 1


@pytest.mark.parametrize(("name", "command", "cap"), FILL_SWEEPS)
def test_each_fill_sweep_is_non_blocking_bounded_and_daily(
    name: str, command: str, cap: str
) -> None:
    step = _step(name)
    # One failing sweep must neither fail the window nor skip the next one.
    assert step.get("continue-on-error") is True
    # A cap hit cancels the run, the one outcome continue-on-error cannot absorb.
    assert isinstance(step.get("timeout-minutes"), int) and step["timeout-minutes"] <= 10
    condition = _norm(step.get("if"))
    assert DAILY in condition
    # The dedupe prerequisite run-repair gates the same passes on: a dedupe that
    # mutated the blob and failed its push must not have its corpus half
    # published by this step's pointer-only commit.
    assert "steps.dedupe-live-rows.outcome == 'success'" in condition


@pytest.mark.parametrize(("name", "command", "cap"), FILL_SWEEPS)
def test_each_fill_sweep_commits_the_pointer_alone(name: str, command: str, cap: str) -> None:
    """Index-only writes: anything under `data/` is not this step's to publish."""
    body = str(_step(name)["run"])
    assert "git add corpus/corpus.db.ref" in body
    assert "git add data" not in body
    assert "push_with_retry.sh" in body
    # Blob before pointer commit, as everywhere.
    assert body.index("fedcourts corpus-push") < body.index("git commit")
    # The ledger line must outlive the step log.
    assert '| tee -a "$GITHUB_STEP_SUMMARY"' in body


def test_the_fill_sweeps_run_after_the_dedupe_and_before_the_verdict() -> None:
    names = [str(s.get("name")) for s in _steps()]
    dedupe = names.index("Dedupe live-minted duplicate rows")
    verdict = names.index("Produce + publish the corpus validation verdict")
    for name, _, _ in FILL_SWEEPS:
        assert dedupe < names.index(name) < verdict, name


def test_every_configured_cap_has_exactly_one_sweep() -> None:
    """A cap with no step reading it is a knob that does nothing; a step whose
    cap is missing would fail every window on a config load."""
    fields = set(SweepCapsConfig.model_fields)
    caps = {f for f in fields if not f.endswith("_ceiling")}
    assert {cap for _, _, cap in FILL_SWEEPS} == caps
    # And every cap has the refusing ceiling beside it.
    assert {f"{cap}_ceiling" for cap in caps} == fields - caps


def test_the_committed_caps_load() -> None:
    caps = load_historical_config(ROOT / "config").sweep_caps
    for _, _, cap in FILL_SWEEPS:
        assert 1 <= getattr(caps, cap) <= getattr(caps, f"{cap}_ceiling")
