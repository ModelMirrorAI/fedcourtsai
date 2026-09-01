"""The staging→main promotion gate lives in scripts/promotion-gate.sh, invoked
from two places: the `promote` dispatch workflow (the maintainer's pre-flight
driver) and ci.yml's `promotion-gate` job (the required check on the promotion
PR). These tests lock that shape: both call sites delegate to the one script,
the promote workflow stays credential-minimal (no environment, no secrets,
ambient token only), the CI job is unreachable from anything but the same-repo
staging→main PR, and the freshness matcher's run-title coupling with the
integration-test workflow holds at both ends. The `main-base` merge-routing
jail and dependabot's staging targeting live here too: routing to `main` is
policy these tests keep mechanical.
"""

import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from fedcourtsai import metrics_refresh
from fedcourtsai.finalize import FinalizeRole

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
ACTIONS = ROOT / ".github" / "actions"
GATE_SCRIPT = ROOT / "scripts" / "promotion-gate.sh"

# The branch→environment auto-resolution the integration-test workflow applies
# wherever it consumes the deploy-environment input. YAML anchors do not work
# in workflows, so the expression is duplicated at each site; pinning the one
# literal here is what keeps the sites from drifting apart.
ENV_RESOLUTION = (
    "inputs.deploy-environment != 'auto' && inputs.deploy-environment "
    "|| (github.ref_name == 'main' && 'prod' || github.ref_name)"
)

# Whether a dispatch resolves its own case, pinned whole rather than by parts:
# the conjunction is the contract. Drop the left half and a pinned dispatch
# resolves anyway, overriding the very escape hatch the staging-corpus runbook
# tells a maintainer to use; drop the right and a corpus that cannot answer
# reddens the two scenarios that never read one.
RESOLVE_GATE = (
    'inputs.docket == \'\' && contains(fromJSON(\'["all", "all-offline", '
    '"ranged-reads", "corpus-service", "stub-cascade", "engine-smoke"]\'), '
    "inputs.scenario)"
)

# The two whole-suite scenarios, whose titles carry the bare scenario name
# rather than a `<scenario> / <engine>` pair — the shapes the freshness gate
# accepts as evidence for the whole required set. Duplicated in the run-name
# and the concurrency group for the same reason ENV_RESOLUTION is.
WHOLE_SUITE = "(inputs.scenario == 'all' || inputs.scenario == 'all-offline')"

# The token-spending legs `all-offline` drops, spelled as required-set entries.
SMOKE_ENTRIES = [
    "engine-smoke/claude-code",
    "engine-smoke/codex",
    "engine-smoke/gemini",
]

needs_jq = pytest.mark.skipif(shutil.which("jq") is None, reason="the plan step shells out to jq")


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _steps_text(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in job.get("steps", []))


def test_promote_is_dispatch_only_and_credential_minimal() -> None:
    wf = _load(WORKFLOWS / "promote.yml")
    # yaml parses the `on:` key as boolean True
    assert list(wf[True].keys()) == ["workflow_dispatch"]
    assert wf["permissions"] == {}
    job = wf["jobs"]["promote"]
    # Strictly read-only: the sync push and the promotion PR are both the
    # maintainer's own writes. Any write scope here (or a bound environment,
    # which would put App keys and role ARNs in reach) is a posture change.
    assert job["permissions"] == {
        "contents": "read",
        "actions": "read",
        "issues": "read",
    }
    assert "environment" not in job
    assert "secrets." not in (WORKFLOWS / "promote.yml").read_text()


def test_promote_delegates_both_gates_to_the_script() -> None:
    job = _load(WORKFLOWS / "promote.yml")["jobs"]["promote"]
    text = _steps_text(job)
    assert "scripts/promotion-gate.sh quiesce" in text
    assert "scripts/promotion-gate.sh freshness" in text


def test_the_contexts_stage_stays_out_of_the_automated_gates() -> None:
    """`contexts` reads a ruleset, which needs admin-level access; ci.yml's
    promotion-gate job holds only contents/actions/issues read. Wiring it into
    `all` — or into either automated call site — would turn a 403 on an advisory
    fact into a blocked promotion, so it stays the maintainer's to run."""
    script = GATE_SCRIPT.read_text()
    assert "contexts)" in script, "the stage exists"
    all_stage = script.split("  all)", 1)[1].split(";;", 1)[0]
    assert "contexts" not in all_stage
    for workflow in ("promote.yml", "ci.yml"):
        assert "promotion-gate.sh contexts" not in (WORKFLOWS / workflow).read_text()


def test_ci_promotion_gate_runs_only_on_the_same_repo_promotion_pr() -> None:
    job = _load(WORKFLOWS / "ci.yml")["jobs"]["promotion-gate"]
    condition = job["if"]
    assert "github.base_ref == 'main'" in condition
    assert "github.head_ref == 'staging'" in condition
    # A fork branch named `staging` must get the skip, never the gate.
    assert "github.event.pull_request.head.repo.full_name == github.repository" in condition
    assert "scripts/promotion-gate.sh all" in _steps_text(job)
    assert "environment" not in job
    # Freshness must see the PR *head* sha — no integration run ever carries
    # the synthetic merge-commit sha, so github.sha would be vacuously red.
    (gate_step,) = [s for s in job["steps"] if "promotion-gate.sh" in str(s.get("run", ""))]
    assert gate_step["env"]["HEAD_SHA"] == "${{ github.event.pull_request.head.sha }}"


