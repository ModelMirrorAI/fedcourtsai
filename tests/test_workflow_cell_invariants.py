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
  (the scan gate, the retention window, the survive-failure condition) is a
  YAML attribute nothing else checks.

Each would regress silently: the cell still runs, the artifact still validates,
the integration gate stays green. So the contracts get pinned here instead.
"""

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
    assert scan.get("continue-on-error") is True  # withhold, never fail the labels result
    assert "scan-diff-for-secrets" in scan["run"]
    assert scan.get("timeout-minutes") == 5  # bounded inside the job's post-agent budget
    assert "--known-secret-env ANTHROPIC_API_KEY" in scan["run"]  # the reachable credential
    upload = next(s for s in steps if (s.get("with") or {}).get("name") == "qp-label-transcript")
    assert upload["with"]["path"] == "${{ steps.label.outputs.execution_file }}"
    assert upload["with"]["retention-days"] == 1
    assert "!cancelled()" in upload["if"]
    assert "steps.transcript_scan.outcome == 'success'" in upload["if"]
