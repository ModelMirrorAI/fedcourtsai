"""Structural invariants of the agent-cell workflows that no runtime check sees.

These contracts live only as lines in workflow YAML, so a refactor can drop any
of them while every gate stays green:

* the **qp-topics oracle fence** — `data/qp-topics/` membership encodes cert
  outcomes (docs/qp-topic.md), so every workflow that puts an agent in a repo
  checkout deletes the directory first (the labeler in `run-analytics` instead
  moves it aside and restores from the commit, because its measure step needs
  the reference set back);
* the **corpus-split env pair** — `FEDCOURTS_CORPUS_SPLIT` is inert without
  `FEDCOURTS_CASESTORE_URL`, and both must carry the same repo-variable
  expressions everywhere or one surface reads the blob while another reads the
  content store;
* the **forward leakage guard** — `run-predict`'s provisioning step is the one
  place `--refuse-terminal` defends the forward information set, and it sits
  behind `continue-on-error`, so losing the flag fails nothing at runtime;
* the **labeler transcript capture** — the qp-topic labeler's execution log is
  scanned and published as a short-lived artifact, and every clause of that
  (the scan gate, the retention window, the survive-failure condition, and the
  post-agent checkout the scanner is installed from, since the scan holds the
  engine key) is a YAML attribute nothing else checks.

Each would regress silently: the cell still runs, the artifact still validates,
the integration gate stays green. So the contracts get pinned here instead.
"""

import re
from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

# Every workflow that runs an agent inside a repo checkout deletes the oracle;
# the labeler's divert/restore counterpart is asserted separately below.
QP_FENCED_WORKFLOWS = (
    "run-predict.yml",
    "run-evaluate.yml",
    "run-backtest.yml",
    "integration-test.yml",
)

# The one sanctioned spelling of the corpus-split read-side pair. The `|| '0'`
# fallback keeps the split off wherever the variable is unset.
SPLIT_ENV_EXPRESSIONS = {
    "FEDCOURTS_CASESTORE_URL": "${{ vars.CASESTORE_URL }}",
    "FEDCOURTS_CORPUS_SPLIT": "${{ vars.FEDCOURTS_CORPUS_SPLIT || '0' }}",
}


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _run_blocks(wf: dict[str, Any]) -> list[str]:
    return [
        step["run"]
        for job in wf["jobs"].values()
        for step in job.get("steps", []) or []
        if isinstance(step.get("run"), str)
    ]


def test_every_agent_checkout_deletes_the_qp_topic_oracle() -> None:
    for name in QP_FENCED_WORKFLOWS:
        fences = [
            step
            for job in _load(name)["jobs"].values()
            for step in job.get("steps", []) or []
            if "rm -rf data/qp-topics" in str(step.get("run") or "")
        ]
        assert fences, (
            f"{name}: no step deletes data/qp-topics before its agent runs — "
            "the directory's membership encodes cert outcomes (docs/qp-topic.md)"
        )
        for step in fences:
            # Unconditional by design: a condition that evaluates false
            # re-admits the oracle with every check still green.
            assert "if" not in step, f"{name}: the oracle fence must not carry an `if:`"


def test_the_labeler_diverts_and_restores_the_oracle() -> None:
    """The labeler needs the reference set back for its measure step, so it
    moves the directory aside and restores it from the commit — restoring the
    agent's own bytes would let a labeler grade against a file it wrote."""
    runs = _run_blocks(_load("run-analytics.yml"))
    assert any('mv data/qp-topics "$RUNNER_TEMP/qp-topics-oracle"' in run for run in runs)
    assert any("git checkout -- data/qp-topics" in run for run in runs)


def _env_mappings(name: str) -> list[tuple[str, dict[str, Any]]]:
    """Every ``env:`` mapping in the workflow — workflow-, job-, and step-level."""
    wf = _load(name)
    found: list[tuple[str, dict[str, Any]]] = []
    if isinstance(wf.get("env"), dict):
        found.append((f"{name}: workflow env", wf["env"]))
    for job_id, job in wf["jobs"].items():
        if isinstance(job.get("env"), dict):
            found.append((f"{name}: job {job_id}", job["env"]))
        for step in job.get("steps", []) or []:
            if isinstance(step.get("env"), dict):
                label = step.get("name", step.get("uses", "run step"))
                found.append((f"{name}: job {job_id}, step {label!r}", step["env"]))
    return found