def test_freshness_title_coupling_holds_at_both_ends() -> None:
    # The gate greps integration-test run titles; the workflow's run-name is
    # what produces them. A drift on either side makes freshness pass or fail
    # vacuously, so both literals are pinned here.
    script = GATE_SCRIPT.read_text()
    # Start-anchored: a crafted value embedded mid-title must never satisfy a
    # per-scenario prefix.
    assert 'prefix="^integration-test: ${scenario} / ${engine} @"' in script
    assert 'prefix="^integration-test: ${scenario} /"' in script
    # The whole-suite acceptance: one green `all` run counts for every
    # required scenario. Whole-line (-x) on the one fully-fixed title.
    assert 'grep -Fqx "integration-test: all @ staging"' in script
    # And its narrowed twin, reachable only under the engine-smoke skip.
    assert 'grep -Fqx "integration-test: all-offline @ staging"' in script
    # The end-anchored suffix pins the staging deployment environment on the
    # per-scenario matches (unanchored, `@ staging-anything` would match); the
    # branch filter rejects same-sha runs from any other ref; and a title
    # that somehow preserved a newline is excluded before matching, so it can
    # never split into a fabricated extra line.
    assert 'grep "@ staging$"' in script
    assert '.head_branch == "staging"' in script
    assert '(.display_title | test("\\n")) | not' in script
    run_name = _load(WORKFLOWS / "integration-test.yml")["run-name"]
    assert isinstance(run_name, str)
    # Pinned in full: a whole-suite branch must yield `integration-test:
    # <all|all-offline> @ <env>` — rendering the scenario itself, so the two
    # cannot collapse onto one title — and the single-scenario branch the
    # exact per-scenario shape the gate's prefixes grep for.
    assert run_name == (
        f"integration-test: ${{{{ {WHOLE_SUITE} && inputs.scenario "
        "|| format('{0} / {1}', inputs.scenario, inputs.engine) }}"
        f" @ ${{{{ {ENV_RESOLUTION} }}}}"
    )


def test_every_title_component_is_a_closed_choice_input() -> None:
    # The freshness gate matches display titles, and the run-name renders
    # scenario, engine, and deploy-environment verbatim — so each must be a
    # server-validated `choice` whose options are a fixed vocabulary. A
    # free-text input here would let one green dispatch (the environment-free
    # collect scenario in particular) carry a crafted title that forges
    # freshness evidence.
    inputs = _load(WORKFLOWS / "integration-test.yml")[True]["workflow_dispatch"]["inputs"]
    for name in ("scenario", "engine", "deploy-environment"):
        assert inputs[name]["type"] == "choice", name
    assert inputs["deploy-environment"]["options"] == ["auto", "prod", "staging"]


def test_deploy_environment_resolution_is_identical_at_every_site() -> None:
    # The run-name's environment suffix is what freshness matches, and a job's
    # `environment:` is what the run actually binds; the same one expression
    # must produce all three, or a title could name an environment a job never
    # deployed to — and the plan job could resolve its case out of a different
    # environment's corpus than the legs then read.
    workflow = _load(WORKFLOWS / "integration-test.yml")
    inputs = workflow[True]["workflow_dispatch"]["inputs"]
    assert inputs["deploy-environment"]["default"] == "auto"
    for job in ("plan", "scenario"):
        assert workflow["jobs"][job]["environment"] == f"${{{{ {ENV_RESOLUTION} }}}}", job
    assert f"@ ${{{{ {ENV_RESOLUTION} }}}}" in workflow["run-name"]
    # No fourth consumer: anywhere else reading the raw input would bypass the
    # resolution and see the literal string `auto`.
    body = (WORKFLOWS / "integration-test.yml").read_text()
    assert body.count("inputs.deploy-environment") == 6  # 3 sites x 2 reads each


def _all_matrix_entries() -> list[dict[str, str]]:
    workflow = _load(WORKFLOWS / "integration-test.yml")
    (step,) = [s for s in workflow["jobs"]["plan"]["steps"] if s.get("id") == "plan"]
    body = str(step["run"])
    literal = body.split("matrix='", 1)[1].split("'", 1)[0]
    entries = json.loads(literal)
    assert isinstance(entries, list)
    return entries


def test_the_all_scenario_matrix_is_exactly_the_required_set() -> None:
    # `scenario=all` is freshness evidence for the whole required set, so the
    # legs it runs and the set the gate demands must coincide — a leg missing
    # here would let the gate accept an `all` run that never exercised a
    # required scenario. collect is required evidence too, but it rides its
    # own environment-free job rather than the matrix, so the matrix must
    # cover exactly the required set minus collect — and the whole-suite
    # equivalence then rests on the collect job firing inside an `all` run,
    # asserted here beside the coverage claim it completes.
    entries = _all_matrix_entries()
    as_required = [
        entry["scenario"] + (f"/{entry['engine']}" if entry["scenario"] == "engine-smoke" else "")
        for entry in entries
    ]
    required = _required_scenario_entries()
    assert "collect" in required
    assert sorted(as_required) == sorted(entry for entry in required if entry != "collect")
    assert all(entry["scenario"] != "collect" for entry in entries)
    collect_if = _load(WORKFLOWS / "integration-test.yml")["jobs"]["collect-scenario"]["if"]
    assert "inputs.scenario == 'all'" in collect_if
    # Every leg carries both keys with non-empty values: the engine-smoke
    # steps and their secret ternaries read matrix.engine, and an empty
    # engine would break the CLI install's case-switch and drop every key.
    assert all(set(entry) == {"scenario", "engine"} for entry in entries)
    assert all(entry["scenario"] and entry["engine"] for entry in entries)


