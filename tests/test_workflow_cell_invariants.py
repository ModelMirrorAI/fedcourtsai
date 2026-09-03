"""Structural invariants of the agent-cell workflows that no runtime check sees.

These contracts live only as lines in workflow YAML, so a refactor can drop any
of them while every gate stays green:

* the **qp-topics oracle fence** — `data/qp-topics/` membership encodes cert
  outcomes (docs/qp-topic.md), so every workflow that puts an agent in a repo
  checkout deletes the directory first (the labeler in `run-analytics` instead
  moves it aside and restores from the commit, because its measure step needs
  the reference set back);
* the **committed-record bracket** — the evaluate cell hides the committed
  `predictions/`/`evaluations/` trees from its judge and restores them the
  moment the agent stops, and both ends are step *order*: a hide before the
  staging step finds nothing to stage, a hide that never runs grades with every
  predictor name in view, and a late restore meets a consumer of the trees it
  has not put back;
* the **corpus-split env pair** — `FEDCOURTS_CORPUS_SPLIT` is inert without
  `FEDCOURTS_CASESTORE_URL`, and both must carry the same repo-variable
  expressions everywhere or one surface reads the blob while another reads the
  content store;
* the **forward leakage guard** — `run-predict`'s provisioning step is the one
  place `--refuse-terminal` defends the forward information set, and it sits
  behind `continue-on-error`, so losing the flag fails nothing at runtime;
* the **codex MCP wiring** — the live codex cells and the engine-smoke codex
  leg must name the same sidecar URL, write the client config to the same
  file, and pin the same `CODEX_HOME`, or the smoke answers a question about a
  configuration nothing else runs;
* the **codex invocation surface** — the two cell workflows' codex-action
  steps, the permission profile `fedcourtsai.mcp` emits for them to select,
  the npm pins of the same CLI in `run-backtest` and `integration-test`, and
  `CodexRunner.build_command`'s argv are one invocation described in several
  places, held in lockstep only by comments; a drifted member runs codex under
  sandbox or search semantics nothing else uses, and every gate stays green;
* the **codex hang bound** — the codex step's own `timeout-minutes` does not
  conclude a wedged engine, so an arm/disarm pair brackets it with a
  runner-level watchdog that kills the engine well inside the job cap and
  leaves its diagnostics in the cell artifact; the whole guard is step order,
  one deadline, and one artifact path;
* the **labeler transcript capture** — the qp-topic labeler's execution log is
  scanned and published as a short-lived artifact, and every clause of that
  (the scan gate, the retention window, the survive-failure condition, and the
  post-agent checkout the scanner is installed from, since the scan holds the
  engine key) is a YAML attribute nothing else checks;
* the **run-surface retry** — the run-record steps and the handoff writes both
  route their `gh` calls through `scripts/gh_retry.sh`'s `gh_retry`; the steps
  that cannot safely source it carry an inline copy, which only stays a copy
  while something compares the two; and the handoff writes stay fatal on
  exhaustion, since a retry that quietly became tolerated would turn a lost
  round into a green run.

Each would regress silently: the cell still runs, the artifact still validates,
the integration gate stays green. So the contracts get pinned here instead.
"""

import io
import json
import re
import textwrap
import tomllib
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import yaml

from fedcourtsai.agent_feedback import (
    _GH_ATTEMPTS,
    _GH_BACKOFF_SECONDS,
    _GH_TIMEOUT_SECONDS,
)
from fedcourtsai.cli import _echo_text_coverage
from fedcourtsai.mcp import CODEX_CELL_PERMISSION_PROFILE, codex_mcp_config
from fedcourtsai.ops import DAILY_DIGEST_LABEL, WEEKLY_DIGEST_LABEL
from fedcourtsai.pipeline.documents import TextCoverage, TextCoverageCut
from fedcourtsai.pipeline.runner import CodexRunner, RunRequest
from fedcourtsai.registry import load_mcp_servers, load_predictors, resolve_mcp_servers
from fedcourtsai.schemas import UsageRole

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
ACTIONS = REPO_ROOT / ".github" / "actions"
GH_RETRY_SCRIPT = REPO_ROOT / "scripts" / "gh_retry.sh"

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