# Every workflow whose reads the corpus-split mode forks: the cell workflows,
# the writer lanes, and the integration scenarios. A workflow leaving this set
# — or a new corpus-reading workflow not joining it — is a deliberate act.
SPLIT_PAIR_WORKFLOWS = {
    "integration-test.yml",
    "run-backtest.yml",
    "run-evaluate.yml",
    "run-predict.yml",
    "run-pull.yml",
    "run-seed.yml",
}


def test_the_corpus_split_pair_travels_together_with_one_spelling() -> None:
    """Any env block naming one of the split pair names both, verbatim — and
    the workflows carrying the pair are exactly the corpus-reading set.

    A block that sets the flag without the URL turns the split on with no
    content store to read; one that sets the URL without the flag silently
    stays on the blob. A respelled expression (a dropped `|| '0'`, a
    different variable) forks the read path between two surfaces that must
    agree — the cell workflows and the integration scenarios certify each
    other only while their env is byte-identical. And a workflow that drops
    the pair entirely defaults the split off for its own reads, so coverage
    is pinned per workflow, not as a count.
    """
    covered: set[str] = set()
    for name in sorted(p.name for p in WORKFLOWS.glob("*.y*ml")):
        for context, env in _env_mappings(name):
            present = {k: env[k] for k in SPLIT_ENV_EXPRESSIONS if k in env}
            if not present:
                continue
            covered.add(name)
            assert present.keys() == SPLIT_ENV_EXPRESSIONS.keys(), (
                f"{context}: sets {sorted(present)} but the corpus-split pair "
                f"must travel together: {sorted(SPLIT_ENV_EXPRESSIONS)}"
            )
            for key, expression in SPLIT_ENV_EXPRESSIONS.items():
                assert env[key] == expression, (
                    f"{context}: {key} must be exactly {expression!r}, got {env[key]!r}"
                )
    assert covered == SPLIT_PAIR_WORKFLOWS, (
        f"corpus-split pair coverage drifted: {sorted(covered ^ SPLIT_PAIR_WORKFLOWS)}"
    )


# The corpus-sidecar composite hydrates full-query bodies server-side, so its
# split configuration rides `with:` inputs rather than env — the same pairing
# rule, one level up.
SIDECAR_INPUT_EXPRESSIONS = {
    "casestore-url": "${{ vars.CASESTORE_URL }}",
    "corpus-split": "${{ vars.FEDCOURTS_CORPUS_SPLIT || '0' }}",
}


def test_sidecar_call_sites_pass_the_split_inputs_together() -> None:
    """A corpus-sidecar call site naming one of the composite's split inputs
    names both, with the canonical expressions — half a wiring hands the
    sidecar a store URL it never consults, or a split flag with no store."""
    for name in sorted(p.name for p in WORKFLOWS.glob("*.y*ml")):
        for job_id, job in _load(name)["jobs"].items():
            for step in job.get("steps", []) or []:
                if not str(step.get("uses", "")).endswith("actions/corpus-sidecar"):
                    continue
                with_block = step.get("with") or {}
                present = {k: with_block[k] for k in SIDECAR_INPUT_EXPRESSIONS if k in with_block}
                if not present:
                    continue
                assert present == SIDECAR_INPUT_EXPRESSIONS, (
                    f"{name}: job {job_id}: corpus-sidecar split inputs must be "
                    f"exactly {SIDECAR_INPUT_EXPRESSIONS}, got {present}"
                )


def _provision_lines(name: str) -> list[str]:
    """Every provision-snapshot invocation, with shell continuations joined so
    a cosmetic re-wrap cannot split a flag off its command, and shell comments
    skipped so prose mentioning the command is not scanned as one."""
    return [
        line
        for run in _run_blocks(_load(name))
        for line in run.replace("\\\n", " ").splitlines()
        if "provision-snapshot" in line and not line.lstrip().startswith("#")
    ]


def test_the_forward_cell_provisions_with_the_leakage_guard() -> None:
    """`--refuse-terminal --mode forward --event` is the forward cell's only
    leakage guard, and its step is `continue-on-error`, so a dropped flag
    fails nothing at runtime — a decided event's outcome would simply be
    handed to a "forward" predictor."""
    lines = _provision_lines("run-predict.yml")
    assert lines, "run-predict.yml no longer provisions a snapshot"
    for line in lines:
        assert "--refuse-terminal" in line and "--mode forward" in line and "--event" in line, line


def test_the_evaluate_cell_provisions_without_the_forward_guard() -> None:
    # The mirror pin: an evaluator provisions the outcome-bearing record, so
    # refusing terminal events there would break every evaluate cell.
    lines = _provision_lines("run-evaluate.yml")
    assert lines, "run-evaluate.yml no longer provisions a snapshot"
    for line in lines:
        assert "--refuse-terminal" not in line, line