def _plan_matrix(scenario: str, tmp_path: Path) -> list[dict[str, str]]:
    """Run the plan step's own shell for one dispatch and read back its matrix."""
    workflow = _load(WORKFLOWS / "integration-test.yml")
    (step,) = [s for s in workflow["jobs"]["plan"]["steps"] if s.get("id") == "plan"]
    script = tmp_path / f"plan-{scenario}.sh"
    script.write_text(str(step["run"]))
    output = tmp_path / f"output-{scenario}"
    output.touch()
    subprocess.run(
        ["bash", str(script)],
        check=True,
        env={
            "PATH": os.environ["PATH"],
            "SCENARIO": scenario,
            "ENGINE": "claude-code",
            "GITHUB_OUTPUT": str(output),
        },
    )
    (line,) = output.read_text().splitlines()
    assert line.startswith("matrix=")
    entries = json.loads(line.removeprefix("matrix="))
    assert isinstance(entries, list)
    return entries


@needs_jq
def test_all_offline_is_the_all_matrix_minus_exactly_the_engine_smokes(tmp_path: Path) -> None:
    # `all-offline` is the promotion gate's required suite with the three
    # token-spending legs removed, and nothing else: a leg quietly dropped
    # alongside them would let a skipped-smoke promotion accept evidence that
    # never exercised a still-required scenario. Run the plan step's real
    # shell for both dispatches rather than re-deriving the filter here.
    full = _plan_matrix("all", tmp_path)
    offline = _plan_matrix("all-offline", tmp_path)
    assert full == _all_matrix_entries()
    assert offline == [entry for entry in full if entry["scenario"] != "engine-smoke"]
    assert len(full) - len(offline) == len(SMOKE_ENTRIES)
    # The collect job is required evidence and costs no tokens, so it rides an
    # `all-offline` run exactly as it rides an `all` one.
    collect_if = _load(WORKFLOWS / "integration-test.yml")["jobs"]["collect-scenario"]["if"]
    assert "inputs.scenario == 'all-offline'" in collect_if
    # A single-scenario dispatch is untouched by the whole-suite branch.
    assert _plan_matrix("qp-topic", tmp_path) == [{"scenario": "qp-topic", "engine": "claude-code"}]


def test_all_offline_is_dispatchable_and_titled_as_a_whole_suite() -> None:
    # The gate accepts an `all-offline` title only if such a run can exist,
    # and only if its title renders bare — the same coupling `all` has.
    workflow = _load(WORKFLOWS / "integration-test.yml")
    options = workflow[True]["workflow_dispatch"]["inputs"]["scenario"]["options"]
    assert "all-offline" in options
    # The plan step's own two couplings, pinned without shelling out so the
    # `all-offline` shape keeps a check on a runner with no jq: both
    # whole-suite scenarios share the one matrix literal, and the only thing
    # separating them is the engine-smoke filter.
    (step,) = [s for s in workflow["jobs"]["plan"]["steps"] if s.get("id") == "plan"]
    body = str(step["run"])
    assert "all | all-offline)" in body
    assert body.count("matrix='") == 1
    assert 'select(.scenario != "engine-smoke")' in body
    assert WHOLE_SUITE in str(workflow["run-name"])
    # And the concurrency group keys on the scenario alone for both, so two
    # dispatches differing only on the meaningless engine input supersede each
    # other instead of racing.
    assert WHOLE_SUITE in str(workflow["concurrency"]["group"])


def _case_step(
    tmp_path: Path,
    *,
    resolve: str,
    docket: str = "",
    court: str = "scotus",
    stub: str = "exit 99",
) -> tuple[subprocess.CompletedProcess[str], str, str, str | None]:
    """Replay the plan job's case step, with `uv` stubbed, and read back its files.

    Returns the completed process, the text of the step's ``$GITHUB_OUTPUT`` and
    ``$GITHUB_STEP_SUMMARY``, and the argv the stubbed `uv` was called with —
    ``None`` when it was never called at all. The default stub fails loudly, so
    a test that does not expect the resolver to run proves it two ways: the
    step still succeeds, and that argv is ``None``.
    """
    workflow = _load(WORKFLOWS / "integration-test.yml")
    (step,) = [s for s in workflow["jobs"]["plan"]["steps"] if s.get("id") == "case"]
    # A fresh subdir per call, so a caller can loop over cases without naming
    # one — and so `uv-argv` below is this call's evidence alone.
    work = Path(tempfile.mkdtemp(dir=tmp_path))
    script = work / "case.sh"
    script.write_text(str(step["run"]))
    bin_dir = work / "bin"
    bin_dir.mkdir()
    argv = work / "uv-argv"
    uv = bin_dir / "uv"
    uv.write_text(f'#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" > "{argv}"\n{stub}\n')
    uv.chmod(0o755)
    output = work / "output"
    output.touch()
    summary = work / "summary"
    summary.touch()
    result = subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True,
        check=False,  # the fail-loud paths are exactly what is under test
        env={
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "RESOLVE_CASE": resolve,
            "COURT": court,
            "DOCKET": docket,
            "RUNNER_TEMP": str(work),
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(summary),
        },
    )
    return (
        result,
        output.read_text(),
        summary.read_text(),
        argv.read_text() if argv.exists() else None,
    )


