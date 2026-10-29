"""run-repair's pass table: its refusals, and its agreement with the workflow.

The table in `src/fedcourtsai/repair_passes.py` is what the workflow's
credential-free `validate` job runs. These tests pin three things: what the
gate refuses and accepts; that it runs by path under the runner's bare
interpreter, as the job runs it; and that the table and the workflow name the
same passes, in the same jobs, with the same bound flags — so a pass added to
the form and not the table, or routed to a job the table does not name, fails
here rather than at a maintainer's dispatch. The pairing of each refusal with
its step of record is `tests/test_workflow_cell_invariants.py`'s.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from fedcourtsai import repair_passes
from fedcourtsai.repair_passes import PASSES, validate

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "src" / "fedcourtsai" / "repair_passes.py"
RUN_REPAIR = ROOT / ".github" / "workflows" / "run-repair.yml"

CELL = "scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge"


def _workflow() -> dict[Any, Any]:
    data = yaml.safe_load(RUN_REPAIR.read_text())
    assert isinstance(data, dict)
    return data


def _form_options() -> list[str]:
    workflow = _workflow()
    triggers = workflow.get("on") or workflow.get(True)
    assert isinstance(triggers, dict)
    return [str(o) for o in triggers["workflow_dispatch"]["inputs"]["repair"]["options"]]


def _named_passes(condition: str) -> set[str]:
    """The passes an `if:` names, by equality or by allow-list membership."""
    named = set(re.findall(r"inputs\.repair == '([a-z-]+)'", condition))
    for listed in re.findall(r"fromJSON\('(\[[^']+\])'\), inputs\.repair\)", condition):
        named |= set(re.findall(r'"([a-z-]+)"', listed))
    return named


# --- the gate's verdicts ---------------------------------------------------


def test_the_default_names_no_pass_and_is_refused() -> None:
    verdict = validate("none", mode="dry-run")
    assert not verdict.accepted
    assert verdict.errors == (repair_passes.NO_PASS_NAMED,)


def test_an_unknown_pass_is_refused_by_name() -> None:
    verdict = validate("not-a-pass", mode="dry-run")
    assert verdict.errors == (
        "unknown repair pass 'not-a-pass' — the selector and this validation have "
        "drifted apart; correct the workflow.",
    )


def test_a_bounded_pass_dry_runs_without_a_bound_and_applies_only_with_one() -> None:
    assert validate("lost-outcomes", mode="dry-run").accepted
    refused = validate("lost-outcomes", mode="apply")
    assert not refused.accepted
    assert refused.errors[0].startswith("repair=lost-outcomes with repair_mode=apply needs")
    assert validate("lost-outcomes", mode="apply", bound="12").accepted
    for malformed in ("0", "-5", "01", "1e3", " 3", "3\n"):
        assert not validate("lost-outcomes", mode="apply", bound=malformed).accepted


def test_a_pass_that_spends_its_bound_on_a_dry_run_checks_it_in_both_modes() -> None:
    assert validate("document-backfill", mode="dry-run").accepted
    refused = validate("document-backfill", mode="dry-run", bound="-5")
    assert "reads repair_bound in BOTH modes" in refused.errors[0]
    # A pass whose dry run reads no bound refuses the same number only on apply.
    assert validate("lost-outcomes", mode="dry-run", bound="-5").accepted


def test_a_field_the_pass_does_not_read_is_refused_not_ignored() -> None:
    bound = validate("qp-backfill", mode="dry-run", bound="3")
    assert "takes no repair_bound" in bound.errors[0]
    target = validate("lost-outcomes", mode="dry-run", target="24")
    assert "takes no repair_target" in target.errors[0]


def test_the_option_list_names_every_unknown_token_then_refuses_the_whole_list() -> None:
    verdict = validate("recut", mode="dry-run", options="all-live, bogus,\tworse")
    assert verdict.errors == (
        "repair=recut does not accept the option 'bogus' — it accepts: all-live.",
        "repair=recut does not accept the option 'worse' — it accepts: all-live.",
        repair_passes.OPTION_LIST_REFUSED,
    )
    none_taken = validate("qp-backfill", mode="dry-run", options="all-live")
    assert none_taken.errors[0].endswith("it accepts: none.")
    assert validate("recut", mode="dry-run", options=" all-live ,").accepted


def test_include_scored_states_its_bound_in_every_mode() -> None:
    refused = validate("disposition-convergence", mode="dry-run", options="include-scored")
    assert refused.errors == (repair_passes.INCLUDE_SCORED_NEEDS_BOUND,)
    assert validate(
        "disposition-convergence", mode="dry-run", bound="40", options="include-scored"
    ).accepted


def test_include_failed_attempts_is_announced_and_takes_no_extra_bound() -> None:
    verdict = validate("merits-phantom-removal", mode="dry-run", options="include-failed-attempts")
    assert verdict.accepted
    assert verdict.notices[0].startswith("include-failed-attempts: the removal will include")


@pytest.mark.parametrize(
    ("name", "good", "bad"),
    [
        ("rederive-distribution-parse", "dist-v2", ("", "Dist-v2", "2dist")),
        ("application-backfill", "24", ("", "4", "024", "ot24")),
    ],
)
def test_a_named_subject_is_required_in_both_modes(
    name: str, good: str, bad: tuple[str, ...]
) -> None:
    bound = "1" if PASSES[name].bound_flag else ""
    assert validate(name, mode="dry-run", target=good).accepted
    assert validate(name, mode="apply", bound=bound, target=good).accepted
    for target in bad:
        assert not validate(name, mode="dry-run", target=target).accepted


def test_the_cell_list_names_every_malformed_line_then_refuses_the_whole_list() -> None:
    assert validate("regrade-stale", mode="apply", target=f"{CELL}\n {CELL}\r\n").accepted
    verdict = validate("regrade-stale", mode="dry-run", target=f"{CELL}\nbad/../cell")
    assert verdict.errors == (
        "malformed regrade cell (want court/docket/event/run_id/actor, e.g. "
        "scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge): bad/../cell",
        repair_passes.CELL_LIST_REFUSED,
    )
    assert validate("regrade-stale", mode="dry-run", target=" \n ").errors == (
        repair_passes.NO_CELLS,
    )


def test_a_value_that_spells_a_placeholder_is_printed_as_typed() -> None:
    verdict = validate("qp-backfill", mode="dry-run", options="${line}")
    assert verdict.errors[0] == (
        "repair=qp-backfill does not accept the option '${line}' — it accepts: none."
    )


def test_every_rendered_refusal_comes_from_a_registered_template() -> None:
    # A refusal rendered from a string outside REFUSALS would escape the pairing
    # test, which compares only REFUSALS against the steps of record.
    templates = [
        re.compile(
            re.escape(t)
            .replace(re.escape("${REPAIR}"), ".*")
            .replace(re.escape("${option}"), ".*")
            .replace(re.escape("${accepted_options:-none}"), ".*")
            .replace(re.escape("${line}"), ".*")
        )
        for t in repair_passes.REFUSALS
    ]
    probes = [
        validate(name, mode=mode, bound=bound, target=target, options=options)
        for name in ("none", "bogus", *PASSES)
        for mode in ("dry-run", "apply")
        for bound in ("", "1", "-1")
        for target in ("", "24", "dist-v2", CELL, "x y")
        for options in ("", "include-scored", "include-failed-attempts", "bogus")
    ]
    errors = {error for verdict in probes for error in verdict.errors}
    assert errors
    for error in errors:
        assert any(t.fullmatch(error) for t in templates), error


# --- run by path, as the validate job runs it ------------------------------


def test_the_module_imports_only_the_standard_library() -> None:
    imported: set[str] = set()
    for node in ast.walk(ast.parse(MODULE.read_text())):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0 and node.module, "repair_passes.py makes a relative import"
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and getattr(node.func, "id", "") == "__import__":
            pytest.fail("repair_passes.py imports dynamically")
    allowed = set(sys.stdlib_module_names) | {"__future__"}
    assert imported <= allowed, f"non-stdlib imports: {sorted(imported - allowed)}"
    assert "importlib" not in imported


@pytest.mark.parametrize(
    ("env", "code", "expected"),
    [
        (
            {"REPAIR": "recut", "REPAIR_MODE": "dry-run", "REPAIR_OPTIONS": "all-live"},
            0,
            "repair=recut mode=dry-run accepted",
        ),
        (
            {"REPAIR": "recut", "REPAIR_MODE": "apply"},
            1,
            "::error::repair=recut with repair_mode=apply needs repair_bound",
        ),
    ],
)
def test_the_gate_runs_by_path_under_an_isolated_interpreter(
    env: dict[str, str], code: int, expected: str
) -> None:
    blank = dict.fromkeys(
        ("REPAIR", "REPAIR_MODE", "REPAIR_BOUND", "REPAIR_TARGET", "REPAIR_OPTIONS"), ""
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(MODULE)],
        env={"PATH": os.environ.get("PATH", ""), **blank, **env},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == code, result.stderr
    assert expected in result.stdout


def test_the_validate_job_runs_the_table_from_a_checkout_of_it_alone() -> None:
    job = _workflow()["jobs"]["validate"]
    assert job["permissions"] == {"contents": "read"}
    checkout, gate = job["steps"]
    assert checkout["with"]["persist-credentials"] is False
    assert checkout["with"]["sparse-checkout-cone-mode"] is False
    assert checkout["with"]["sparse-checkout"].split() == ["src/fedcourtsai/repair_passes.py"]
    assert gate["run"].strip() == "python3 -I -S src/fedcourtsai/repair_passes.py"
    assert sorted(gate["env"]) == [
        "REPAIR",
        "REPAIR_BOUND",
        "REPAIR_MODE",
        "REPAIR_OPTIONS",
        "REPAIR_TARGET",
    ]


# --- the table agrees with the workflow ------------------------------------


def test_the_table_names_every_pass_the_form_offers_in_its_order() -> None:
    assert _form_options() == ["none", *PASSES]


def test_each_job_runs_exactly_the_passes_the_table_routes_to_it() -> None:
    jobs = _workflow()["jobs"]
    for job_id, job in jobs.items():
        condition = str(job.get("if", ""))
        named = _named_passes(condition)
        if not named:
            assert "inputs.repair" not in re.sub(r"inputs\.repair_[a-z]+", "", condition), (
                f"job {job_id!r} gates on inputs.repair in a form this test cannot read"
            )
            continue
        routed = {name for name, p in PASSES.items() if job_id in p.jobs}
        assert named == routed, (
            f"job {job_id!r} gates on {sorted(named)}, but the pass table routes "
            f"{sorted(routed)} to it"
        )
    for name, p in PASSES.items():
        for job_id in p.jobs:
            assert job_id in jobs, f"{name}: routed to a job run-repair does not have"


def test_each_bound_reaches_the_flag_the_table_names() -> None:
    jobs = _workflow()["jobs"]
    for name, p in PASSES.items():
        if not p.bound_flag:
            continue
        texts = []
        for job_id in p.jobs:
            job = jobs[job_id]
            job_gated = name in _named_passes(str(job.get("if", "")))
            for step in job.get("steps", []):
                step_names = _named_passes(str(step.get("if", "")))
                if (step_names and name in step_names) or (not step_names and job_gated):
                    texts.append(str(step.get("run", "")))
        assert any(
            re.search(re.escape(p.bound_flag) + r'[ =]"?\$\{?REPAIR_BOUND', text) for text in texts
        ), f"{name}: no step of the pass passes repair_bound as {p.bound_flag}"


def test_the_regrade_steps_cell_grammar_is_the_tables() -> None:
    step = next(
        s
        for s in _workflow()["jobs"]["regrade"]["steps"]
        if s.get("name") == "Re-grade named cells"
    )
    (pattern,) = re.findall(r"pattern='([^']+)'", str(step["run"]))
    assert pattern == f"^{repair_passes.REGRADE_CELL.pattern}$"


# --- the corpus job's persist step -----------------------------------------


def _repair_steps() -> list[dict[str, Any]]:
    steps = _workflow()["jobs"]["repair"]["steps"]
    assert isinstance(steps, list)
    return steps


def _pass_step(name: str) -> dict[str, Any]:
    (step,) = [
        s
        for s in _repair_steps()
        if s.get("id") != "reconcile-scope"
        and re.findall(r"inputs\.repair == '([a-z-]+)'", str(s.get("if", ""))) == [name]
        and "uv run fedcourts" in str(s.get("run", ""))
        and not str(s.get("name", "")).startswith(("Install", "Mint", "Configure"))
    ]
    return step


def test_every_corpus_pass_is_persisted_once() -> None:
    corpus = {name for name, p in PASSES.items() if p.jobs == ("repair",)}
    # The split passes whose writer commits from the pass table's record.
    recorded = {name for name, p in PASSES.items() if "documents" in p.jobs}
    assert recorded == {"ocr-recovery", "recut", "document-backfill"}
    assert set(repair_passes.PERSIST) == corpus | recorded
    commit = next(
        s
        for s in _workflow()["jobs"]["documents"]["steps"]
        if s.get("name") == "Commit the documents pointer"
    )
    assert "python3 -I -S src/fedcourtsai/repair_passes.py persist" in commit["run"]
    for name in corpus:
        run = str(_pass_step(name)["run"])
        assert "push_with_retry.sh" not in run and "corpus-push" not in run, (
            f"{name}: its pass step commits its own write, which the pass table's "
            "persist record says the persist step does"
        )


def test_the_persist_step_follows_every_pass_and_precedes_the_verdict() -> None:
    names = [str(s.get("name", "")) for s in _repair_steps()]
    persist = names.index("Persist the pass's write")
    verdict = names.index("Produce + publish the corpus validation verdict")
    assert persist < verdict
    for name in repair_passes.PERSIST:
        if PASSES[name].jobs != ("repair",):
            continue
        assert names.index(str(_pass_step(name)["name"])) < persist, name
    step = _repair_steps()[persist]
    assert step["if"] == "${{ inputs.repair_mode == 'apply' }}"
    assert "python3 -I -S src/fedcourtsai/repair_passes.py persist" in step["run"]
    assert step["timeout-minutes"] == 15
    assert step["env"]["GH_TOKEN"] == "${{ steps.app-token.outputs.token }}"


@pytest.mark.parametrize(
    ("repair", "code", "lines"),
    [
        (
            "lost-outcomes",
            0,
            [
                "pointer+data",
                "repair: record lost ledger outcomes",
                "lost-outcome pointer",
                "No lost outcomes left to record; nothing to persist.",
            ],
        ),
        (
            "document-backfill",
            0,
            [
                "pointer+data",
                "repair: provision missing primary documents",
                "document backfill pointer",
                "Recovered documents are in the content store; the index pointer is unchanged.",
            ],
        ),
        ("regrade-stale", 1, ["::error::repair=regrade-stale has no persist record"]),
    ],
)
def test_the_persist_record_is_read_by_path(repair: str, code: int, lines: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(MODULE), "persist"],
        env={"PATH": os.environ.get("PATH", ""), "REPAIR": repair},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == code, result.stderr
    if code:
        assert result.stdout == ""
        assert result.stderr.startswith(lines[0])
    else:
        assert result.stdout.splitlines() == lines


def test_a_persist_record_is_one_line_per_field() -> None:
    for name, record in repair_passes.PERSIST.items():
        for field in (record.message, record.label, record.unchanged):
            assert field and "\n" not in field and '"' not in field, name