def test_the_forward_refusal_short_circuits_every_agent_step() -> None:
    """A refused forward cell runs no agent at all.

    Provisioning's exit-3 refusal (the record gate, the staleness bound, or the
    textual scan) sets `refused=true`; every step that would spend tokens, hold
    a credential, or write a runner-local config for the agent — the comment
    token mint, the MCP retrieval config, the engine installs and runs, and the
    event materialization — must carry the gate, or a refused cell produces a
    context-less prediction claiming a mode it never had.
    """
    wf = _load("run-predict.yml")
    steps = wf["jobs"]["predict"]["steps"]
    provision = next(s for s in steps if s.get("id") == "provision")
    assert provision.get("continue-on-error") is True
    assert "--max-snapshot-age-days" in provision["run"]  # the staleness bound is armed
    assert 'echo "refused=true"' in provision["run"]
    gated = [
        "Mint agent comment token",
        "Configure agent retrieval (MCP)",
        "Materialize the event definition for the ledger",
        "Predict with Claude Code",
        "Predict with Codex",
        "Install the Gemini CLI",
        "Predict with Gemini",
    ]
    names = [s.get("name") for s in steps]
    for name in gated:
        step = next(s for s in steps if s.get("name") == name)
        assert "steps.provision.outputs.refused != 'true'" in str(step.get("if")), name
    # The gate can only hold for steps that run after provisioning.
    assert all(
        names.index(name) > names.index("Provision the case snapshot from the corpus")
        for name in gated
    )


def test_the_predict_cell_records_retrieval_mode_from_its_context() -> None:
    # The retrieval log's mode comes from the provisioned record where one
    # exists, with the workflow literal as the fallback — one source of truth
    # for the mode, which is what matters wherever a provisioner writes
    # `replay` (a refused cell writes no context and never reaches this step).
    runs = _run_blocks(_load("run-predict.yml"))
    line = next(r for r in runs if "record-retrieval" in r)
    assert "--mode forward --mode-from-context" in line


def test_the_qp_labeler_transcript_is_captured_and_short_lived() -> None:
    """The transcript artifact contract: captured always, scanned first, 1-day.

    The labeler's turn-by-turn transcript is the only record of *how* a
    no-output run failed, and it embeds the QP text the agent read — so it must
    be uploaded on every path the action survives (a gate-refusing run is as
    diagnostic as a no-output one), only after the secret scan passed, and
    under the same shortest-offered retention the qp-texts extract argues for.
    """
    wf = _load("run-analytics.yml")
    steps = wf["jobs"]["qp-topic-label"]["steps"]
    label = next(s for s in steps if "claude-code-action" in str(s.get("uses") or ""))
    assert label.get("id") == "label", "the labeling step needs an id for its outputs"
    scan = next(s for s in steps if s.get("id") == "transcript_scan")
    # A tampered tree is a run that needs diagnosing, and the scanner is
    # installed out of the labeler's reach (asserted below), so the tree's
    # state must not gate the capture: the transcript survives the tampering
    # it is evidence of.
    assert "steps.pristine.outcome" not in scan["if"]
    pristine = next(s for s in steps if s.get("id") == "pristine")
    assert "assert the tree is pristine" in pristine["name"]
    # The assertion must record a real outcome even on a labeler failure: a run
    # that both failed and tampered has to say which, and a skipped step says
    # nothing.
    assert "!cancelled()" in pristine["if"]
    # What the assertion does gate is the *number*. The measure step runs this
    # checkout's `fedcourts qp-topics`, so it must stay on the default
    # `success()` gate — an `if:` of its own would let a rigged tree be
    # measured.
    measure = next(s for s in steps if s.get("id") == "measure")
    assert "if" not in measure, "the measure step must stay on the default success() gate"
    assert steps.index(pristine) < steps.index(measure)
    assert scan.get("continue-on-error") is True  # withhold, never fail the labels result
    assert "scan-diff-for-secrets" in scan["run"]
    assert scan.get("timeout-minutes") == 5  # bounded inside the job's post-agent budget
    assert "--known-secret-env ANTHROPIC_API_KEY" in scan["run"]  # the reachable credential
    # The transcript surface, not the generic one: an execution log's own tool
    # ids are high-entropy by format, so the --extra-file detector suite
    # convicts every real transcript and the artifact only ever publishes
    # empty. --transcript-file keeps containment + the credential shapes.
    assert "--transcript-file" in scan["run"]
    assert "--extra-file" not in scan["run"]
    # The action must run the pre-installed pinned CLI: its own installer
    # skips the package postinstall and the native binary goes missing.
    assert label["with"]["path_to_claude_code_executable"] == "${{ steps.claude-cli.outputs.path }}"
    install = next(s for s in steps if s.get("id") == "claude-cli")
    assert "--global @anthropic-ai/claude-code@" in install["run"]
    # The postinstall is the actual fix: --ignore-scripts suppresses the
    # script that places the native binary, so the step must run the pinned
    # package's own installer explicitly.
    assert "install.cjs" in install["run"]
    # Ordered before the label step, or the output resolves empty and the
    # action silently falls back to its own broken installer.
    assert steps.index(install) < steps.index(label)
    # The secret-free property the step's comment claims.
    assert "secrets." not in str(install.get("env") or {})
    # One CLI pin across every workflow that installs it, as the comments ask.
    pins = set()
    for name in ("run-analytics.yml", "run-backtest.yml", "integration-test.yml"):
        text = (WORKFLOWS / name).read_text()
        pins.update(re.findall(r"@anthropic-ai/claude-code@([0-9][\w.\-]*)", text))
    assert len(pins) == 1, f"claude-code CLI pins diverge across workflows: {sorted(pins)}"
    upload = next(s for s in steps if (s.get("with") or {}).get("name") == "qp-label-transcript")
    assert upload["with"]["path"] == "${{ steps.label.outputs.execution_file }}"
    assert upload["with"]["retention-days"] == 1
    assert "!cancelled()" in upload["if"]
    assert "steps.transcript_scan.outcome == 'success'" in upload["if"]