def test_a_pinned_dispatch_passes_through_without_resolving(tmp_path: Path) -> None:
    # `docket` non-empty is the override — the escape hatch for the split mode,
    # where the resolver refuses by design, and for pointing at one case. The
    # command must not run at all (the stub would exit 99), and the pinned pair
    # must reach the same two outputs the resolved path writes, so the legs
    # below have exactly one place to read from.
    result, output, _, argv = _case_step(tmp_path, resolve="false", docket="73274837")
    assert result.returncode == 0, result.stderr
    assert output.splitlines() == ["court=scotus", "docket=73274837"]
    assert argv is None


def test_a_resolving_dispatch_takes_the_pair_from_the_command(tmp_path: Path) -> None:
    # The resolve path: the command's two stdout lines become the job outputs
    # verbatim, and its stderr diagnostic reaches the summary so a run names
    # the case it ran on whatever else happens.
    stub = (
        "printf 'court=scotus\\ndocket=71234567\\n'\n"
        "printf 'resolved scotus/71234567 (candidate 1): live-polled ...\\n' >&2\n"
    )
    result, output, summary, argv = _case_step(tmp_path, resolve="true", stub=stub)
    assert result.returncode == 0, result.stderr
    assert output.splitlines() == ["court=scotus", "docket=71234567"]
    assert "resolved scotus/71234567" in summary
    # The court input narrows the search rather than naming the case, and the
    # backend is pinned: the query service serves no unresolved-first census,
    # and `ranged` is the one backend needing no pull.
    assert argv is not None
    assert argv.split() == [
        "run",
        "fedcourts",
        "corpus-integration-case",
        "--court",
        "scotus",
        "--corpus-backend",
        "ranged",
    ]


def test_nothing_resolvable_fails_the_plan_with_the_resolver_message(tmp_path: Path) -> None:
    # Fail loud, never fall back to a static case: the plan job carries the
    # whole matrix, so a corpus that cannot answer costs seconds instead of the
    # engine-smoke legs' tokens — and the reason (the command's per-reason
    # tally) has to survive into the run, not just the exit code.
    stub = "printf 'no case in scotus is shaped for the integration suite: ...\\n' >&2\nexit 2\n"
    result, output, summary, _ = _case_step(tmp_path, resolve="true", stub=stub)
    assert result.returncode == 2
    assert output == ""
    assert "no case in scotus is shaped" in summary
    assert "no case in scotus is shaped" in result.stderr


def test_a_resolution_that_is_not_a_court_docket_pair_is_refused(tmp_path: Path) -> None:
    # The two lines are appended straight to $GITHUB_OUTPUT and their values
    # come from corpus rows built out of upstream data, so the step pins their
    # shape rather than trusting them: a third line, or a value that is not a
    # court id and an integer docket, is a bug or a crafted row and neither
    # reaches the outputs.
    malformed = (
        "court=scotus\\ndocket=71234567\\nmatrix=[]\\n",  # a smuggled third output
        # The same, unterminated: a line count counts newlines, so this is the
        # shape a "there are two lines" screen waves through.
        "court=scotus\\ndocket=71234567\\nmatrix=[]",
        "court=scotus\\ndocket=not-a-docket\\n",
        "court=\\ndocket=71234567\\n",
        "docket=71234567\\ncourt=scotus\\n",  # right lines, wrong order
    )
    for stdout in malformed:
        result, output, _, _ = _case_step(tmp_path, resolve="true", stub=f"printf '{stdout}'\n")
        assert result.returncode == 1, stdout
        # Pin the reason, not just the refusal: any other exit-1 path would
        # satisfy the code alone.
        assert "did not emit a court/docket pair" in result.stdout, stdout
        assert output == "", stdout


