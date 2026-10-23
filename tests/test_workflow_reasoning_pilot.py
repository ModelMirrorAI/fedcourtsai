"""run-evaluate's ``reasoning-pilot`` mode: a pilot round that spends and commits nothing.

The pilot of the unregistered ``predicted_reasoning_quality`` grade
(``docs/outcome-decomposition.md``, *The pilot, and what it reports*) rides the
evaluate cell, so it shares the workflow; these tests hold the mode to the
promises its comments make — derived cells, always held, never collected, and
an output job that can reach nothing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "run-evaluate.yml"
SECTION = ".github/prompts/pilot/predicted-reasoning-quality.md"
PILOT = "github.event_name == 'workflow_dispatch' && inputs.mode == 'reasoning-pilot'"


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
    assert inputs["mode"]["options"] == ["backlog", "reasoning-pilot"]
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
    assert job["permissions"] == {"contents": "read", "actions": "read"}
    assert "secrets." not in yaml.safe_dump(job)
    assert "needs.plan.outputs.pilot == 'true'" in job["if"]
    assert "needs.approval.result == 'success'" in job["if"]
    assert "needs.authorize.outputs.attempt == github.run_attempt" in job["if"]
    assert "pilot-report" in workflow["jobs"]["run-gate"]["needs"]
    report = _step(job, "Report the round")["run"]
    assert '--round-id "$ROUND_ID"' in report
    assert f"--prompt {SECTION}" in report
