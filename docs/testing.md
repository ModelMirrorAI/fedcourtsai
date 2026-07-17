# Testing

How the project is tested, and how to exercise the parts that normally only run in
GitHub Actions. The guiding split mirrors the rest of the architecture: the
**deterministic core** is ordinary library code, tested exhaustively offline; the
**agentic stages** delegate judgment to coding agents inside workflows, and the job
of the local harness is to make everything *around* that judgment runnable without
a CI round-trip.

For where these commands fit the pipeline, see [pipeline.md](pipeline.md); for
the change workflow every contributor follows, see [AGENTS.md](../AGENTS.md).

## The local gate

The gate is the contract: "passes the local gate" and "green CI" mean the same
thing, because [`ci.yml`](../.github/workflows/ci.yml) runs exactly these commands
and nothing secret.

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov --cov-report=term-missing
uv run fedcourts validate data       # ledger schema + git-only references
uv run fedcourts corpus-status       # corpus + metrics bookkeeping is consistent
```

The `pytest` run includes an offline **stub-cascade smoke** (`tests/test_cascade_smoke.py`):
it drives provision → predict → evaluate → `validate` over the fixture corpus with no
network, so a broken predict/evaluate cell fails in the gate in seconds. Run just it
with `uv run pytest -k cascade_smoke`.

If you changed the pydantic models, regenerate and commit the exported schemas —
CI fails on drift:

```bash
uv run fedcourts export-schemas schemas
git diff --exit-code schemas
```

Run it all in the included devcontainer (`.devcontainer/`) or any environment with
[uv](https://docs.astral.sh/uv/).

## What's covered where

**The deterministic core** — schemas and ids/paths, the registry and matrix
builders, corpus ingestion, retrieval, validation, and the back-test harness — is
plain Python under `pytest`, using `tmp_path` and in-memory corpus seeding. This is
the bulk of the codebase and it is fully testable offline. The
[`Backtester`](data-pipeline.md) seam is the model to imitate: its reference
predictors (`ConstantBacktester`, `PriorVoteBacktester`) run with no model and no
network, so the scoring metric is real in a unit test.

**The agentic stages** — `run:predict` and `run:evaluate` —
are the gap. They invoke a coding agent (`anthropics/claude-code-action` and the
Codex equivalent) *inside the workflow*, so without a harness the only feedback on a
change to a prompt, the snapshot provisioning, or a finalize step is "open a PR,
have a maintainer apply a label, wait for Actions, read the logs" — slow,
token-spending, and human-gated.

**Infra-bound integration** — the live CourtListener REST API, the corpus pull
from S3 over OIDC, the GitHub App token, issue comments — is deliberately
*not* part of the fast loop. It is exercised by dedicated paths and occasional
manual workflow dispatch, never on every iteration.

That infrastructure has a dedicated path:
[`integration-test.yml`](../.github/workflows/integration-test.yml) (manual
dispatch, read-only role, strictly side-effect free) runs one scenario per
dispatch. `ranged-reads` is the tested `fedcourts corpus-integration-check`
read set — a point lookup, a priors retrieval, a snapshot provisioning —
against the real remote blob for a known case, asserting every read comes back
non-empty, reporting per-read GET/byte counters to the run summary, and
exiting non-zero on a blown wall-clock budget. `corpus-service` launches the
same corpus sidecar composite the cell workflows use and probes it through the
exact CLI surface a cell retrieves with. `stub-cascade` runs one offline stub
`local-cascade` cell over the ranged backend, covering provisioning end to
end. `mcp-sidecar` launches the same CourtListener MCP sidecar composite the
cell workflows use, deliberately without its optional token input, and runs
the tested `fedcourts mcp-integration-check` client against it (initialize +
tools/list, failing unless the handshake completes and tools are advertised).
`engine-smoke` is the one token-spending scenario: a single real-engine
predictor cell (the `engine` input picks which; one predict cell's spend
against the default open-event case — a resolved event also replays
evaluator cells) driven through `local-cascade` with the agent's retrieval on the
service sidecar and the cascade's own provisioning reads pinned to `ranged`
via `--corpus-backend` — the full production cell posture, including each
engine's real sandbox semantics, which is exactly the layer an engine-level
integration break (a sandbox denying localhost, a CLI behavior change) hides
in. Dispatch a scenario around the changes it guards: **before and after any
change to corpus access** (the read seams, `corpus_ranged`, the sidecar
composites, the blob's physical layout) **or to a corpus-consuming workflow**,
**engine-smoke around any engine CLI version bump or sandbox/config change**,
and as a preflight **before a release dry run** and **before a prediction
freeze** — the moments when a silent read regression would be most expensive.
The `deploy-environment` input names which deployment environment supplies the
role and remote variables: main dispatches use `runner`, and a
maintainer-approval-gated environment (deployment-branch policy open, required
reviewer) lets a PR branch's changed read seams run against real
infrastructure before merge — the capability the trigger path structurally
cannot provide.

> **Status.** The deterministic core and the gate above, the engine seam (with the
> offline `stub` and `replay` backends), the fixture corpus, the stub cascade that
> composes them (run in the gate as the `test_cascade_smoke.py` smoke), and the
> one-command `local-cascade` wrapper are all in place today. What remains is folding
> the rest of the workflow shell into tested CLI commands.

## Testing the agentic stages locally

Three pieces turn the agentic cells into something runnable on a laptop, keeping the
local path **byte-identical** to the workflow path so a green local run faithfully
predicts a green CI run.

**An engine seam with offline backends.** The per-engine execution lives behind a
runner interface in the library rather than in YAML. Alongside the real
`claude-code`, `codex`, and `gemini` backends sits a `stub` backend that writes
schema-valid canned artifacts with no model call and no network. The stub exercises the whole
cell mechanism — provisioning, artifact production, validation, and the code that
consumes the output — so the majority of "did I break the plumbing" regressions are
caught in `pytest`, not in CI. The stub tests the scaffolding, not the judgment;
that distinction is the point.

**A `replay` backend for the consume path.** The stub's output is *clean by
construction* (the trivial `denied`/0.0 floor), so it cannot catch a bug in the code
that **consumes** realistic agent output — the scoring metrics, the leaderboard
roll-up. The `replay` backend closes that gap: it emits a **captured real
prediction** from a committed cassette (`tests/cassettes`, pointed at by
`FEDCOURTS_REPLAY_ROOT`), keeping the recorded forecast — a real calibrated
probability and panel votes — while rebinding identity to the cell. Scoring it
reuses the stub's deterministic evaluate path, so an evaluate cell computes a
non-degenerate Brier score and vote accuracy, and the leaderboard rolls up real
numbers — all offline and token-free. `tests/test_replay.py` drives that consume
path over the cassette; capturing a fresh cassette is a record-once step (run a real
cell, copy its `prediction.json` / `reasoning.md` under `tests/cassettes`).

**A fixture corpus.** A tiny synthetic corpus, built deterministically by
`fedcourts make-fixture-corpus`, stands in for the S3-hosted corpus so
`provision-snapshot`, `query`, and `open-events` — and therefore the whole cascade —
run with no remote, no role assumption, and no tokens.

**A one-command cascade.** `fedcourts local-cascade --court <id> --docket <id>`
chains provision → predict → evaluate → `validate` over the fixture corpus:

```bash
# offline, token-free — the default loop
uv run fedcourts local-cascade --court ca9 --docket <id> --engine stub