def test_the_case_resolution_is_skipped_where_no_leg_reads_a_case() -> None:
    # The mcp-sidecar and qp-topic scenarios touch no corpus, and each is
    # required freshness evidence in its own right — a corpus that cannot
    # answer must not redden a dispatch of theirs. So the gate is both
    # conditions: the sentinel AND a scenario some leg of which reads a case.
    workflow = _load(WORKFLOWS / "integration-test.yml")
    job = workflow["jobs"]["plan"]
    # Pinned whole, not by parts: asserting the two halves separately leaves
    # the *conjunction* free, and `||` in its place would resolve a case over
    # the top of a pinned dispatch — the escape hatch, silently gone.
    assert job["env"]["RESOLVE_CASE"] == f"${{{{ {RESOLVE_GATE} }}}}"
    corpus_reading = {
        "all",
        "all-offline",
        "ranged-reads",
        "corpus-service",
        "stub-cascade",
        "engine-smoke",
    }
    for scenario in ("mcp-sidecar", "qp-topic"):
        assert f'"{scenario}"' not in RESOLVE_GATE, scenario
    # Every scenario the workflow offers is either in that set or deliberately
    # out of it: a new one added to the input options and to nothing else would
    # silently dispatch with an empty case.
    options = set(workflow[True]["workflow_dispatch"]["inputs"]["scenario"]["options"])
    assert options == corpus_reading | {"mcp-sidecar", "qp-topic", "collect"}
    # The step itself is unconditional — it is the single producer of the two
    # outputs, and gating it would hand every leg an empty pair on a pinned
    # dispatch, which no leg would notice until its read failed.
    (case_step,) = [step for step in job["steps"] if step.get("id") == "case"]
    assert "if" not in case_step
    # Its prerequisites do ride the gate, so a dispatch that resolves nothing
    # assumes no role and builds no environment either.
    gated = [
        step
        for step in job["steps"]
        if step.get("uses", "").startswith(
            (
                "actions/checkout",
                "./.github/actions/setup-python",
                "aws-actions/configure-aws-credentials",
            )
        )
    ]
    assert len(gated) == 3
    for step in gated:
        assert step["if"] == "${{ env.RESOLVE_CASE == 'true' }}", step


def test_every_leg_reads_the_one_settled_case() -> None:
    # One canonical pair for the whole fan-out: a leg still reading the raw
    # dispatch inputs would ignore the resolution and run on the empty
    # sentinel. The plan job publishes the pair; the scenario job reads only
    # the outputs.
    workflow = _load(WORKFLOWS / "integration-test.yml")
    outputs = workflow["jobs"]["plan"]["outputs"]
    assert outputs["court"] == "${{ steps.case.outputs.court }}"
    assert outputs["docket"] == "${{ steps.case.outputs.docket }}"
    scenario = yaml.safe_dump(workflow["jobs"]["scenario"])
    assert "inputs.court" not in scenario
    assert "inputs.docket" not in scenario
    # Four consuming legs, five steps: ranged-reads, corpus-service, the
    # cascade's provisioning guard and its cell, and engine-smoke.
    assert scenario.count("${{ needs.plan.outputs.court }}") == 5
    assert scenario.count("${{ needs.plan.outputs.docket }}") == 5
    # Every read passes through the environment, never into a shell.
    for step in workflow["jobs"]["scenario"]["steps"]:
        assert "needs.plan.outputs" not in str(step.get("run", ""))
    # And the sentinel is what makes resolution the default.
    assert workflow[True]["workflow_dispatch"]["inputs"]["docket"]["default"] == ""


def test_scenario_steps_key_on_the_matrix_not_the_dispatch_inputs() -> None:
    # The scenario job fans out one leg per planned {scenario, engine} pair;
    # a step condition (or engine env/secret ternary, or a job-level env)
    # still reading the dispatch inputs would run the same steps on every leg
    # of an `all` run — and hand every leg the single-dispatch engine's key.
    # The whole job minus its `if` (the collect partition legitimately reads
    # inputs.scenario there) must be input-free on these two.
    job = _load(WORKFLOWS / "integration-test.yml")["jobs"]["scenario"]
    text = yaml.safe_dump({key: value for key, value in job.items() if key != "if"})
    assert "inputs.scenario" not in text
    assert "inputs.engine" not in text
    assert "matrix.scenario" in text
    assert "matrix.engine" in text


def _required_scenario_entries() -> list[str]:
    script = GATE_SCRIPT.read_text()
    (line,) = [ln for ln in script.splitlines() if ln.startswith("REQUIRED_SCENARIOS=")]
    return line.split(":-", 1)[1].rstrip('}"').split()


def test_required_scenarios_exist_on_the_integration_workflow() -> None:
    # Every scenario — and every engine variant — the gate demands must be
    # dispatchable, or a promotion could never satisfy freshness.
    entries = _required_scenario_entries()
    required = {entry.split("/")[0] for entry in entries}
    engines = {entry.split("/", 1)[1] for entry in entries if "/" in entry}
    inputs = _load(WORKFLOWS / "integration-test.yml")[True]["workflow_dispatch"]["inputs"]
    assert required <= set(inputs["scenario"]["options"])
    assert engines <= set(inputs["engine"]["options"])


def _run_freshness(
    tmp_path: Path, titles: list[str], **env: str
) -> subprocess.CompletedProcess[str]:
    """Run the freshness stage against a canned set of green run titles.

    The stage's only outside call is one `gh api` read of the integration-test
    runs at the sha, so a stub that prints the titles is the whole world it
    needs — which lets the required-set arithmetic be tested as behaviour
    rather than as script text.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    titles_file = tmp_path / "titles.txt"
    titles_file.write_text("".join(f"{title}\n" for title in titles))
    gh = bin_dir / "gh"
    gh.write_text(f"#!/usr/bin/env bash\ncat {shlex.quote(str(titles_file))}\n")
    gh.chmod(0o755)
    return subprocess.run(
        ["bash", str(GATE_SCRIPT), "freshness", "0" * 40],
        capture_output=True,
        text=True,
        check=False,  # an unmet gate exits 1, which is the thing under test
        env={
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "GITHUB_REPOSITORY": "owner/repo",
            **env,
        },
    )


def _missing(result: subprocess.CompletedProcess[str]) -> list[str]:
    """The required entries the run reported as unmet, in the gate's own words."""
    marker = "::error::freshness: no green '"
    return [
        line.split(marker, 1)[1].split("'", 1)[0]
        for line in result.stdout.splitlines()
        if marker in line
    ]