def test_the_labeler_reaches_exactly_the_qp_io_directory() -> None:
    """The labeler's file access outside the checkout is one granted directory.

    The pinned CLI confines reads and writes to the checkout plus explicit
    `--add-dir` grants, so the extract and the output slot live in a dedicated
    `qp-io` subdirectory of $RUNNER_TEMP and that subdirectory is the one
    grant. Three ways this could rot silently: the grant widens to the bare
    temp directory (which holds the diverted oracle — handing the labeler the
    reference set destroys the measurement), one of the staged paths drifts
    out of the granted directory (the agent is structurally unable to reach
    it and every run fails no-output, the shape run 31894995596 diagnosed),
    or the sandbox's socat dependency drops from the install (no shell
    command can execute at all)."""
    wf = _load("run-analytics.yml")
    steps = wf["jobs"]["qp-topic-label"]["steps"]
    label = next(s for s in steps if "claude-code-action" in str(s.get("uses") or ""))
    args = label["with"]["claude_args"]
    assert "--add-dir ${{ runner.temp }}/qp-io" in args
    # The grant is the subdirectory, never the bare temp dir beside the oracle.
    assert "--add-dir ${{ runner.temp }}\n" not in args + "\n"
    for env_key in ("QP_TEXTS", "LABELS_OUT"):
        assert "${{ runner.temp }}/qp-io/" in label["env"][env_key]
    # The oracle's diversion target sits outside the granted directory.
    oracle = next(s for s in steps if "qp-topics-oracle" in str(s.get("run") or ""))
    assert '"$RUNNER_TEMP/qp-topics-oracle"' in oracle["run"]
    measure = next(s for s in steps if "qp-topic-measure" in str(s.get("uses") or ""))
    assert measure["with"]["labels"] == "${{ runner.temp }}/qp-io/qp-labels.jsonl"
    assert measure["with"]["texts"] == "${{ runner.temp }}/qp-io/qp-texts.json"
    sandbox = next(s for s in steps if "bubblewrap" in str(s.get("run") or ""))
    assert "socat" in sandbox["run"]


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
# the writer lanes, the integration scenarios, and the analysis surface. A
# workflow leaving this set — or a new corpus-reading workflow not joining it —
# is a deliberate act.
# staging-corpus-refresh.yml is deliberately absent: its source is pinned on
# the command line from dedicated production-source variables, so it reads NO
# ambient corpus variable at all — neither half of the pair — and the pinning
# test below holds it to that.
SPLIT_PAIR_WORKFLOWS = {
    "integration-test.yml",
    "run-analytics.yml",
    "run-backtest.yml",
    "run-evaluate.yml",
    "run-predict.yml",
    "run-pull.yml",
    "run-repair.yml",
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


# The four variables the staging runbook's scenario repoint sets on the
# staging environment — the refresh lane must reference NONE of them, or the
# repoint moves the seeder's source with it.
_SCENARIO_REPOINT_VARS = (
    "vars.CORPUS_REMOTE_URL",
    "vars.CASESTORE_URL",
    "vars.FEDCOURTS_CORPUS_SPLIT",
    "vars.FEDCOURTS_CORPUS_POINTER",
)


def test_the_refresh_lane_pins_its_source_out_of_the_scenario_variables() -> None:
    """The refresh lane's source and the scenarios' corpus wiring are disjoint.

    The seeder reads from — and its refusal rail compares against — a source
    pinned on the command line from dedicated production-source variables.
    The staging runbook repoints the scenario variables at the staging pair,
    so a reference to any of them here would have that repoint silently move
    the seeder's source, and the rail with it: the seeder would read the
    staging pair as its own source and refuse every legitimate re-seed. The
    guard is textual on purpose — no expression anywhere in the file, not
    just no env mapping — and the source/destination variables are held
    pairwise distinct so the two halves can never be flipped together.
    """
    text = (WORKFLOWS / "staging-corpus-refresh.yml").read_text(encoding="utf-8")
    for expression in _SCENARIO_REPOINT_VARS:
        assert expression not in text, (
            f"staging-corpus-refresh.yml references {expression}, which the "
            "staging runbook's scenario repoint moves — the refresh lane's "
            "source must come only from its dedicated production-source "
            "variables"
        )
    pinned = {
        "SOURCE_REMOTE": "${{ vars.PROD_CORPUS_REMOTE_URL }}",
        "SOURCE_CASESTORE": "${{ vars.PROD_CASESTORE_URL }}",
        "DEST_REMOTE": "${{ vars.STAGING_CORPUS_REMOTE_URL }}",
        "DEST_CASESTORE": "${{ vars.STAGING_CASESTORE_URL }}",
    }
    seed_steps = [
        step
        for job in _load("staging-corpus-refresh.yml")["jobs"].values()
        for step in job.get("steps", []) or []
        if "corpus-seed-slice" in str(step.get("run", ""))
    ]
    assert len(seed_steps) == 1, "expected exactly one seeding step"
    env = seed_steps[0].get("env") or {}
    for key, expression in pinned.items():
        assert env.get(key) == expression, (
            f"seed step env {key} must be exactly {expression!r}, got {env.get(key)!r}"
        )
    backing = [
        expression.removeprefix("${{ ").removesuffix(" }}") for expression in pinned.values()
    ]
    assert len(set(backing)) == len(backing), (
        f"the source and destination halves must come from four distinct variables, got {backing}"
    )
    run_block = str(seed_steps[0]["run"])
    for flag, variable in (
        ("--source-remote", '"${SOURCE_REMOTE}"'),
        ("--source-casestore", '"${SOURCE_CASESTORE}"'),
    ):
        assert f"{flag} {variable}" in run_block, (
            f"the seed invocation must pass {flag} {variable} — the pin is "
            "only a pin if the command consumes it"
        )
    # The textual guard above is name-based, so also pin the env surfaces
    # exactly: a corpus URL smuggled in under a different name would land in
    # one of these mappings.
    assert set(env) == {
        "DOCKETS",
        "APPLY",
        "SOURCE_REMOTE",
        "SOURCE_CASESTORE",
        "DEST_REMOTE",
        "DEST_CASESTORE",
    }, f"unexpected seed-step env keys: {sorted(env)}"
    job_envs = [
        job["env"]
        for job in _load("staging-corpus-refresh.yml")["jobs"].values()
        if isinstance(job.get("env"), dict)
    ]
    assert job_envs == [{"FEDCOURTS_CORPUS_BACKEND": "ranged"}], (
        f"the refresh job's env must be exactly the backend literal, got {job_envs}"
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


# The out-of-band corpus index pointer, in its one spelling and its one home.
# It is the only corpus variable that REDIRECTS a read — the store URLs say
# where to look, this says which blob to read there — so both halves are
# pinned: the exact expression (no `|| ''`, which would be a no-op an unset
# variable already gives, and no respelling), and the exact set of surfaces
# that may carry it.
POINTER_ENV_EXPRESSION = "${{ vars.FEDCOURTS_CORPUS_POINTER }}"
# The scenario lane alone. The production lanes read the pair the committed
# pointer names, so a pointer reaching run-predict/run-evaluate/the writers
# would repoint a real run's corpus at another blob — hence a pinned set
# rather than a count, exactly as the split pair is pinned above.
POINTER_WORKFLOWS = {"integration-test.yml"}


def test_the_corpus_pointer_is_spelled_once_and_scoped_to_the_scenario_lane() -> None:
    """The pointer override travels in one spelling, on one workflow.

    A copy-paste onto a production lane silently redirects that lane's corpus
    reads to whatever blob the variable names; a respelling forks the read
    path between the job env and the sidecar input, which must agree for the
    sidecar to serve the same pair the in-process reads resolve.
    """
    covered: set[str] = set()
    for name in sorted(p.name for p in WORKFLOWS.glob("*.y*ml")):
        for context, env in _env_mappings(name):
            if "FEDCOURTS_CORPUS_POINTER" not in env:
                continue
            covered.add(name)
            assert env["FEDCOURTS_CORPUS_POINTER"] == POINTER_ENV_EXPRESSION, (
                f"{context}: the corpus pointer must be exactly "
                f"{POINTER_ENV_EXPRESSION!r}, got {env['FEDCOURTS_CORPUS_POINTER']!r}"
            )
    assert covered == POINTER_WORKFLOWS, (
        f"corpus pointer coverage drifted: {sorted(covered ^ POINTER_WORKFLOWS)}"
    )


def test_sidecar_call_sites_pass_the_pointer_with_the_same_spelling() -> None:
    """A sidecar call site's pointer input matches the job env's expression.

    The sidecar is a separate process resolving its own corpus connection, so
    a call site whose pointer disagrees with the job env serves one blob's
    index rows to cells whose in-process reads resolve another's.
    """
    for name in sorted(p.name for p in WORKFLOWS.glob("*.y*ml")):
        for job_id, job in _load(name)["jobs"].items():
            for step in job.get("steps", []) or []:
                if not str(step.get("uses", "")).endswith("actions/corpus-sidecar"):
                    continue
                pointer = (step.get("with") or {}).get("corpus-pointer")
                if pointer is None:
                    continue
                assert pointer == POINTER_ENV_EXPRESSION, (
                    f"{name}: job {job_id}: corpus-sidecar corpus-pointer must be "
                    f"exactly {POINTER_ENV_EXPRESSION!r}, got {pointer!r}"
                )


# The codex cell's MCP wiring, in the one spelling every surface must share.
# The live cells and the engine-smoke codex leg certify each other only while
# these agree: the smoke exists to say what a real codex transcript's MCP
# items look like, and an answer collected under different wiring than the
# cells run is an answer about a configuration nothing else uses. Each half is
# separately silent when it drifts — a config written where the CLI does not
# read it, a port the sidecar does not serve, a server id the manifest does not
# resolve, a home the session rollout does not land in — and the cell still
# runs, still validates, and still reports no MCP calls. The redirect carries a
# second stake now that the same file declares the cell's permission profile:
# written where the CLI does not read it, the codex step names a profile no
# config defines and the cell dies at startup instead of degrading.
CODEX_MCP_HTTP_URL = "--http-url courtlistener=http://127.0.0.1:8378/mcp"
CODEX_MCP_CONFIG_REDIRECT = "> .codex/config.toml"
CODEX_HOME_EXPRESSION = "${{ github.workspace }}/.codex"
CODEX_MCP_WORKFLOWS = ("run-predict.yml", "run-evaluate.yml", "integration-test.yml")


def _joined_run_blocks(name: str) -> list[str]:
    """Every ``run:`` block with whitespace collapsed, so a cosmetic re-wrap
    cannot split a flag off the command it belongs to."""
    return [" ".join(block.split()) for block in _run_blocks(_load(name))]


def test_the_codex_mcp_wiring_agrees_across_the_cells_and_the_smoke() -> None:
    """`mcp-config --engine codex` is invoked identically on both surfaces:
    same sidecar URL and server id, redirected to the file the CLI reads."""
    for name in CODEX_MCP_WORKFLOWS:
        blocks = [b for b in _joined_run_blocks(name) if "mcp-config --engine codex" in b]
        assert blocks, f"{name}: no codex mcp-config invocation found"
        for block in blocks:
            assert CODEX_MCP_HTTP_URL in block, (
                f"{name}: codex mcp-config must name the sidecar as "
                f"{CODEX_MCP_HTTP_URL!r}; a drifted port or server id "
                f"silently falls back to a stdio spawn or fails the step"
            )
            assert CODEX_MCP_CONFIG_REDIRECT in block, (
                f"{name}: codex mcp-config must write {CODEX_MCP_CONFIG_REDIRECT!r} "
                f"— the CODEX_HOME the cell runs under"
            )


# A credential-shaped env name on an `mcp-config` step is the one input that
# changes what the command writes: stdio entries inject token values from the
# emitting process's environment into the generated file, which is the residual
# the localhost sidecar retired. `--http-url` entries carry no token whatever
# the env holds, so this is defence for the day someone drops the flag.
_CREDENTIAL_ENV_NAME = re.compile(r"TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|AUTH", re.IGNORECASE)


def test_no_mcp_config_step_can_inject_a_token_into_the_file_it_writes() -> None:
    """Every `mcp-config` step's env is identifiers only — no credential-shaped
    name, no `secrets.` expression — on the cell workflows and the smoke leg
    alike, so no generated client config can carry a token value."""
    seen: set[str] = set()
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for job_id, job in _load(path.name)["jobs"].items():
            for step in job.get("steps", []) or []:
                run = step.get("run")
                if not isinstance(run, str) or "mcp-config" not in run:
                    continue
                seen.add(path.name)
                context = f"{path.name}: job {job_id}, step {step.get('name')!r}"
                for key, value in (step.get("env") or {}).items():
                    assert not _CREDENTIAL_ENV_NAME.search(key), (
                        f"{context}: credential-shaped env {key!r} on an mcp-config "
                        f"step — a stdio entry would write its value into the "
                        f"generated config file"
                    )
                    assert "secrets." not in str(value), (
                        f"{context}: env {key!r} interpolates a secret into an mcp-config step"
                    )
    assert CODEX_MCP_WORKFLOWS[1] in seen, "the smoke leg must generate its own MCP config"


def test_every_codex_home_is_the_workspace_dir_the_config_is_written_into() -> None:
    """One spelling of ``CODEX_HOME`` everywhere, and the smoke declares it.

    The config lands in ``.codex`` and the session rollout the usage, retrieval,
    and shape captures read lands under it, so a step that omits the variable
    gets the CLI's own default (or, in the local cascade, a temp home named
    after a pid) and every one of those reads misses in silence.
    """
    declared: set[str] = set()
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for context, env in _env_mappings(path.name):
            if "CODEX_HOME" not in env:
                continue
            declared.add(path.name)
            assert env["CODEX_HOME"] == CODEX_HOME_EXPRESSION, (
                f"{context}: CODEX_HOME must be exactly {CODEX_HOME_EXPRESSION!r}, "
                f"got {env['CODEX_HOME']!r}"
            )
    assert CODEX_MCP_WORKFLOWS[1] in declared, (
        "the engine-smoke codex leg must pin CODEX_HOME: unset, the cascade "
        "picks a temp home and neither the MCP config nor the shape "
        "distillation finds what it is looking for"
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


def test_the_evaluate_cell_brackets_its_agent_with_the_committed_record_hide() -> None:
    """The judge's blinding is only as good as the tree beside the staging area.

    `hide-cell-record` takes the committed `predictions/`/`evaluations/` trees
    out of the working tree and `restore-cell-record` puts them back, and both
    ends of that bracket are pure step *order* — nothing at runtime notices a
    hide that moved before the staging step (which reads those predictions), a
    hide that never runs (the judge grades with every predictor name in view and
    the cell still validates), or a restore that landed after a consumer of the
    committed trees. `docs/process-version.md` treats what the harness takes off
    disk as part of the evaluator's information set, so dropping this step would
    silently restore the old one under a freshly blessed digest.
    """
    steps = _load("run-evaluate.yml")["jobs"]["evaluate"]["steps"]
    runs = [str(step.get("run") or "") for step in steps]

    def index(needle: str) -> int:
        found = [i for i, run in enumerate(runs) if needle in run]
        assert len(found) == 1, f"expected exactly one step running {needle!r}, found {found}"
        return found[0]

    stage = index("provision-blinded-predictions")
    hide = index("hide-cell-record")
    restore = index("restore-cell-record")
    # Every step that reads the committed trees after the agent stops: the two
    # captures write *into* `evaluations/`, and the last three read it.
    consumers = [
        index("record-usage"),
        index("record-retrieval"),
        index("unblind-evaluations"),
        index("stamp-cell"),
        index("validate data"),
    ]
    agents = [
        i for i, step in enumerate(steps) if str(step.get("id") or "").startswith("evaluate_")
    ]
    assert len(agents) == 3, "expected the three engine steps"

    assert stage < hide < min(agents), "the hide runs after the staging step, before every agent"
    assert max(agents) < restore < min(consumers), "the restore is the first post-agent step"
    # Unconditional, like the oracle fence beside it: a condition that evaluates
    # false re-admits the committed record with every check still green.
    assert "if" not in steps[hide]
    # The restore, by contrast, must run even behind a failed or timed-out
    # agent, whose cell is still recorded from the committed trees.
    assert steps[restore].get("if") == "${{ !cancelled() }}"
    assert "continue-on-error" not in steps[restore]


def test_the_forward_refusal_short_circuits_every_agent_step() -> None:
    """A refused forward cell runs no agent at all.

    Two outcomes refuse, and each sets `refused=true` on its own step: the
    provisioning gate's exit 3 (the record gate, the staleness bound, or the
    textual scan) and an unprovisioned record — no snapshot in the corpus, or a
    provisioning write that did not land complete, which the `record` step reads
    off disk. Every step that would spend tokens, hold a credential, or write a
    runner-local config for the agent — the comment token mint, the MCP
    retrieval config, the engine installs and runs, and the event
    materialization — must carry *both* halves of the gate, or a refused cell
    produces a context-less prediction claiming a mode it never had.
    """
    wf = _load("run-predict.yml")
    steps = wf["jobs"]["predict"]["steps"]
    provision = next(s for s in steps if s.get("id") == "provision")
    assert provision.get("continue-on-error") is True
    assert "--max-snapshot-age-days" in provision["run"]  # the staleness bound is armed
    assert 'echo "refused=true"' in provision["run"]
    record = next(s for s in steps if s.get("id") == "record")
    assert record.get("continue-on-error") is True
    assert "assert-cell-record" in record["run"]
    assert 'echo "refused=true"' in record["run"]
    # The record check is itself gated on provisioning, and on that half only:
    # a cell the forward gate refused was never provisioned by design, so
    # re-asserting its record would report the refusal as an incomplete write.
    assert record.get("if") == "steps.provision.outputs.refused != 'true'"
    # The watchdog's arm step belongs here too: it guards the codex step's
    # window, so a refused cell — which runs no engine — must not arm a killer
    # over the deterministic steps that follow. Its disarm counterpart is
    # deliberately absent: that one is `always()`, because a cell that armed
    # nothing must still be safe to stand down.
    gated = [
        "Mint agent comment token",
        "Configure agent retrieval (MCP)",
        "Materialize the event definition for the ledger",
        "Predict with Claude Code",
        "Arm the codex watchdog",
        "Predict with Codex",
        "Install the Gemini CLI",
        "Predict with Gemini",
    ]
    names = [s.get("name") for s in steps]
    for name in gated:
        step = next(s for s in steps if s.get("name") == name)
        for half in (
            "steps.provision.outputs.refused != 'true'",
            "steps.record.outputs.refused != 'true'",
        ):
            assert half in str(step.get("if")), (name, half)
    # The gate can only hold for steps that run after both refusal points.
    assert all(
        names.index(name) > names.index("Assert the provisioned record landed") for name in gated
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
    assert src["env"]["GIT_CONFIG_NOSYSTEM"] == "1"
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


def test_the_staging_seed_accepts_the_only_list_shape_its_form_can_produce() -> None:
    """`dockets` is a `string` input, and GitHub renders those as a single-line
    field — so the per-line list the description asks for cannot be typed into
    the dispatch form at all, and a pasted one arrives space-joined. The step
    must therefore split on whitespace, not newlines alone; writing the value
    verbatim hands `corpus-seed-slice` one long "id" and the run dies at the
    grammar check having done nothing.
    """
    workflow = _load("staging-corpus-refresh.yml")
    dockets = workflow[True]["workflow_dispatch"]["inputs"]["dockets"]
    # If this ever becomes a multi-line input type, the split below stops being
    # load-bearing and this test should be revisited rather than deleted.
    assert dockets["type"] == "string"
    # The contract has to admit what the form can actually give.
    assert "spaces work" in dockets["description"]

    step = next(
        s
        for s in workflow["jobs"]["refresh"]["steps"]
        if str(s.get("name", "")).startswith("Seed the staging corpus slice")
    )
    run = str(step["run"])
    # The one pipeline that builds the docket file, comments excluded.
    (build,) = [
        line.strip()
        for line in run.splitlines()
        if "dockets_file" in line and not line.strip().startswith("#") and ">" in line
    ]
    assert r"tr -s ' \t\r' '\n'" in build, "split the docket list on whitespace"
    # `grep -v` exits 1 on an all-blank value, which pipefail would turn into a
    # step failure before the command's own emptiness refusal is reached.
    assert "grep -v" not in build
    assert "sed '/^$/d'" in build


# The retried steps, by the surface they live on. A step sources the shared
# script when it runs after a checkout into a workspace no agent has written
# to; every other one carries an inline copy instead — pinned identical below.
SOURCING_OPS_STEPS = (
    "Collect recent workflow runs",
    "Collect issues wearing a stale fan-out label",
    "Post or update the ops dashboard issue",
    "Escalate a failing data-validation verdict",
)
# `(workflow, job, step name)` for the record-keeping writes that source the
# script: each runs after its own job's checkout, in a workspace no agent has
# touched. Empty on the run surfaces — the fan-outs' own records go to the step
# summary, which needs no API call and so no retry — and kept as a table rather
# than deleted, because the next such write belongs here and the tests below
# already scan whatever it holds.
SOURCING_HANDOFF_STEPS: tuple[tuple[str, str, str], ...] = ()
# The composites, whose `uses: ./.github/actions/...` resolution already proves
# a workspace checkout put `scripts/` on disk.
SOURCING_COMPOSITES = ("run-log-dashboard",)
# `(workflow, job, step name)` for each step that inlines its own copy.
INLINE_GH_RETRY_STEPS = (
    ("run-pull.yml", "pull", "Open the failure run-log issue"),
    ("run-pull.yml", "live", "Open the failure run-log issue"),
    ("run-seed.yml", "guard", "Escalate a cancelled or failed seed walk"),
)
# The find-or-create alarms, where an exhausted listing that reads as an empty
# result opens a second thread for the same broken day.
FIND_OR_CREATE_ALARM_STEPS = (
    ("run-pull.yml", "pull", "Open the failure run-log issue"),
    ("run-pull.yml", "live", "Open the failure run-log issue"),
)
# The writes that decide whether a queued round runs at all: retried, never
# tolerated. An exhausted retry must still fail its step. Empty for the same
# reason `SOURCING_HANDOFF_STEPS` is, and kept for the same reason.
FATAL_HANDOFF_STEPS: tuple[tuple[str, str, str], ...] = ()
# Any `gh` invocation, with the `gh_retry` prefix when it carries one — the
# assertion below is that every match has the prefix. `\b` anchors the prefix so
# a name merely *ending* in `gh_retry` cannot pass as the wrapper, and `\s+`
# absorbs the extra spacing a line continuation leaves once it is joined.
BARE_GH_CALL = re.compile(r"(?:\bgh_retry\s+)?\bgh\s+[a-z-]+")
# Not part of the API surface these steps latch, and safe to leave unwrapped:
# `gh` sub-commands that talk to no server.
LOCAL_GH_SUBCOMMANDS = frozenset({"help", "version"})


def _gh_retry_body(text: str) -> str:
    """Return the `gh_retry` definition inside `text`, dedented to column zero.

    `yaml.safe_load` already strips a block scalar's own indentation, so an
    inline copy arrives at column zero like the script's; the dedent is
    defensive, for a copy that ends up nested inside a shell block. It is the
    only normalization applied — everything else has to match byte for byte.
    """
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "gh_retry() {")
    indent = " " * (len(lines[start]) - len(lines[start].lstrip()))
    # The closing brace at the definition's own indent ends it.
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == f"{indent}}}")
    return textwrap.dedent("\n".join(lines[start : end + 1]))


def _named_step(workflow: str, job: str, name: str) -> dict[str, Any]:
    steps = _load(workflow)["jobs"][job]["steps"]
    (step,) = [s for s in steps if s.get("name") == name]
    assert isinstance(step, dict)
    return step


def _composite_run(name: str) -> str:
    action = yaml.safe_load((ACTIONS / name / "action.yml").read_text())
    (step,) = action["runs"]["steps"]
    return str(step["run"])


def _uncommented(run: str) -> list[str]:
    """The run block's code lines, with `\\`-continuations joined into one line.

    A call split across a continuation is one command, and scanning the raw
    lines would see `gh \\` and `issue list …` as two — neither of which
    matches, so an unwrapped call written that way would pass unnoticed.
    """
    joined = re.sub(r"\\\n\s*", " ", run)
    return [line for line in joined.splitlines() if not line.strip().startswith("#")]


def test_every_inline_gh_retry_copy_matches_the_shared_script() -> None:
    """The steps that cannot source `gh_retry` duplicate it; nothing else notices drift.

    `run-pull`'s failure alarms and `run-seed`'s guard exist precisely to fire
    when the run fell over early, so they cannot `source` a file the checkout
    may never have produced; the `rejected` jobs take no checkout at all,
    because one added to a job whose whole purpose is to close a stranded issue
    is one more way to strand it; and the back-test's report step runs in a
    workspace its own agent cells have had write access to, where sourcing a
    file would run agent-authored shell against the job's token. That leaves
    several hand-maintained copies of
    the retry, and a fix applied to the script alone — a longer timeout, a
    fourth attempt — would silently reach only some of the call sites. Compare
    them here so the divergence fails a test instead of being discovered during
    an outage.
    """
    canonical = _gh_retry_body(GH_RETRY_SCRIPT.read_text())
    # A body that lost its bounds would still "match" every identical copy,
    # so pin the shape the script's header promises as well.
    assert "timeout 30" in canonical
    assert "for attempt in 1 2 3" in canonical
    assert "sleep $((attempt * 5))" in canonical
    # Both annotations go to stderr: on stdout they would be captured into the
    # `num=$(gh_retry …)` command substitutions rather than reaching the log.
    assert canonical.count(">&2") == 2

    for workflow, job, name in INLINE_GH_RETRY_STEPS:
        run = str(_named_step(workflow, job, name)["run"])
        assert _gh_retry_body(run) == canonical, (
            f"{workflow}:{job}:{name} has drifted from scripts/gh_retry.sh"
        )
        # And the copy must say it is one, so the next editor knows to keep it
        # in step rather than "improving" it locally.
        assert "Inline copy of scripts/gh_retry.sh" in run


def test_run_seeds_early_validator_duplicates_every_late_refusal_verbatim() -> None:
    """`Validate dispatch inputs` is a fail-fast copy, not a second opinion.

    run-seed refuses a malformed dispatch twice: once up front, ahead of the
    corpus pull, so a typo costs seconds rather than a walk window on the shared
    corpus-write lock, and again inside the step that acts on the input, which is
    the check of record because a step has to be safe on whatever reaches it.
    The pair only earns that arrangement while it is one refusal in two places —
    the same grammar, the same splitting, the same `::error::` text. Let one copy
    drift and the same mistake reports differently depending on where it was
    caught, which is worse than having caught it once.
    """
    steps = _load("run-seed.yml")["jobs"]["seed"]["steps"]
    (early,) = [s for s in steps if s.get("name") == "Validate dispatch inputs"]
    early_errors = _error_lines(str(early["run"]))
    assert early_errors, "the up-front validator refuses nothing"
    # Every refusal a dispatch-only step can print must be printable up front in
    # exactly the same words. The step's own guards differ — its `if:` already
    # narrows the mode, so a late copy needs no mode conjunct the early one does
    # — but the text a maintainer reads may not.
    #
    # The list is curated rather than derived from "every step that can print an
    # `::error::`", because one other kind of annotation in this lane is
    # correctly absent from the up-front copy and would make a derived list
    # fail: a refusal the early validator does not duplicate because the input
    # is parsed where it is consumed (the `refresh_terms` Term grammar). The
    # walk lane refuses exactly one dispatch input at a distance; the
    # maintenance passes share the idiom on run-repair, pinned by the sibling
    # below.
    for owner in ("Re-serve the named dockets",):
        late_errors = _error_lines(str(_named_step("run-seed.yml", "seed", owner)["run"]))
        assert late_errors, f"{owner}: refuses nothing, so the pairing is vacuous"
        drifted = late_errors - early_errors
        assert not drifted, (
            f"{owner}: refusal text absent from `Validate dispatch inputs` — "
            f"the two copies must stay word-for-word identical: {sorted(drifted)}"
        )


# Every run-repair step that acts on the selector, and the job it lives in. The
# list is curated rather than derived for the reason the run-seed pairing above
# states: a derived list would also sweep in run-time failures that are not
# input refusals (the questions-presented backfill's convergence check). A new
# pass that refuses a selector field belongs here; nothing enforces that but
# this comment.
#
# A step may fail at run time as well as refuse its input — the OCR recovery
# verifies its own write — so each entry carries the substrings of its
# **run-time** failures, which have no up-front copy by construction: nothing in
# a credential-free validation job can know whether a content-store write
# landed. They are named rather than pattern-matched, and each is asserted to
# actually appear, so the exemption cannot outlive the check it exempts.
REPAIR_PASS_STEPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("repair", "Re-derive the distribution counts", ()),
    ("repair", "Converge stored docket markings", ()),
    ("repair", "Backfill the dated response signals", ()),
    ("repair", "Recover scanned petitions by OCR", ("apply did not converge",)),
    ("repair", "Backfill missing primary documents", ("apply did not converge",)),
    ("repair", "Backfill the interim arrival stamps", ()),
    ("repair", "Remove ungranted merits phantoms", ()),
    ("repair", "Converge disposition labels", ()),
    ("repair", "Repair the sampled-frame weights", ()),
    ("regrade", "Re-grade named cells", ()),
)


def test_run_repairs_selector_gate_duplicates_every_pass_refusal_verbatim() -> None:
    """`Validate the repair selector` is a fail-fast copy, not a second opinion.

    run-repair refuses a malformed dispatch twice: once in a credential-free
    job every writer job depends on, so a typo is refused before an App token is
    minted or the corpus-write lock is taken, and again inside the pass that
    acts on the field, which is the check of record because a step has to be
    safe on whatever reaches it. The pair only earns that arrangement while it
    is one refusal in two places — the same grammar, the same splitting, the
    same `::error::` text. Let one copy drift and the same mistake reports
    differently depending on where it was caught, which is worse than having
    caught it once.

    A step's **run-time** failures are held apart (`REPAIR_PASS_STEPS`): they
    report what a write did, which the up-front gate cannot know and must not
    claim to.
    """
    (early,) = [
        s
        for s in _load("run-repair.yml")["jobs"]["validate"]["steps"]
        if s.get("name") == "Validate the repair selector"
    ]
    early_errors = _error_lines(str(early["run"]))
    assert early_errors, "the up-front selector gate refuses nothing"
    for job, owner, runtime in REPAIR_PASS_STEPS:
        late_errors = _error_lines(str(_named_step("run-repair.yml", job, owner)["run"]))
        assert late_errors, f"{owner}: refuses nothing, so the pairing is vacuous"
        for marker in runtime:
            matched = {line for line in late_errors if marker in line}
            assert matched, (
                f"{owner}: no `::error::` line contains {marker!r} — the run-time "
                "failure this entry exempts is gone, so the exemption is stale"
            )
            late_errors -= matched
        assert late_errors, (
            f"{owner}: every refusal it emits is exempted as a run-time failure, "
            "so the pairing covers nothing"
        )
        drifted = late_errors - early_errors
        assert not drifted, (
            f"{owner}: refusal text absent from `Validate the repair selector` — "
            f"the two copies must stay word-for-word identical: {sorted(drifted)}"
        )


def test_every_input_gated_step_on_a_scheduled_workflow_is_fail_closed() -> None:
    """An input comparison in a scheduled workflow must be false on a schedule.

    On a schedule the `inputs` context is empty, so `inputs.<mode> != 'none'`
    compares null against a string and evaluates TRUE — a dispatch-only writer
    step gated on the mode alone would fire on every scheduled window, which is
    precisely what these gates exist to prevent. Two shapes are safe on their
    own and are what this admits: a `github.event_name == 'workflow_dispatch'`
    conjunct, which no schedule satisfies, and a comparison against `''`, which
    a schedule's null equals under the same coercion that makes `!= 'none'`
    dangerous. Everything else is refused.
    """
    checked = 0
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        wf = _load(path.name)
        triggers = wf.get("on") or wf.get(True) or {}
        if "schedule" not in triggers:
            continue
        for job in wf["jobs"].values():
            for step in job.get("steps", []):
                condition = str(step.get("if", ""))
                if "inputs." not in condition:
                    continue
                checked += 1
                fail_closed = (
                    "github.event_name == 'workflow_dispatch'" in condition or "!= ''" in condition
                )
                assert fail_closed, (
                    f"{path.name}: step {step.get('name')!r} gates on an input "
                    "with neither a `github.event_name == 'workflow_dispatch'` "
                    "conjunct nor a comparison against '' — on a schedule the "
                    "empty inputs context can make that comparison TRUE, so the "
                    "step would run on every window"
                )
    assert checked, "no scheduled workflow gates a step on an input; the invariant is vacuous"


def test_every_run_repair_pass_gates_on_an_equality_against_a_declared_pass() -> None:
    """run-repair's pass gates name their pass affirmatively, never by `!=`.

    An affirmative gate — an equality, or an allow-list membership test — is
    false under an empty `inputs` context, so it stays fail-closed if this
    workflow ever grows a trigger that carries no inputs; an inequality is TRUE
    there. That hazard is the scheduled-workflow check's above, headed off here
    by shape rather than by a conjunct that would be tautological on a
    dispatch-only workflow. Pinning each gated value against the declared choice
    options also catches the quieter failure: a gate naming a value the selector
    cannot produce never fires at all, and a dispatch of it looks exactly like a
    converged no-op.

    Job-level `if:` is checked with the steps, and for a second reason: the
    corpus job's gate is what grants a pass the read-write role, `id-token:
    write` and the App token. A deny-list there would hand every future selector
    value the full writer credential set by default.
    """
    wf = _load("run-repair.yml")
    # YAML parses a bare `on:` key to the boolean True, so both spellings are
    # tried before indexing.
    triggers = wf.get("on") or wf.get(True) or {}
    options = set(triggers["workflow_dispatch"]["inputs"]["repair"]["options"])
    gated = 0
    for job in wf["jobs"].values():
        for gate in (job,) if "if" in job else ():
            condition = str(gate["if"])
            if "inputs.repair" not in condition:
                continue
            gated += 1
            assert "inputs.repair !=" not in condition, (
                "a run-repair job gates on `inputs.repair !=` — an inequality is "
                "TRUE under an empty inputs context, and on the corpus job it "
                "would also grant the writer credentials to every pass added "
                "later by default; name the passes affirmatively instead"
            )
            named = set(re.findall(r"[\"']([a-z][a-z-]+)[\"']", condition))
            assert named, "a run-repair job gates on inputs.repair without naming a pass"
            unknown = named - options
            assert not unknown, (
                f"a run-repair job gate names {sorted(unknown)}, which the "
                "`repair` choice cannot produce — the job can never run"
            )
        for step in job.get("steps", []):
            condition = str(step.get("if", ""))
            if "inputs.repair " not in condition:
                continue
            gated += 1
            assert "!= 'none'" not in condition or "inputs.repair !=" not in condition, (
                f"{step.get('name')!r}: gated on `inputs.repair != 'none'` — an "
                "inequality is TRUE under an empty inputs context; name the pass "
                "with `==` instead"
            )
            named = set(re.findall(r"inputs\.repair == '([a-z-]+)'", condition))
            assert named, f"{step.get('name')!r}: gates on inputs.repair without naming a pass"
            unknown = named - options
            assert not unknown, (
                f"{step.get('name')!r}: names {sorted(unknown)}, which the "
                f"`repair` choice cannot produce — the step can never run"
            )
    assert gated, "run-repair carries no selector-gated step; the invariant is vacuous"


# GitHub's documented maximum is 10 `workflow_dispatch` inputs per workflow, and
# the "Run workflow" form is where it bites: inputs past the limit are simply
# unreachable through the UI a maintainer dispatches from. A workflow can still
# be *authored* past it, so nothing but this check stops per-pass inputs from
# accumulating back over the cap one PR at a time.
GITHUB_MAX_DISPATCH_INPUTS = 10


def test_no_workflow_declares_more_dispatch_inputs_than_the_ui_can_render() -> None:
    """Every workflow stays within GitHub's 10-input dispatch cap.

    Past the cap the extra inputs exist in the file and are reachable by API,
    but the "Run workflow" form silently stops rendering them — so a maintainer
    dispatching through the UI cannot set them, and a pass documented as
    dispatch-gated becomes undispatchable without anyone being told. Counted per
    workflow rather than pinned per name so a new workflow inherits the check.
    """
    checked = 0
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        triggers = _load(path.name).get("on") or _load(path.name).get(True) or {}
        dispatch = triggers.get("workflow_dispatch") or {}
        inputs = (dispatch or {}).get("inputs") or {}
        if not inputs:
            continue
        checked += 1
        assert len(inputs) <= GITHUB_MAX_DISPATCH_INPUTS, (
            f"{path.name}: declares {len(inputs)} workflow_dispatch inputs, past "
            f"GitHub's documented maximum of {GITHUB_MAX_DISPATCH_INPUTS} — the "
            "Run workflow form stops rendering the rest, so they cannot be set "
            "from the UI at all. Consolidate them behind a generic selector "
            "rather than adding one input per pass."
        )
    assert checked, "no workflow declares dispatch inputs; the invariant is vacuous"


def _error_lines(run: str) -> set[str]:
    """Every ``::error::`` annotation a block can emit, indentation stripped.

    Compared as a set rather than in order, because the up-front copy carries
    every step's refusals in one script while each step carries only its own.
    """
    return {line.strip() for line in run.splitlines() if "::error::" in line}


def test_the_python_seams_bounds_match_the_shared_script() -> None:
    """The Python-side `gh` seams hold the same three numbers as the script.

    Two Python seams bound their calls themselves, because the commands they
    back are invoked from Python rather than wrapped in shell:
    `agent_feedback.py`'s default runner, whose constants this test compares to
    the script directly, and `authz.py`'s default permission lookup, whose
    constants `test_authz.py` pins equal to `agent_feedback.py`'s — so the pin
    to the script is transitive, and deleting either link breaks the chain.
    The constants say they are kept identical to the script's, which is only
    true while something compares them — the same reason the inline copies
    above are pinned. A longer timeout or a fourth attempt applied on one side
    alone would otherwise leave the surfaces silently disagreeing about how
    long a degraded API is tolerated.
    """
    canonical = _gh_retry_body(GH_RETRY_SCRIPT.read_text())
    assert f"timeout {_GH_TIMEOUT_SECONDS}" in canonical
    assert f"for attempt in {' '.join(str(n) for n in range(1, _GH_ATTEMPTS + 1))}" in canonical
    assert f"sleep $((attempt * {_GH_BACKOFF_SECONDS}))" in canonical


def test_the_agent_free_post_checkout_steps_source_the_shared_script() -> None:
    """Where sourcing is safe, the step uses the file, not another private copy.

    One spelling everywhere, and an absolute one: a relative `source` would
    also work today but would silently depend on the step's working directory
    staying the workspace.
    """
    source_line = 'source "${GITHUB_WORKSPACE}/scripts/gh_retry.sh"'
    ops_steps = _load("run-ops.yml")["jobs"]["ops"]["steps"]
    by_name = {s.get("name"): s for s in ops_steps}
    for name in SOURCING_OPS_STEPS:
        run = str(by_name[name]["run"])
        assert source_line in run, f"run-ops step {name!r} must source the retry"
        assert "gh_retry() {" not in run, f"run-ops step {name!r} must not re-define it"

    for site in SOURCING_HANDOFF_STEPS:
        run = str(_named_step(*site)["run"])
        assert source_line in run, f"{site} must source the retry"
        assert "gh_retry() {" not in run, f"{site} must not re-define it"

    # A composite is reached through `uses: ./.github/actions/...`, and a
    # local action ref resolves relative to the workspace — so the action
    # running at all already proves a default-path checkout put `scripts/`
    # there. That is the same assumption, not an extra one.
    for name in SOURCING_COMPOSITES:
        composite = _composite_run(name)
        assert source_line in composite, f"{name} must source the retry"
        assert "gh_retry() {" not in composite, f"{name} must not re-define it"


def test_no_retried_step_makes_an_unretried_github_api_call() -> None:
    """Every `gh` call in these steps goes through the wrapper.

    Scoped to the run surfaces' record-keeping and handoff writes rather than
    the whole repository: elsewhere — ci.yml's label read, the collect jobs'
    own PR plumbing — a bare `gh` call is fine, and a repo-wide ban would be a
    rule nobody could keep. Here it is the whole point.
    """
    ops_steps = _load("run-ops.yml")["jobs"]["ops"]["steps"]
    by_name = {s.get("name"): s for s in ops_steps}
    blocks = [str(by_name[name]["run"]) for name in SOURCING_OPS_STEPS]
    # `FATAL_HANDOFF_STEPS` is a cross-cut of the other two rather than a third
    # set, so the union is de-duplicated — included anyway, so that a fatal site
    # added there and nowhere else is still scanned.
    sites = list(
        dict.fromkeys(INLINE_GH_RETRY_STEPS + SOURCING_HANDOFF_STEPS + FATAL_HANDOFF_STEPS)
    )
    blocks += [str(_named_step(*site)["run"]) for site in sites]
    blocks += [_composite_run(name) for name in SOURCING_COMPOSITES]

    for block in blocks:
        for line in _uncommented(block):
            for call in BARE_GH_CALL.findall(line):
                if call.split()[-1] in LOCAL_GH_SUBCOMMANDS:
                    continue
                assert call.startswith("gh_retry"), f"unretried GitHub API call: {line.strip()}"


def test_the_handoff_writes_stay_fatal_on_exhaustion() -> None:
    """A retry absorbs a blip; it must never turn a real outage into a pass.

    A write on `FATAL_HANDOFF_STEPS` *is* the work — the record that keeps a
    finished or declined round from reading as a stalled fan-out — so none of
    them may tolerate an exhausted retry: no `continue-on-error` on the step, and
    no `|| true` swallowing the non-zero return the wrapper exists to deliver at
    the end of three attempts. The set is empty while every such record is a step
    summary, which no API call can lose; the assertion stands ready for the next
    one rather than being a rule someone has to remember to reinstate.

    The other half of the invariant is an absence, and it is the load-bearing
    half. No stage may hand work to another by filing a labelled issue:
    run-predict and run-evaluate each derive their own backlog from committed
    state on their own schedule, and nothing keys on `issues: labeled` to receive
    such a handoff anyway (`tests/test_workflow_auth_gate.py` sweeps the trigger
    side). The coupling would come back as a step that *applies* a fan-out label,
    so that is what is asserted absent across every workflow — a mention is fine,
    since run-ops reads those labels to report on them; applying one is the
    coupling. A lost round is then impossible rather than merely fatal.
    """
    for site in FATAL_HANDOFF_STEPS:
        step = _named_step(*site)
        assert "continue-on-error" not in step, f"{site} must fail its job on exhaustion"
        for line in _uncommented(str(step["run"])):
            if "gh_retry gh" in line:
                assert "||" not in line, f"{site} swallows an exhausted retry: {line.strip()}"

    fan_out_labels = ("run:predict", "run:evaluate", "run:pull", "run:backtest")
    # `gh` spells label application four ways; each is a write that would restore
    # a stage-to-stage handoff, and a mention on any other line is a read.
    applying = ("--label", "--add-label", "label create", "labels:")
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line in _uncommented(path.read_text()):
            if not any(label in line for label in fan_out_labels):
                continue
            assert not any(verb in line for verb in applying), (
                f"{path.name} applies a fan-out label: {line.strip()} — nothing triggers "
                "on a label, and each stage derives its own backlog from committed state"
            )


def test_the_list_of_retried_ops_steps_is_complete() -> None:
    """The scope above is a name list, so a *fifth* `gh`-calling step is the hole.

    Adding one to `run-ops` with an unwrapped `gh issue create` in it would pass
    every assertion above simply by not being listed. Invert the question — any
    step in that workflow that talks to `gh` at all must be on the list — so the
    enumeration cannot silently fall behind the workflow. Scoped to the whole
    file rather than the `ops` job, because a second job is exactly the shape a
    new reporting surface takes here, and one scanned job would leave it out.
    """
    calling = {
        str(step.get("name"))
        for job in _load("run-ops.yml")["jobs"].values()
        for step in job.get("steps", [])
        if any(BARE_GH_CALL.search(line) for line in _uncommented(str(step.get("run") or "")))
    }
    assert calling == set(SOURCING_OPS_STEPS)


def test_the_retried_listings_are_captured_before_they_are_filtered() -> None:
    """A retried listing is assigned to a variable, not piped into `jq`.

    Each of these lookups feeds a find-or-create: an empty result reads as "no
    issue yet", which opens a duplicate — or, on the pipeline-runs dashboard,
    restarts its rolling 14-day table from the current window. `pipefail` is
    what keeps a failed listing from reaching that branch, and it is a lot of
    weight for one shell option to carry, so the shape is pinned instead: the
    retried listing lands in a variable, making an exhausted retry the
    assignment's own failure.
    """
    blocks = [str(_named_step(*site)["run"]) for site in FIND_OR_CREATE_ALARM_STEPS]
    blocks.append(_composite_run("run-log-dashboard"))
    for block in blocks:
        assert "listing=$(gh_retry gh issue list" in block
        assert '<<<"$listing"' in block
        # No survivor of the old shape: a `gh` call feeding a pipe directly.
        assert not [
            line for line in _uncommented(block) if "gh_retry gh issue list" in line and "|" in line
        ]

    # The dashboard's body read had the same silent failure and the worst
    # consequence, so it is captured too rather than redirected from a pipe.
    composite = _composite_run("run-log-dashboard")
    assert "body=$(gh_retry gh issue view" in composite
    assert "dashboard-body.md" in composite


# The codex invocation surface, described in six places that certify each
# other only while they agree: the codex-action steps of the two cell
# workflows (the action pin and its `codex-version` / `codex-args` /
# `permission-profile` inputs), the codex-action step of the
# `engine-actions-smoke` scenario — whose entire claim is that the cells' input
# block is still *accepted*, which is worth nothing if the block it sends is
# not the cells' — the permission profile `fedcourtsai.mcp` emits into the
# `$CODEX_HOME/config.toml` those steps select by name, the npm pins of the
# same CLI in run-backtest and the engine smoke, and
# `CodexRunner.build_command`'s argv. Each carries a "keep in lockstep" comment
# and nothing else held them together: a member that drifts runs codex under
# sandbox or web-search semantics nothing else uses — a strictly smaller (or
# larger) information set than the engines it is scored against — and the cell
# still runs, still validates, and stays green.
CODEX_ACTION_CELL_WORKFLOWS = ("run-predict.yml", "run-evaluate.yml")
CODEX_ACTION_SMOKE_WORKFLOW = "integration-test.yml"
CODEX_NPM_PIN_WORKFLOWS = ("run-backtest.yml", "integration-test.yml")
# The inputs that make the invocation what it is. The prompt and the model
# deliberately differ on the smoke leg (a boot probe against a resolved
# default, not a cell against a case); everything that decides how codex runs
# does not.
CODEX_LOCKSTEP_INPUTS = (
    "codex-version",
    "codex-args",
    "permission-profile",
    "safety-strategy",
    "effort",
    "allow-bot-users",
)

# The action path and the bare-CLI path express ONE network posture in two
# dialects, so they cannot be compared for equality.
#
# The constraint: codex-action selects a permission profile — a table in the
# trusted `$CODEX_HOME/config.toml` — and refuses a `sandbox_workspace_write`
# or `sandbox_mode` override in `codex-args` alongside it, so the action-side
# posture is *declarative* and lives in the emitted config file. `CodexRunner`
# drives `codex exec` directly with no action in front of it and no
# `permission-profile` concept to pass; its posture is *imperative*, the legacy
# sandbox flags the CLI still accepts. Neither dialect can be spelled on the
# other surface.
#
# So the two are held together by this mapping instead: each action-side
# profile setting against the runner argv fragment that expresses the same
# grant. It is asserted in BOTH directions — every profile setting must have
# its runner fragment, and every sandbox/network fragment in the runner argv
# must be a setting the profile declares — so neither surface can gain or lose
# a grant the other does not have.
#
# This table is now the only place the runner's sandbox mode is pinned (the
# action's `sandbox:` input it used to be compared against is gone), so editing
# it is a change to what a codex cell may reach, not a test fix. Bring it to
# security review, and dispatch the engine smokes named in docs/testing.md.
CODEX_POSTURE_PARITY: dict[str, tuple[str, ...]] = {
    # `extends = ":workspace"` inherits the built-in workspace filesystem
    # policy, which is what `--sandbox workspace-write` selects on the CLI.
    "extends=:workspace": ("--sandbox", "workspace-write"),
    # `[...network] enabled = true` compiles to an unrestricted network policy
    # for sandboxed commands — the same grant the legacy override makes.
    "network.enabled=true": ("-c", "sandbox_workspace_write.network_access=true"),
}
# The runner argv tokens that decide sandbox or network posture. Anything here
# that the mapping above does not account for is drift the mapping would miss.
CODEX_RUNNER_POSTURE_TOKENS = ("--sandbox", "sandbox_workspace_write.network_access=true")

# Ends on a word character, never a dot: prose comments in the run blocks can
# put a sentence-ending period right after a pin.
_CODEX_NPM_PIN = re.compile(r"@openai/codex@([\w-]+(?:\.[\w-]+)*)")


def _codex_action_step(name: str) -> dict[str, Any]:
    steps: list[dict[str, Any]] = [
        step
        for job in _load(name)["jobs"].values()
        for step in job.get("steps", []) or []
        if str(step.get("uses") or "").startswith("openai/codex-action@")
    ]
    assert len(steps) == 1, f"{name}: expected exactly one codex-action step, found {len(steps)}"
    return steps[0]


def _config_overrides(argv: list[str]) -> list[str]:
    """The values handed to ``-c``, in order — the config surface itself."""
    return [argv[i + 1] for i, flag in enumerate(argv[:-1]) if flag == "-c"]


def _cell_permission_profile() -> dict[str, Any]:
    """The emitted profile the cell steps select, parsed from its own TOML.

    Emitted for the codex cell's real manifest, so this is the document the
    workflow step writes to ``$CODEX_HOME/config.toml``, not a stub of it.
    """
    registry = REPO_ROOT / "config" / "predictors.yaml"
    actor = next((a for a in load_predictors(registry) if a.id == "codex-baseline"), None)
    assert actor is not None, "no `codex-baseline` predictor: the cell this test describes is gone"
    servers = resolve_mcp_servers(load_mcp_servers(registry), actor.mcp_servers)
    document = tomllib.loads(codex_mcp_config(servers))
    # The emitter owns the whole trusted document, so a posture key added at the
    # top level would never reach `_profile_posture_settings`' guard below.
    assert set(document) == {"default_permissions", "permissions", "mcp_servers"}, (
        f"the emitted codex config carries {sorted(document)!r}; a key outside "
        f"retrieval and permissions is configuration no surface compares"
    )
    assert document["default_permissions"] == CODEX_CELL_PERMISSION_PROFILE
    profiles = document["permissions"]
    assert set(profiles) == {CODEX_CELL_PERMISSION_PROFILE}, (
        f"the emitted config.toml declares {sorted(profiles)!r}; the cells select "
        f"exactly one profile, and an unselected second one is dead configuration "
        f"a reader would take for the live policy"
    )
    profile = profiles[CODEX_CELL_PERMISSION_PROFILE]
    assert isinstance(profile, dict)
    return profile


# Every key a cell profile may carry, split into the two that decide posture
# and the one that does not. A key outside this set is a grant (or a narrowing)
# CODEX_POSTURE_PARITY has never been asked about, so it fails here rather than
# reaching a cell unmapped — `filesystem` and `workspace_roots` are the two the
# schema allows next, and either would move what the cell can touch.
_PROFILE_POSTURE_KEYS = ("extends", "network")
_PROFILE_INERT_KEYS = ("description",)


def _profile_posture_settings(profile: dict[str, Any]) -> set[str]:
    """The profile's sandbox/network grants, in the mapping's own spelling."""
    unknown = sorted(set(profile) - set(_PROFILE_POSTURE_KEYS) - set(_PROFILE_INERT_KEYS))
    assert not unknown, (
        f"the cell permission profile carries {unknown!r}, which this test does "
        f"not know how to compare against the runner — add it to "
        f"CODEX_POSTURE_PARITY (with its runner-side expression) or to "
        f"_PROFILE_INERT_KEYS if it decides nothing"
    )
    settings: set[str] = set()
    if "extends" in profile:
        settings.add(f"extends={profile['extends']}")
    network = profile.get("network") or {}
    assert isinstance(network, dict)
    for key, value in network.items():
        settings.add(f"network.{key}={str(value).lower()}")
    return settings


def test_the_codex_invocation_surface_agrees_across_cells_smoke_and_runner() -> None:
    """One codex invocation, six surfaces: both cell steps and the action-path
    smoke share the action pin and its inputs; the profile they select is the
    one the emitted config.toml declares; the runner reaches the same network
    posture through the mapping below; the npm installs pin the CLI version the
    action pins."""
    predict, evaluate = (_codex_action_step(name) for name in CODEX_ACTION_CELL_WORKFLOWS)
    smoke = _codex_action_step(CODEX_ACTION_SMOKE_WORKFLOW)
    assert predict["uses"] == evaluate["uses"], (
        f"the codex-action pin differs between the cell workflows: "
        f"{predict['uses']!r} vs {evaluate['uses']!r} — one permission-profile "
        f"contract cannot be validated against two action versions"
    )
    assert smoke["uses"] == predict["uses"], (
        f"the action-path smoke pins {smoke['uses']!r} but the cells run "
        f"{predict['uses']!r} — the smoke would certify a version nothing else "
        f"uses, which is the exact failure it exists to catch"
    )
    for key in CODEX_LOCKSTEP_INPUTS:
        # Presence first: a `.get()` comparison would pass vacuously when an
        # input vanishes from every surface at once, and `safety-strategy` has
        # no other anchor in the repo.
        for name, step in (
            ("run-predict.yml", predict),
            ("run-evaluate.yml", evaluate),
            (CODEX_ACTION_SMOKE_WORKFLOW, smoke),
        ):
            assert key in step["with"], (
                f"{name}: codex-action input {key!r} is missing — it is part "
                f"of the lockstep invocation surface"
            )
            # The legacy input the profile replaced. It does not compose with
            # `permission-profile` — the action refuses the pair — so a surface
            # that regains it fails at run time, after the cell is funded.
            assert "sandbox" not in step["with"], (
                f"{name}: codex-action input `sandbox:` is back alongside "
                f"`permission-profile:`; the action refuses both together"
            )
        assert predict["with"][key] == evaluate["with"][key], (
            f"codex-action input {key!r} differs between the cell workflows: "
            f"{predict['with'][key]!r} vs {evaluate['with'][key]!r}"
        )
        assert predict["with"][key] == smoke["with"][key], (
            f"codex-action input {key!r} differs between the cells and the "
            f"action-path smoke: {predict['with'][key]!r} vs {smoke['with'][key]!r} "
            f"— the smoke's acceptance claim is only about the block it sends"
        )

    # The profile the steps name is the profile the emitted config declares —
    # the two ends of a selection that fails at startup if they disagree.
    profile = _cell_permission_profile()
    assert predict["with"]["permission-profile"] == CODEX_CELL_PERMISSION_PROFILE, (
        f"the cell steps select {predict['with']['permission-profile']!r} but "
        f"fedcourtsai.mcp emits {CODEX_CELL_PERMISSION_PROFILE!r} — codex refuses "
        f"a `default_permissions` naming a profile its config.toml does not define"
    )

    # The runner's argv is the same invocation for back-tests and the stub
    # cascade. Its `-c` overrides must match the action's on the dialect the two
    # share, and its sandbox/network posture must match the profile's through
    # CODEX_POSTURE_PARITY on the dialect they do not.
    request = RunRequest(
        role=UsageRole.predictor,
        court_id="scotus",
        docket_id=1,
        event_id="evt-petition-disposition",
        actor_id="codex-baseline",
        run_id="20260101T000000Z",
        prompt=Path(".github/prompts/predict.md"),
        data_root=Path("data"),
    )
    argv = CodexRunner().build_command(request).argv
    action_args = json.loads(str(predict["with"]["codex-args"]))
    assert isinstance(action_args, list) and action_args[::2] == ["-c"] * (len(action_args) // 2), (
        f"codex-args must be `-c key=value` pairs only, got {action_args!r} — any "
        f"other flag would decide how codex runs without any surface below "
        f"comparing it against the runner"
    )
    # The action's overrides are the runner's minus the posture ones the profile
    # carries instead; nothing the action passes may be missing from the runner.
    action_overrides = set(_config_overrides(action_args))
    runner_overrides = set(_config_overrides(argv))
    assert action_overrides <= runner_overrides, (
        f"codex config overrides drifted: the action passes "
        f"{sorted(action_overrides - runner_overrides)!r}, which "
        f"CodexRunner.build_command does not"
    )
    mapped_overrides = {
        fragment[1]
        for fragment in CODEX_POSTURE_PARITY.values()
        if fragment[0] == "-c" and len(fragment) == 2
    }
    assert runner_overrides - action_overrides == mapped_overrides, (
        f"the runner's extra config overrides "
        f"{sorted(runner_overrides - action_overrides)!r} are not the ones "
        f"CODEX_POSTURE_PARITY maps the profile onto ({sorted(mapped_overrides)!r})"
    )

    # Both directions of the mapping. Forward: every grant the profile declares
    # is expressed in the runner's argv.
    settings = _profile_posture_settings(profile)
    assert settings == set(CODEX_POSTURE_PARITY), (
        f"the profile declares {sorted(settings)!r} but CODEX_POSTURE_PARITY maps "
        f"{sorted(CODEX_POSTURE_PARITY)!r} — an unmapped profile setting is a "
        f"posture the runner is never checked against"
    )
    for setting, fragment in CODEX_POSTURE_PARITY.items():
        assert any(
            tuple(argv[index : index + len(fragment)]) == fragment
            for index in range(len(argv) - len(fragment) + 1)
        ), (
            f"the profile's {setting!r} has no counterpart in the runner's argv: "
            f"expected {list(fragment)!r}, got {argv!r}"
        )
    # Reverse: every sandbox/network decision the runner's argv makes is one the
    # profile declares, so the runner cannot quietly gain a grant the cells lack.
    for token in CODEX_RUNNER_POSTURE_TOKENS:
        assert token in argv, (
            f"the runner no longer passes {token!r}; CODEX_POSTURE_PARITY maps the "
            f"profile onto it, so the mapping now certifies a posture nothing runs"
        )
    # argv[-1] is the free-text kickoff instruction, scanned out: a prompt that
    # happens to say "network" is not runner posture drift.
    unmapped = [
        token
        for token in argv[:-1]
        if ("sandbox" in token or "network" in token)
        and not any(token in fragment for fragment in CODEX_POSTURE_PARITY.values())
    ]
    assert not unmapped, (
        f"the runner passes sandbox/network argv {unmapped!r} that no "
        f"CODEX_POSTURE_PARITY entry maps to a profile setting — the action path "
        f"would run without it"
    )

    # The CLI the action installs is the CLI the npm surfaces pin.
    version = str(predict["with"]["codex-version"])
    for name in CODEX_NPM_PIN_WORKFLOWS:
        pins = {pin for block in _joined_run_blocks(name) for pin in _CODEX_NPM_PIN.findall(block)}
        assert pins == {version}, (
            f"{name}: @openai/codex npm pin(s) {sorted(pins)!r} differ from the "
            f"cell steps' codex-version {version!r}"
        )


# The codex hang bound, which is three step attributes and their ORDER. A
# wedged `codex exec` outlives the engine step's own `timeout-minutes` — the
# step stays `in_progress` until the job cap cancels the runner, which runs
# none of the capture tail and leaves GitHub no logs to serve, so the hang
# erases its own evidence and spends the whole budget. The watchdog converts
# that into a step failure the tail salvages, and every clause of it is YAML
# nothing at runtime notices: an arm step that does not immediately precede the
# engine guards a window that is not the engine's, a disarm step that does not
# immediately follow it leaves a killer running through the capture steps, a
# deadline at or above the step's own backstop never bites first, and a bundle
# the artifact does not carry is thrown away with the runner.
CODEX_WATCHDOG_SCRIPT = "scripts/codex-watchdog.sh"
CODEX_WATCHDOG_DIR = "codex-watchdog"
# 40 minutes, against a 60-minute job cap and the engine step's 50-minute
# backstop; the arm steps carry the arithmetic.
CODEX_WATCHDOG_DEADLINE_S = "2400"
CODEX_WATCHDOG_CELL_JOBS = {"run-predict.yml": "predict", "run-evaluate.yml": "evaluate"}


def test_the_codex_cell_brackets_its_engine_with_a_watchdog() -> None:
    assert (REPO_ROOT / CODEX_WATCHDOG_SCRIPT).is_file()
    for name, job_name in CODEX_WATCHDOG_CELL_JOBS.items():
        job = _load(name)["jobs"][job_name]
        steps = job["steps"]
        engine_at = next(
            i
            for i, step in enumerate(steps)
            if str(step.get("uses") or "").startswith("openai/codex-action@")
        )
        engine = steps[engine_at]
        arm, disarm = steps[engine_at - 1], steps[engine_at + 1]
        assert arm.get("name") == "Arm the codex watchdog", f"{name}: nothing arms the watchdog"
        assert disarm.get("name") == "Disarm the codex watchdog", (
            f"{name}: the step after the engine does not disarm the watchdog"
        )
        # The arm step guards exactly the window the engine step runs in.
        assert arm.get("if") == engine.get("if"), f"{name}: the arm step's gate is not the engine's"
        assert CODEX_WATCHDOG_SCRIPT in str(arm["run"])
        # The production pattern is the script's default; an override here
        # would point the watchdog at a process the cell does not run.
        assert set(arm["env"]) == {"CODEX_HOME", "WATCHDOG_DIR", "WATCHDOG_DEADLINE_S"}, (
            f"{name}: unexpected watchdog configuration {sorted(arm['env'])!r}"
        )
        assert arm["env"]["CODEX_HOME"] == CODEX_HOME_EXPRESSION
        # Outside the workspace: the bundle is evidence about a cell that may
        # be wedged inside that tree, so the tree must not be able to rewrite
        # it. The disarm step is what carries it back for the upload.
        assert arm["env"]["WATCHDOG_DIR"] == f"${{{{ runner.temp }}}}/{CODEX_WATCHDOG_DIR}"
        assert arm["env"]["WATCHDOG_DEADLINE_S"] == CODEX_WATCHDOG_DEADLINE_S
        # Deadline < the step's own `timeout-minutes` < the job cap. The middle
        # bound is a backstop for an overrun the runner can end, not evidence
        # that it ends this one — a wedged engine has run straight through it;
        # what this pins is that the watchdog is the bound that comes first and
        # that its kill still leaves the tail inside the job.
        deadline_minutes = int(CODEX_WATCHDOG_DEADLINE_S) / 60
        assert deadline_minutes < engine["timeout-minutes"] < job["timeout-minutes"], (
            f"{name}: the watchdog deadline does not sit under the step and job bounds"
        )
        # `always()`, so an engine that failed, timed out, or never ran still
        # stands its killer down before the capture tail.
        assert disarm.get("if") == "${{ always() && matrix.engine == 'codex' }}"
        assert "codex-watchdog.pid" in str(disarm["run"])
        assert CODEX_WATCHDOG_DIR in str(disarm["run"]), (
            f"{name}: the disarm step does not carry the bundle back for the upload"
        )
        # The evidence has to leave the runner, and the cell artifact is the
        # only thing that does; the collect job commits `data/` alone, so the
        # bundle reaches a maintainer without reaching the ledger.
        upload = next(s for s in steps if s.get("name") == "Upload cell output")
        assert CODEX_WATCHDOG_DIR in str(upload["with"]["path"]).split()


# The one condition every engine-actions-smoke step is gated on. A leg whose
# steps are gated on something subtly different runs nothing and reports
# green, which is the vacuous pass the scenario exists to replace.
ACTIONS_SMOKE_IF = "${{ matrix.scenario == 'engine-actions-smoke' }}"
ACTIONS_SMOKE_ENGINES = ("claude-code", "codex", "gemini")


_GEMINI_SETTINGS = re.compile(r"(\{\"context\":\{\"fileFiltering\".*?\}\}\})")


def _gemini_settings_literal(name: str) -> str:
    """The one `.gemini/settings.json` literal a workflow writes."""
    found = {
        match.group(1)
        for block in _joined_run_blocks(name)
        for match in _GEMINI_SETTINGS.finditer(block)
    }
    assert len(found) == 1, f"{name}: expected one gemini settings literal, found {len(found)}"
    return found.pop()


def _actions_smoke_steps() -> list[dict[str, Any]]:
    job = _load("integration-test.yml")["jobs"]["scenario"]
    return [
        step
        for step in job["steps"]
        if "engine-actions-smoke" in str(step.get("if") or "")
        and "engine-smoke'" not in str(step.get("if") or "")
    ]


def test_the_action_path_smoke_invokes_each_engine_the_way_the_cells_do() -> None:
    """The `engine-actions-smoke` legs run the cells' own invocation surfaces.

    The scenario claims only that each engine still *accepts* the block a cell
    sends it — the layer the engine smoke never traverses, since that leg
    drives the bare CLI through the runner. The claim is worth exactly the
    fidelity of the blocks, so the pins live here: the two actions at the same
    shas the cells use (the codex `with:` inputs are compared value by value
    above), gemini through the same CLI call `run-predict` makes, and every
    step gated on one spelling of one condition so a leg cannot go green
    having invoked nothing.
    """
    steps = _actions_smoke_steps()
    assert steps, "the engine-actions-smoke scenario has no steps at all"
    for step in steps:
        condition = str(step["if"])
        engine_clause = [
            f" && matrix.engine == '{engine}' }}}}" for engine in ACTIONS_SMOKE_ENGINES
        ]
        assert condition == ACTIONS_SMOKE_IF or any(
            condition == ACTIONS_SMOKE_IF.removesuffix(" }}") + clause for clause in engine_clause
        ), f"unexpected engine-actions-smoke condition: {condition!r}"

    by_id = {step.get("id"): step for step in steps}

    # Claude: the cells' action at the cells' sha, with the inputs that decide
    # how it runs. `github_token` is the one deliberate deviation — the cells
    # mint an App token for the agent's issue comment, and a probe must not —
    # so it is pinned to the job token rather than left free.
    claude = by_id["actions_smoke_claude"]
    cell_claude = next(
        step
        for step in _load("run-predict.yml")["jobs"]["predict"]["steps"]
        if str(step.get("uses") or "").startswith("anthropics/claude-code-action@")
    )
    assert claude["uses"] == cell_claude["uses"], (
        "the action-path smoke pins a different claude-code-action than the cells"
    )
    assert claude["with"]["allowed_bots"] == cell_claude["with"]["allowed_bots"]
    assert claude["with"]["anthropic_api_key"] == cell_claude["with"]["anthropic_api_key"]
    assert claude["with"]["settings"] == cell_claude["with"]["settings"]
    assert claude["with"]["github_token"] == "${{ github.token }}", (
        "the smoke must hand claude-code-action the job's read-capped token: "
        "omitting it triggers the action's OIDC fallback, which mints an "
        "installation token defaulting to contents/issues/pull-requests write"
    )
    # The args the cells pass, minus the model (resolved per engine below).
    cell_args = {
        line.strip()
        for line in str(cell_claude["with"]["claude_args"]).splitlines()
        if line.strip() and not line.strip().startswith("--model")
    }
    smoke_args = {
        line.strip()
        for line in str(claude["with"]["claude_args"]).splitlines()
        if line.strip() and not line.strip().startswith("--model")
    }
    assert smoke_args == cell_args, (
        f"claude_args drifted between the cell and the smoke: {sorted(smoke_args ^ cell_args)}"
    )

    # Gemini has no pinned action (the upstream one `uses:` unpinned actions),
    # so its production invocation is the CLI call in run-predict's own step —
    # which is what this leg must reproduce, flag for flag.
    gemini = by_id["actions_smoke_gemini"]
    cell_gemini = next(
        step
        for step in _load("run-predict.yml")["jobs"]["predict"]["steps"]
        if str(step.get("name") or "") == "Predict with Gemini"
    )
    invocation = 'gemini --yolo --model "$MODEL_ID" --prompt "$PROMPT" --output-format json'
    assert invocation in " ".join(str(cell_gemini["run"]).split()), (
        "the cell's gemini invocation moved; this test's expectation is stale"
    )
    assert invocation in " ".join(str(gemini["run"]).split()), (
        "the smoke's gemini invocation differs from the cell step's"
    )
    # The settings file is part of what gemini is invoked *with* — the CLI
    # reads it at startup and `mcp-config --base-settings` merges over it — and
    # its schema has twice produced a silent no-op from a wrong namespace, so a
    # probe sending a trimmed one would certify a configuration the cells do
    # not run. One literal, compared whole, across the cell step and the
    # workflow step both engine legs share.
    settings = _gemini_settings_literal("integration-test.yml")
    assert settings == _gemini_settings_literal("run-predict.yml"), (
        "the gemini settings literal drifted between the cell step and the "
        "integration workflow's — that file is part of the invocation surface"
    )
    assert (
        gemini["env"]["GEMINI_CLI_TRUST_WORKSPACE"]
        == (cell_gemini["env"]["GEMINI_CLI_TRUST_WORKSPACE"])
    )
    assert gemini["env"]["GEMINI_API_KEY"] == cell_gemini["env"]["GEMINI_API_KEY"]

    # Each engine's key reaches only its own leg: the step conditions above
    # already partition them, and no leg may carry a second engine's secret.
    for engine, step in (
        ("claude-code", claude),
        ("codex", by_id["actions_smoke_codex"]),
        ("gemini", gemini),
    ):
        rendered = yaml.safe_dump(step)
        for other, secret in (
            ("claude-code", "ANTHROPIC_API_KEY"),
            ("codex", "OPENAI_API_KEY"),
            ("gemini", "GEMINI_API_KEY"),
        ):
            if other == engine:
                continue
            assert secret not in rendered, f"the {engine} leg carries {other}'s key"


def test_the_action_path_smoke_probes_the_model_a_cell_would_run() -> None:
    """The probe resolves its model from the package, and that is the model a
    cell resolves too.

    A literal here would drift the day an engine's default moves, leaving the
    smoke certifying an invocation production no longer makes. So the step
    reads `DEFAULT_MODELS`, and this holds the other half of that equivalence:
    the baseline predictors pin no override, so `DEFAULT_MODELS` *is* what the
    predict matrix resolves into their cells. If one ever takes an override,
    the smoke has to follow it rather than this assertion being deleted.
    """
    predictors = yaml.safe_load((REPO_ROOT / "config" / "predictors.yaml").read_text())
    baselines = {
        entry["engine"]: entry
        for entry in predictors["predictors"]
        if entry["id"] in {"claude-baseline", "codex-baseline", "gemini-baseline"}
    }
    assert set(baselines) == set(ACTIONS_SMOKE_ENGINES)
    for engine, entry in baselines.items():
        assert entry.get("model") is None, (
            f"{entry['id']} pins model {entry['model']!r}, so a cell of this engine no "
            f"longer runs DEFAULT_MODELS[{engine!r}] — the action-path smoke's model "
            f"resolution must follow the registry override instead"
        )

    (resolve,) = [step for step in _actions_smoke_steps() if step.get("id") == "cell"]
    run = " ".join(str(resolve["run"]).split())
    assert "from fedcourtsai.pricing import DEFAULT_MODELS" in run
    for engine in ACTIONS_SMOKE_ENGINES:
        assert f"{engine})" in run, f"the resolve step names no cell identity for {engine}"
    # The resolved value rides into an action's `with:` block, so it is
    # shape-screened before it becomes a step output.
    assert "*[!a-zA-Z0-9.-]*" in run
    # And every engine's invocation reads it, rather than one of them keeping
    # a literal that the resolve step's existence would then hide.
    readers = {
        str(step.get("id"))
        for step in _actions_smoke_steps()
        if "steps.cell.outputs.model" in yaml.safe_dump(step)
    }
    assert readers >= {
        "actions_smoke_claude",
        "actions_smoke_codex",
        "actions_smoke_gemini",
    }, f"an invocation does not read the resolved model: {sorted(readers)}"


def test_the_text_coverage_summary_truncation_matches_the_cli_ledger_headers() -> None:
    """The text-coverage job's step summary is truncated at the first ledger
    header by an awk sentinel, because the summary is readable without login
    while the artifact is not — the untruncated case-id ledgers must never
    land on the page. The sentinel couples a workflow regex to the CLI's
    ledger-header spellings, so this pins them together: renaming a header in
    `_echo_text_coverage` without moving the awk pattern would silently dump
    every case id onto the summary (the size guard bounds, but the sentinel
    is the control)."""
    wf = _load("run-analytics.yml")
    steps = wf["jobs"]["text-coverage"]["steps"]
    run = next(s["run"] for s in steps if "awk" in s.get("run", ""))
    match = re.search(r"awk '/(.+?)/\{exit\}", run)
    assert match, "the truncation sentinel awk pattern is gone from the summary step"
    pattern = re.compile(match.group(1))

    coverage = TextCoverage(
        cases=3,
        cases_read=2,
        distributed=3,
        distributed_without_petition=1,
        queued=2,
        queued_cert_forms=1,
        queued_application_forms=1,
        queued_without_petition=1,
        queued_without_application=1,
        unopened_petitions=0,
        offloaded=True,
        cuts=[TextCoverageCut(kind="petition", segment="scored", documents=2, empty=1)],
        empty_documents={"scotus/1": ["petition"]},
        queued_without_petition_cases=["scotus/2"],
        # Every ledger, so the sentinel is pinned against all of them and not
        # only the two that happen to print first.
        queued_without_application_cases=["scotus/3"],
    )
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        _echo_text_coverage(coverage)
    lines = buffer.getvalue().splitlines()

    matched = [i for i, line in enumerate(lines) if pattern.search(line)]
    assert matched, (
        "no line of the CLI report matches the workflow's truncation sentinel — "
        + "a ledger header was renamed and the summary would carry every case id"
    )
    kept = lines[: matched[0]]
    assert not any(
        any(case_id in line for case_id in ("scotus/1", "scotus/2", "scotus/3")) for line in kept
    ), "a ledger case id sits above the truncation sentinel — the summary would leak it"

    # EVERY header, not just the first one printed. A ledger is printed only
    # when it is non-empty, so a header missing from the sentinel leaks its
    # whole ledger onto the login-free summary on any run where the ledgers
    # above it happen to be empty — which is the state a drained gap reaches.
    headers = [line for line in lines if re.match(r"^\S.*\(\d+ case\(s\)\):$", line)]
    assert len(headers) == 3, f"expected three ledger headers, got {headers}"
    unguarded = [header for header in headers if not pattern.search(header)]
    assert not unguarded, (
        "a ledger header is outside the workflow's truncation sentinel, so a run "
        + f"whose earlier ledgers are empty would publish its case ids: {unguarded}"
    )


def test_the_daily_digest_job_keeps_its_narrow_permission_surface() -> None:
    """The digest job opens issues, so its grant is pinned rather than inherited.

    It exists as a separate job for exactly one reason — permissions are
    per-job — so that grant is the thing an edit must not widen by accident. It
    reads the committed ledger and writes issues; it touches no branch, no
    environment, and no secret, and a `contents: write` or an `environment:`
    appearing here would mean the reporting surface had grown a writer's
    capability.
    """
    job = _load("run-ops.yml")["jobs"]["daily-digest"]
    assert job["permissions"] == {"contents": "read", "issues": "write"}
    assert "environment" not in job
    assert "secrets." not in yaml.safe_dump(job), "the digest job needs no secret"


def test_no_workflow_triggers_on_a_digest_label() -> None:
    """The digests' labels must stay non-triggering, which is what makes the job safe.

    A reporting job holding `issues: write` opens an issue every day; if any
    workflow ever keyed on that label, the daily report would start a run — and
    a spending one, if the label were ever added to a fan-out. Nothing enforces
    the property but this assertion, so it reads every workflow rather than the
    one that posts.
    """
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        workflow = _load(path.name)
        # `on` parses to the truthy bool key in YAML; tolerate either spelling.
        triggers = workflow.get("on") or workflow.get(True) or {}
        for label in (DAILY_DIGEST_LABEL, WEEKLY_DIGEST_LABEL):
            assert label not in yaml.safe_dump(triggers), (
                f"{path.name} triggers on the non-triggering {label} label"
            )
            for name, job in (workflow.get("jobs") or {}).items():
                conditions = [str(job.get("if", ""))]
                conditions += [str(step.get("if", "")) for step in job.get("steps", [])]
                for condition in conditions:
                    assert label not in condition, (
                        f"{path.name}:{name} gates on the non-triggering {label} label"
                    )


def test_every_schedule_gate_names_a_cron_run_ops_declares() -> None:
    """A cron literal in a gate must be one the workflow actually declares.

    Change the schedule and forget the gate, and the weekly digest silently stops
    posting — fail-closed, but silently, on a surface whose whole point is being
    read once a week, so "silently" costs weeks. Scoped by *what a gate compares
    against* rather than by the step's name, because a gate can live in an `if:`
    or in an `env:` value the shell then tests, and keying on the name would stop
    covering the gate the moment it moved.
    """
    workflow = _load("run-ops.yml")
    triggers = workflow.get("on") or workflow.get(True) or {}
    declared = {str(entry["cron"]) for entry in triggers["schedule"]}
    gates = [
        expression
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
        for expression in [str(step.get("if", "")), *map(str, (step.get("env") or {}).values())]
        if "github.event.schedule" in expression
    ]
    assert gates, "run-ops gates nothing on its schedule"
    for gate in gates:
        assert any(cron in gate for cron in declared), (
            f"the gate {gate!r} names no cron run-ops declares: {sorted(declared)}"
        )