# a real end-to-end run; use subscription auth locally so it doesn't bill per token
export CLAUDE_CODE_OAUTH_TOKEN=...
uv run fedcourts local-cascade --court ca9 --docket <id> --engine claude-code
```

The stub cascade is fast and offline enough to belong in the gate, and it does:
`tests/test_cascade_smoke.py` drives it over the fixture corpus on every `pytest`
run, so a broken predict/evaluate cell surfaces *before* a PR is opened. A
real-engine run is a deliberate, occasional check — it catches prompt-level
regressions the stub can't see — not the inner loop.

## Keep the workflow a thin wrapper

The more logic lives in YAML, the less of the pipeline is testable, because YAML only
runs in Actions. The standing principle is to push logic *out* of the workflows and
into tested `fedcourts` commands, leaving the YAML as orchestration. The matrix
builders follow this (`predict-matrix` / `evaluate-matrix` are library code with unit
tests, not inline script), as do the predict/evaluate decisions: the
trigger-authorization gate (`authorize-trigger`), whether a cell produced its own
output (`finalize-produced`), the path jail (`assert-paths`), and the per-run
ready/draft PR aggregation (`collect-plan`). The YAML
calls those and runs only the git/`gh` plumbing, so "test the workflow" reduces to
"test the commands, then smoke-test the wiring."

For the orchestration that genuinely must live in YAML, two static checks already
run in CI and catch most mistakes without execution:
[`lint-actions.yml`](../.github/workflows/lint-actions.yml) runs **actionlint**
(workflow syntax, `${{ }}` expressions, `needs`/matrix references, embedded shell)
and **zizmor** (the security invariants in [SECURITY.md](../SECURITY.md) — pinned
actions, least-privilege permissions). For a heavier local check of the
deterministic jobs (the `plan` job, matrix generation, the auth gate),
[`nektos/act`](https://github.com/nektos/act) can run them in Docker — useful for
orchestration, though its OIDC and secret handling mean it does not cover the agent
or S3 steps.

## Fixture scale is not corpus scale

The fixture corpus is deliberately tiny, and that blinds it to two classes of bug.
**Scale blowups:** code that iterates every row — or issues a per-item query that
itself scans a whole court's slice — passes fixture-sized tests instantly and then
times out on its first run against the real corpus of millions of cases. When
writing anything that walks the corpus, budget its complexity against the full row
count, not the fixture's; prefer building an index or a single filtered query over
per-item scans. **Data-shape assumptions:** the fixture's values are clean by
construction, but a century of real docket data is not — historical numbering
formats, sparse or missing dates, and unlinked records dominate the long tail, so a
parser or scope predicate that looks total on the fixture can quietly mis-classify
at scale. The check is the same for both: before relying on new corpus-walking code
or a new predicate, exercise it against the real corpus through a read-only
analytics run and read the numbers it reports. The fixture proves the logic;
only the corpus proves it at scale.

## The boundary that remains

Even with the harness, two things stay outside the fast loop by design, and that is
correct: **model judgment** (the stub is clean by construction, so prediction
*quality* is only seen in a real run) and **secret-bound infra** (the live API, the
S3 remote, the App token). Treat both as deliberate, infrequent checks — a real
`local-cascade` run and a manual workflow dispatch — rather than gaps to close. The
goal of the harness is not to run everything locally; it is to make the *common*
change — to a prompt, a schema, a cell's plumbing, an orchestration step — fail fast
on a laptop instead of in CI.