def _per_scenario_titles(entries: list[str]) -> list[str]:
    titles = []
    for entry in entries:
        scenario, _, engine = entry.partition("/")
        titles.append(f"integration-test: {scenario} / {engine or 'claude-code'} @ staging")
    return titles


def test_the_smoke_skip_drops_exactly_the_engine_smoke_entries(tmp_path: Path) -> None:
    # The whole contract of PROMOTION_SKIP_SMOKE: three entries leave the
    # required set and nothing else moves. Per-scenario evidence for the
    # token-free scenarios only, so the smokes are the only thing that can be
    # unmet.
    offline_titles = _per_scenario_titles(
        [entry for entry in _required_scenario_entries() if entry not in SMOKE_ENTRIES]
    )
    strict = _run_freshness(tmp_path, offline_titles)
    assert strict.returncode == 1
    assert _missing(strict) == SMOKE_ENTRIES
    skipped = _run_freshness(tmp_path, offline_titles, PROMOTION_SKIP_SMOKE="1")
    assert skipped.returncode == 0, skipped.stdout
    assert _missing(skipped) == []


def test_the_default_required_set_is_unchanged(tmp_path: Path) -> None:
    # No environment set: every entry the script has always demanded is still
    # demanded, and the whole-suite `all` acceptance still stands alone.
    result = _run_freshness(tmp_path, [])
    assert result.returncode == 1
    assert _missing(result) == _required_scenario_entries()
    assert _run_freshness(tmp_path, ["integration-test: all @ staging"]).returncode == 0
    # An `all-offline` run is NOT whole-suite evidence by default — the lever
    # is what admits it, so a dispatcher choosing the cheaper scenario cannot
    # relax the gate on their own.
    default = _run_freshness(tmp_path, ["integration-test: all-offline @ staging"])
    assert default.returncode == 1
    assert _missing(default) == _required_scenario_entries()


def test_the_skip_accepts_either_whole_suite_run(tmp_path: Path) -> None:
    # The narrowed acceptance, and the strictly larger one: a full `all` run
    # is always sufficient evidence for the smaller requirement.
    for title in ("integration-test: all-offline @ staging", "integration-test: all @ staging"):
        result = _run_freshness(tmp_path, [title], PROMOTION_SKIP_SMOKE="1")
        assert result.returncode == 0, result.stdout
    # A red run is never evidence: the gate reads only titles the API call
    # already filtered to successes, so an unmatched title fails as unmet.
    assert _run_freshness(tmp_path, ["integration-test: qp-topic / claude-code @ prod"]).returncode


def test_the_skip_fails_closed_on_anything_but_one(tmp_path: Path) -> None:
    # promote.yml sets '1' or the empty string, and nothing else may enable
    # the relaxation: a typo, a truthy-looking word, or a stray '0' all leave
    # the gate strict rather than silently dropping the smokes.
    titles = ["integration-test: all-offline @ staging"]
    for value in ("", "0", "true", "yes", "01", " 1"):
        result = _run_freshness(tmp_path, titles, PROMOTION_SKIP_SMOKE=value)
        assert result.returncode == 1, value
        assert _missing(result) == _required_scenario_entries(), value


def test_a_local_narrowing_still_forbids_the_whole_suite_shortcut(tmp_path: Path) -> None:
    # PROMOTION_SCENARIOS is unchanged by the lever: an overridden set may
    # name something outside the `all` matrix, so neither whole-suite title
    # can satisfy it — with or without the skip.
    titles = ["integration-test: all @ staging", "integration-test: all-offline @ staging"]
    for env in ({}, {"PROMOTION_SKIP_SMOKE": "1"}):
        result = _run_freshness(tmp_path, titles, PROMOTION_SCENARIOS="qp-topic", **env)
        assert result.returncode == 1
        assert _missing(result) == ["qp-topic"]
    # And the skip still filters whatever set is in force.
    narrowed = _run_freshness(
        tmp_path,
        _per_scenario_titles(["qp-topic"]),
        PROMOTION_SCENARIOS="qp-topic engine-smoke/codex",
        PROMOTION_SKIP_SMOKE="1",
    )
    assert narrowed.returncode == 0, narrowed.stdout
    # Filtering a smoke-only narrowing down to nothing must refuse, not report
    # a clean gate: an empty required set makes freshness a loop over nothing.
    empty = _run_freshness(
        tmp_path,
        [],
        PROMOTION_SCENARIOS="engine-smoke/codex",
        PROMOTION_SKIP_SMOKE="1",
    )
    assert empty.returncode == 2
    assert "would check nothing" in empty.stdout