def test_the_qp_transcript_scanner_runs_from_an_install_the_labeler_never_saw() -> None:
    """The scan holds the engine key, so it must import no byte the agent wrote.

    `setup-python-env` installs this project editable, so a workspace `uv run`
    resolves `fedcourtsai` through the checkout and its gitignored venv — both
    written to freely by a labeler running `bypassPermissions`, and the venv
    side is invisible to the tree-pristine assertion, which compares tracked
    files only. The scanner therefore comes from a second checkout taken after
    the agent finished and fetched from GitHub, with its own venv inside it.
    """
    steps = _load("run-analytics.yml")["jobs"]["qp-topic-label"]["steps"]
    label_at = steps.index(next(s for s in steps if s.get("id") == "label"))
    scan = next(s for s in steps if s.get("id") == "transcript_scan")
    scan_at = steps.index(scan)

    src = next(s for s in steps if s.get("id") == "scanner_src")
    assert "actions/checkout@" in src["uses"]
    assert src["with"]["path"] == ".transcript-scanner"
    # Resolved against the remote at this run's own commit — never out of the
    # workspace object store, which the agent rewrites as freely as the tree.
    assert src["with"]["ref"] == "${{ github.sha }}"
    assert src["with"]["persist-credentials"] is False
    # After the agent, or the tree it clones is a tree the agent outlived.
    assert label_at < steps.index(src) < scan_at

    # A `.git` planted at the path would be reused, hooks and all, rather than
    # replaced — so the path is cleared before the clone, and the clone is
    # gated on that having worked: a swallowed `rm` failure is the one case
    # that hands the checkout exactly the `.git` it must not reuse.
    clear = next(s for s in steps if s.get("id") == "scanner_clear")
    assert ".transcript-scanner" in clear["run"]
    assert label_at < steps.index(clear) < steps.index(src)
    assert "steps.scanner_clear.outcome == 'success'" in src["if"]
    # Global and system git config are executable (`core.hooksPath`,
    # `init.templateDir`) and fire during a checkout.
    assert src["env"]["GIT_CONFIG_SYSTEM"] == "/dev/null"
    assert "${{ runner.temp }}" in src["env"]["GIT_CONFIG_GLOBAL"]

    install = next(s for s in steps if s.get("id") == "scanner_install")
    # A package cache the labeler can write reaches the import path as surely
    # as a venv it can write, and so does the interpreter the venv is built on
    # — uv keeps both under the runner user's home by default.
    assert ".transcript-scanner" in install["env"]["UV_CACHE_DIR"]
    assert ".transcript-scanner" in install["env"]["UV_PYTHON_INSTALL_DIR"]
    assert "--managed-python" in install["run"]
    assert "sync --locked" in install["run"]
    assert "steps.scanner_src.outcome == 'success'" in install["if"]
    assert steps.index(src) < steps.index(install) < scan_at
    # `uv` sits where `setup-uv` put it — writable by the runner user without
    # sudo — so the path recorded before the agent ran is not enough on its own.
    assert install["env"]["UV_SHA256"] == "${{ steps.uv-bin.outputs.sha256 }}"
    assert "sha256sum --check" in install["run"]
    # `rm`, `git` and `sha256sum` all come off PATH, and `$GITHUB_PATH` prepends
    # ahead of everything — so the toolchain PATH is pinned to root-owned
    # directories, which puts those three behind the same sudo as the image.
    for step in (clear, src, install):
        assert step["env"]["PATH"].startswith("/usr/local/sbin:")
    # The scan must not run at all without the install: `$SCANNER` is a path
    # inside the workspace, and an ungated step would execute whatever is there.
    assert "steps.scanner_install.outcome == 'success'" in scan["if"]

    # `$GITHUB_ENV` and `$GITHUB_PATH` are appendable from any earlier step,
    # the labeling step's subprocesses included, and the runner applies those
    # writes to every step that follows — so a planted `PYTHONPATH` or
    # `LD_PRELOAD` reaches the one process holding the key regardless of what
    # is on the import path. Both the build and the scan strip them.
    for step in (install, scan):
        assert "unset PYTHONPATH" in step["run"]
        assert "unset LD_PRELOAD" in step["run"]

    # None of the three may fail the run: the artifact is the labels, and a
    # scanner that failed to build leaves the scan its existing fail-closed
    # path — no executable, so the transcript is withheld rather than published.
    for step in (clear, src, install):
        assert step.get("continue-on-error") is True

    # And the scan invokes that install by absolute path. A bare `uv run` here
    # is the whole bug: it resolves the project out of the labeler's workspace.
    # `-E -s` is the exhaustive form of the unset above over the PYTHON* family;
    # `-P` drops the implicit working-directory entry, which `-m` would
    # otherwise put *first* on `sys.path` — and a run step's default working
    # directory is the workspace the labeler wrote to. The working-directory
    # override is the same answer from the other side; neither alone is
    # load-bearing, and dropping either quietly re-opens the import path.
    assert "uv run" not in scan["run"]
    assert '"$SCANNER" -E -s -P -m fedcourtsai.cli scan-diff-for-secrets' in scan["run"]
    assert scan["env"]["SCANNER"].endswith(".transcript-scanner/.venv/bin/python")
    assert scan["working-directory"].endswith("/.transcript-scanner")
    assert "-E -s -P -m fedcourtsai.cli" in install["run"]


