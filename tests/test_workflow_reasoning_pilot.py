"""run-evaluate's pilot modes: a pilot round that spends and commits nothing.

The pilot of the unregistered ``predicted_reasoning_quality`` grade
(``docs/outcome-decomposition.md``, *The pilot, and what it reports*) rides the
evaluate cell, so it shares the workflow; these tests hold the mode to the
promises its comments make — derived cells, always held, never collected, and
an output job that can reach nothing. ``reasoning-pilot-merits`` is the same
round over the replay merits calibration cells, whose events come from a merits
back-test's kept forecasts rather than the ledger.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "run-evaluate.yml"
SECTION = ".github/prompts/pilot/predicted-reasoning-quality.md"
PILOT = "github.event_name == 'workflow_dispatch' && startsWith(inputs.mode, 'reasoning-pilot')"
MERITS = "github.event_name == 'workflow_dispatch' && inputs.mode == 'reasoning-pilot-merits'"


def _workflow() -> dict[Any, Any]:
    loaded = yaml.safe_load(WORKFLOW.read_text())
    assert isinstance(loaded, dict)
    return loaded


def _step(job: dict[str, Any], name: str) -> dict[str, Any]:
    step = next(s for s in job["steps"] if s.get("name") == name)
    assert isinstance(step, dict)
    return step


def test_the_mode_is_one_choice_input_defaulting_to_the_backlog() -> None:
    inputs = _workflow()[True]["workflow_dispatch"]["inputs"]
    assert list(inputs) == ["mode"]
    assert inputs["mode"]["type"] == "choice"
    assert inputs["mode"]["options"] == ["backlog", "reasoning-pilot", "reasoning-pilot-merits"]
    assert inputs["mode"]["default"] == "backlog"


def test_pilot_is_read_affirmatively_so_a_schedule_is_never_a_pilot() -> None:
    workflow = _workflow()
    plan = workflow["jobs"]["plan"]
    assert plan["outputs"]["pilot"] == "${{ " + PILOT + " }}"
    assert _step(plan, "Build evaluator x case x event matrix")["env"]["PILOT"] == (
        "${{ " + PILOT + " }}"
    )
    assert PILOT in workflow["concurrency"]["group"]


def test_the_plan_reports_the_cells_it_minted() -> None:
    plan = _workflow()["jobs"]["plan"]
    build = _step(plan, "Build evaluator x case x event matrix")["run"]
    assert "reasoning-pilot-sample pilot-sample" in build
    assert "args=(--body-file pilot-sample/body.md --force)" in build
    assert f"--pilot-section {SECTION}" in build
    report = _step(plan, "Report the plan for approval")["run"]
    assert "mapfile -t args < plan-args.txt" in report
    assert '--run-id "$PLAN_RUN_ID" "${args[@]}"' in report


def test_a_pilot_round_never_auto_releases() -> None:
    hold = _step(_workflow()["jobs"]["plan"], "Decide the hold")
    assert f"!({PILOT})" in hold["if"]


def test_a_pilot_round_is_never_collected() -> None:
    assert "needs.plan.outputs.pilot != 'true'" in _workflow()["jobs"]["collect"]["if"]


def test_every_engine_kickoff_names_the_section_only_on_a_pilot_row() -> None:
    text = WORKFLOW.read_text()
    line = (
        "${{ matrix.pilot_section && format('This is a pilot round: also read {0}, which "
        "amends the evaluate prompt for this round only.', matrix.pilot_section) || '' }}"
    )
    assert text.count(line) == 3


def test_the_report_job_reaches_nothing() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["pilot-report"]
    assert "environment" not in job
    assert job["permissions"] == {"contents": "read"}
    sample = _step(job, "Download the sample")["with"]
    assert sample["artifact-ids"] == "${{ needs.plan.outputs.sample_artifact_id }}"
    assert "name" not in sample
    assert "secrets." not in yaml.safe_dump(job)
    assert "needs.plan.outputs.pilot == 'true'" in job["if"]
    assert "needs.approval.result == 'success'" in job["if"]
    assert "needs.authorize.outputs.attempt == github.run_attempt" in job["if"]
    assert "pilot-report" in workflow["jobs"]["run-gate"]["needs"]
    report = _step(job, "Report the round")["run"]
    assert '--round-id "$ROUND_ID"' in report
    assert f"--prompt {SECTION}" in report


def test_the_merits_pilot_takes_its_source_from_a_reviewed_merits_backtest_run() -> None:
    """Only run-backtest's own successful runs on `main`, at a commit `main` still
    holds, count, and the kept tree is downloaded by id outside the checkout."""
    plan = _workflow()["jobs"]["plan"]
    assert plan["permissions"]["actions"] == "read"
    source = _step(plan, "Find the merits back-test's kept forecasts")
    assert source["if"] == "${{ " + MERITS + " }}"
    run = source["run"]
    for clause in (
        "actions/workflows/run-backtest.yml/runs?branch=main&status=success",
        '.path == \\".github/workflows/run-backtest.yml\\"',
        '.head_branch == \\"main\\"',
        '.head_repository.full_name == \\"${REPO}\\"',
        "(.expired | not)",
        "compare/${sha}...main",
    ):
        assert clause in run, clause
    download = _step(plan, "Download the merits back-test's kept forecasts")["with"]
    assert download["artifact-ids"] == "${{ steps.source.outputs.artifact }}"
    assert download["run-id"] == "${{ steps.source.outputs.run }}"
    assert download["path"] == "${{ runner.temp }}/merits-forecasts"


def test_the_merits_pilot_checks_its_overlay_before_the_matrix_reads_it() -> None:
    plan = _workflow()["jobs"]["plan"]
    build = _step(plan, "Build evaluator x case x event matrix")
    assert build["env"]["MERITS"] == "${{ " + MERITS + " }}"
    run = build["run"]
    sample = run.index("reasoning-pilot-merits-sample")
    assert "--allow-stub" not in run
    copy = run.index('cp -R "$event" "data/$rel"')
    assert sample < run.index('validate "$calibration"') < copy < run.index("--calibration)")
    assert 'if [ -e "data/$rel" ]' in run
    upload = _step(plan, "Upload the merits pilot's calibration events")
    assert upload["with"]["path"] == "${{ runner.temp }}/calibration-data"
    assert plan["outputs"]["calibration_artifact_id"] == (
        "${{ steps.calibration-upload.outputs.artifact-id }}"
    )


def test_a_calibration_cell_lays_in_its_own_event_and_never_projects_it() -> None:
    cell = _workflow()["jobs"]["evaluate"]
    names = [s.get("name") for s in cell["steps"]]
    download = _step(cell, "Download the calibration events")
    assert download["if"] == "${{ matrix.calibration }}"
    assert download["with"]["artifact-ids"] == "${{ needs.plan.outputs.calibration_artifact_id }}"
    lay = _step(cell, "Lay the calibration event into the checkout")
    assert lay["if"] == "${{ matrix.calibration }}"
    assert 'if [ -e "data/$EVENT_DIR" ]' in lay["run"]
    assert names.index("Lay the calibration event into the checkout") < names.index(
        "Stage the blinded candidates"
    )
    materialize = _step(cell, "Materialize the event definition for the ledger")
    assert materialize["if"] == "${{ !matrix.calibration }}"