def test_promote_threads_the_skip_to_the_freshness_step_only() -> None:
    # Two explicit acts stand between a promotion and a smoke-free gate: the
    # dispatch input here, and the `all-offline` scenario the maintainer must
    # have dispatched. The input is a boolean defaulting to false, and the
    # expression is a truthiness test — an absent inputs context yields '',
    # never the enabling value.
    workflow = _load(WORKFLOWS / "promote.yml")
    skip = workflow[True]["workflow_dispatch"]["inputs"]["skip_engine_smoke"]
    assert skip["type"] == "boolean"
    assert skip["default"] is False
    steps = workflow["jobs"]["promote"]["steps"]
    carriers = [s for s in steps if "PROMOTION_SKIP_SMOKE" in (s.get("env") or {})]
    assert [s["name"] for s in carriers] == ["Freshness gate at the staging head"]
    assert carriers[0]["env"]["PROMOTION_SKIP_SMOKE"] == (
        "${{ inputs.skip_engine_smoke && '1' || '' }}"
    )


def test_no_workflow_ever_overrides_the_required_set() -> None:
    # PROMOTION_SCENARIOS is a local re-check narrowing and must never be set
    # on any automated surface. PROMOTION_SKIP_SMOKE is the one sanctioned
    # workflow-side relaxation, with exactly two setters: the promote dispatch
    # (narrowing one pre-flight) and ci.yml's promotion-gate job (narrowing
    # what one labelled batch merges on). A third surface setting either is
    # what this fails on. Assignments only: naming a variable in a comment is
    # documentation, not a setting.
    surfaces = [
        path
        for pattern in ("*.yml", "*.yaml")
        for path in list(WORKFLOWS.glob(pattern)) + list(ACTIONS.glob(f"*/{pattern}"))
    ]
    assert surfaces
    # A name followed by `:` or `=` is an assignment (a YAML env key, a shell
    # export); the `${` lookbehind lets a `${VAR:-}` read through.
    setter = re.compile(r"(?<!\$\{)\b(PROMOTION_SCENARIOS|PROMOTION_SKIP_SMOKE)\b\s*[:=]")
    found = []
    for path in sorted(surfaces):
        for line in path.read_text().splitlines():
            if line.lstrip().startswith("#"):
                continue
            match = setter.search(line)
            if match is None:
                continue
            found.append((path.name, match.group(1)))
    assert found == [
        ("ci.yml", "PROMOTION_SKIP_SMOKE"),
        ("promote.yml", "PROMOTION_SKIP_SMOKE"),
    ], found


def test_promote_help_text_lists_every_required_scenario() -> None:
    # On a freshness failure promote.yml prints the dispatch commands that
    # would satisfy the gate; if that help text drifts from the script's
    # required set, the maintainer is told to dispatch the wrong runs.
    # The names ride shell for-loops, so pin each name's presence in the step
    # text rather than a fully expanded command line.
    text = _steps_text(_load(WORKFLOWS / "promote.yml")["jobs"]["promote"])
    for entry in _required_scenario_entries():
        for name in entry.split("/", 1):
            assert name in text, f"promote.yml help text is missing {name!r}"
    # The one-shot dispatch leads: a single whole-suite run satisfies the
    # freshness gate, so it is the first command the summary offers, with the
    # per-scenario dispatches kept as the fallback. Which suite it names
    # follows the skip — telling a smoke-free batch to dispatch `all` would
    # spend exactly the tokens the lever exists to save.
    all_command = "gh workflow run integration-test.yml --ref staging -f scenario=${suite}"
    assert all_command in text
    assert text.index(all_command) < text.index("-f scenario=${s}")
    assert "suite=all\n" in text
    assert "suite=all-offline\n" in text
    # The engine-smoke dispatches are printed only while they are required.
    assert '"$suite" = all' in text


def test_main_base_jail_covers_every_legitimate_lane() -> None:
    # Merge routing to main rides this job's allowlist, which must track the
    # real bot lanes mechanically, or a renamed lane's PRs hit the jail.
    job = _load(WORKFLOWS / "ci.yml")["jobs"]["main-base"]
    condition = job["if"]
    assert "github.base_ref == 'main'" in condition
    assert "github.head_ref == 'staging'" in condition
    # The negation is the load-bearing structure: the job runs on everything
    # OUTSIDE the allowlist. Without the `!(` the jail inverts — it would fail
    # exactly the legitimate lanes and wave feature PRs through.
    assert "!(" in condition
    assert condition.index("!(") < condition.index("github.head_ref == 'staging'")
    # Fork heads must never match the allowlist, whatever their branch name —
    # the same-repo conjunct must sit INSIDE the negated group.
    same_repo = "github.event.pull_request.head.repo.full_name == github.repository"
    assert same_repo in condition
    assert condition.index("!(") < condition.index(same_repo)
    for role in FinalizeRole:
        assert f"startsWith(github.head_ref, '{role.value}/run-')" in condition
    # Pin the other end of the prefix coupling: the collect plan builder must
    # still construct branches under `<role>/run-`, or the jail's allowlist
    # silently stops matching what collect actually pushes.
    collect_src = (ROOT / "src" / "fedcourtsai" / "collect.py").read_text()
    assert 'f"{role.value}/run-{run_id}"' in collect_src
    assert "startsWith(github.head_ref, 'cleanup/')" in condition
    assert f"github.head_ref == '{metrics_refresh.REFRESH_BRANCH}'" in condition
    assert f"github.head_ref == '{metrics_refresh.BACKTEST_BRANCH}'" in condition
    assert job["permissions"] == {}
    # The job exists only to fail: when the `if` matches, the PR must not merge.
    assert "exit 1" in _steps_text(job)