def test_the_qp_measure_composite_is_shared_by_the_paid_run_and_the_scenario() -> None:
    """Production and the token-free scenario must invoke the same composite.

    The point of the `qp-topic` integration scenario is that it exercises the
    exact post-label steps the paid labeling run depends on — the no-output
    guard, the publication gate, the publish-and-validate path. That only
    holds while both surfaces call `qp-topic-measure` rather than one of them
    inlining a copy that can drift.
    """
    composite = "./.github/actions/qp-topic-measure"

    label_steps = _load("run-analytics.yml")["jobs"]["qp-topic-label"]["steps"]
    production = [s for s in label_steps if s.get("uses") == composite]
    assert len(production) == 1, "the labeling job must measure through the composite"

    # The paid job must consume the measured block through the composite's
    # declared output, never a path convention that a composite-internal
    # rename would silently break after the model spend.
    assert production[0].get("id") == "measure"
    pr_step = next(s for s in label_steps if s.get("name") == "Open or update the review PR")
    assert pr_step["env"]["MEASURED_FILE"] == "${{ steps.measure.outputs.measured-file }}", (
        "the PR body must read the measured block from the composite's output"
    )
    # And no inlined copy of the measure invocation may reappear beside it
    # (`--labels` marks the command; the job's prose mentions the command name).
    label_runs = [str(s.get("run") or "") for s in label_steps]
    assert not any("--labels" in run for run in label_runs)

    scenario_steps = _load("integration-test.yml")["jobs"]["scenario"]["steps"]
    scenario = [s for s in scenario_steps if s.get("uses") == composite]
    assert len(scenario) == 3, "the scenario drives the composite's three paths"
    # Two failure paths (no output, gate refusal) must be tolerated so the
    # scenario can assert they failed; the faithful pass must not be, so a
    # publish regression fails the leg outright.
    tolerated = [s for s in scenario if s.get("continue-on-error") is True]
    assert len(tolerated) == 2
    untolerated = [s for s in scenario if s.get("continue-on-error") is not True]
    assert untolerated[0]["with"]["labeler"] == "canned/reference"