def test_dependabot_targets_staging() -> None:
    # Dependency bumps are code/config; without an explicit target-branch
    # dependabot PRs go to main, where the main-base jail would strand them.
    config = _load(ROOT / ".github" / "dependabot.yml")
    for update in config["updates"]:
        assert update.get("target-branch") == "staging", update["package-ecosystem"]


def test_the_gate_checks_the_environment_the_staging_writer_actually_binds() -> None:
    """The gate hard-codes which environment's deployment-branch policy it
    verifies, and the refresh workflow independently declares the environment
    whose trust carries the staging write role. Rename either and the gate
    silently checks a policy on an environment the job no longer deploys to —
    pin both ends to the one name."""
    gate = GATE_SCRIPT.read_text()
    assert "environments/staging/deployment-branch-policies" in gate
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "staging-corpus-refresh.yml").read_text()
    )
    (job,) = workflow["jobs"].values()
    assert job["environment"] == "staging"


WAIVER_LABEL = "promote:skip-engine-smoke"


def _promotion_gate_job() -> dict[str, Any]:
    job = _load(WORKFLOWS / "ci.yml")["jobs"]["promotion-gate"]
    assert isinstance(job, dict)
    return job


def _waiver_step() -> dict[str, Any]:
    return next(s for s in _promotion_gate_job()["steps"] if s.get("id") == "waiver")


def test_the_merge_gate_waiver_is_derived_from_the_label_never_hardcoded() -> None:
    """The maintainer's dial: the promotion PR carries the waiver label, and this
    check drops the engine smokes for that batch. The value must come from the
    label read — a literal `1` here would waive every promotion silently and
    forever, which is the one thing the two-setter rule exists to prevent.
    """
    job = _promotion_gate_job()
    assert job["env"]["WAIVER_LABEL"] == WAIVER_LABEL
    (gate_step,) = [s for s in job["steps"] if "promotion-gate.sh" in str(s.get("run", ""))]
    assert gate_step["env"]["PROMOTION_SKIP_SMOKE"] == "${{ steps.waiver.outputs.skip }}"
    # One literal, in WAIVER_LABEL; everything else reads it by name. A second
    # literal is how the check and its warning start naming different labels.
    # Comments may say it as often as they need to.
    literals = [
        line
        for line in (WORKFLOWS / "ci.yml").read_text().splitlines()
        if WAIVER_LABEL in line and not line.lstrip().startswith("#")
    ]
    assert literals == [f"      WAIVER_LABEL: {WAIVER_LABEL}"], literals


def test_the_waiver_label_is_read_at_check_time_not_from_the_event_payload() -> None:
    """A re-run replays the original `pull_request` payload, so a payload read
    would miss a label added after the gate first failed — the usual sequence.
    Fixing that through the payload would need `labeled`/`unlabeled` on the
    trigger, re-running the whole workflow on every label edit to every PR. The
    API read is what keeps "re-run this check before merging" sufficient.
    """
    run = str(_waiver_step()["run"])
    assert "issues/${PR_NUMBER}/labels" in run
    body = (WORKFLOWS / "ci.yml").read_text()
    assert "pull_request.labels" not in body
    types = _load(WORKFLOWS / "ci.yml")[True]["pull_request"]["types"]
    for stale in ("labeled", "unlabeled"):
        assert stale not in types, "the API read exists so these are not needed"


def test_the_waiver_fails_closed_and_says_so_when_it_fires() -> None:
    """Waiving removes the only real-engine evidence a promotion has, so the
    two things that must never break are: nothing but an exact label waives,
    and a batch that waived is legible as waived from its own run record.
    """
    step = _waiver_step()
    run = str(step["run"])
    # Whole-line match: a label that merely contains this one waives nothing.
    assert "grep -Fqx" in run
    # A failed read must not read as a waiver.
    assert "|| true" in run
    assert 'echo "skip=1"' in run
    # Loud on the PR, and durable in the run record the promotion is audited
    # from.
    assert "::warning::" in run
    assert "$GITHUB_STEP_SUMMARY" in run
    # `issues: read` is what the label read needs; it is already there for
    # quiescence, but dropping it would break this silently.
    assert _promotion_gate_job()["permissions"]["issues"] == "read"


def test_the_gate_script_names_what_the_waiver_dropped(tmp_path: Path) -> None:
    """A waived run must be readable as waived from the gate's own log, without
    reconstructing which surface set the variable."""
    offline = _per_scenario_titles(
        [entry for entry in _required_scenario_entries() if entry not in SMOKE_ENTRIES]
    )
    waived = _run_freshness(tmp_path, offline, PROMOTION_SKIP_SMOKE="1")
    assert waived.returncode == 0, waived.stderr
    assert "engine-smoke waived" in waived.stdout
    for engine in ("claude-code", "codex", "gemini"):
        assert f"engine-smoke/{engine}" in waived.stdout
    # Strict runs stay silent about a waiver that did not happen.
    strict = _run_freshness(tmp_path, offline)
    assert "waived" not in strict.stdout
