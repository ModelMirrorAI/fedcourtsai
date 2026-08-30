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
thing, because [`ci.yml`](../.github/workflows/ci.yml) and the local gate invoke
the same script — [`scripts/gate.sh`](../scripts/gate.sh), the single definition of
what the gate runs (stages and usage: [AGENTS.md](../AGENTS.md)). It needs nothing
secret.

The `test` stage includes an offline **stub-cascade smoke** (`tests/test_cascade_smoke.py`):
it drives provision → predict → evaluate (blinded, then un-aliased) → `validate` over the fixture corpus with no
network, so a broken predict/evaluate cell fails in the gate in seconds. It covers every
predicted stage — a cert petition, and the opt-in CVSG docket whose later-moment cert
cell answers the same `cert-v2` claim set; the fixture's substantive stay application,
whose interim cell answers the four `interim-v1` claims and carries a Brier score but no
segment baseline; and its granted docket,
whose merits cell carries a judgment with its mandatory vote block, the one declared
`merits-v1` claim, and the two declared `semantic-v1` propositions its grader answers
entirely with the availability mask (the fixture corpus holds no opinion body). Each non-cert cell lands in the leaderboard's own unranked stage block
rather than the ranked cert board, and the later-moment cert cell likewise aggregates
into its own `cert@cvsg` block. Run just it with `uv run pytest -k cascade_smoke`.

If you changed the pydantic models, the `schemas` stage regenerates the exported
schemas and fails on drift — so regenerate and commit them in the same change.

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
dispatch, read-only role — the collect scenario none at all — strictly
side-effect free) runs one scenario per dispatch, or — `scenario=all` — the
promotion gate's whole required suite as one run (every required scenario, with
engine-smoke once per engine, so three cells' token spend; collect rides the
run as its own environment-free job beside the matrix). `scenario=all-offline`
is that suite minus the three engine-smoke legs; the jobs that remain are
identical, environment binding included, and the run is token-free end to end.
`ranged-reads` is the tested `fedcourts corpus-integration-check`
read set — a point lookup, a priors retrieval, a snapshot provisioning —
against the real remote blob for a known case, asserting every read comes back
non-empty, reporting per-read GET/byte counters to the run summary, and
exiting non-zero on a blown wall-clock budget. `corpus-service` launches the
same corpus sidecar composite the cell workflows use — with the same
corpus-split inputs, so under the split the sidecar hydrates from the content
store exactly as the fleet's does — and probes it through the exact CLI
surface a cell retrieves with. `stub-cascade` first runs the production
`provision-snapshot --mode forward --refuse-terminal` command against the
known case in an isolated data root, failing the leg on a refusal (the same
command is `continue-on-error` in run-predict, so this is where a guard
drifting to always-refuse surfaces; the dispatched case must be genuinely
open — snapshot non-terminal, corpus event unresolved, row undecided, no
committed outcome — since the guard now reads the record as well as the
snapshot), then runs one offline stub `local-cascade` cell over the ranged
backend, covering provisioning end to end. `mcp-sidecar` launches the same
CourtListener MCP sidecar composite the
cell workflows use, deliberately without its optional token input, and runs
the tested `fedcourts mcp-integration-check` client against it (initialize +
tools/list, failing unless the handshake completes and tools are advertised).
`collect` exercises the `collect-run` composite — the single writer for a
predict/evaluate run's agent output — against synthetic stamped cells the job
itself builds from the fixture corpus and uploads to its own run: a `gh` shim
forces one artifact's download to fail and stubs every PR surface, and a git
URL rewrite diverts the branch push to a runner-local scratch remote, so the
scenario asserts collect's whole durability contract (a transfer loss costs
one cell and not the run; the plan names the lost artifact and the
queued-cell census the never-uploaded cell, and both withhold the
trigger-issue close; the salvage cell
rides the draft; a rerun updates in place) with no App token, no PR, and no
matrix spend. It is the one scenario whose job binds no deployment
environment at all — it needs no role variables and no secret — so it is the
one scenario no deployment-branch policy can ever refuse, and a dispatch from
any branch runs it to completion.
`qp-topic` drives the shared `qp-topic-measure` composite — the post-label
half of the paid labeling run: the no-output guard, the `fedcourts qp-topics`
publication gate, and the publish-and-validate path — over canned inputs built
from the committed reference set: a labeler that wrote nothing and one that
drifted below the agreement gate must both fail without publishing, and a
faithful one must publish an artifact covering the whole reference set.
Token-free and credential-free; the extract and the model call stay uncovered
*by this scenario* by design — the extract is a corpus read, so it is pinned in
the unit suite instead (scope, the `--all` measurement form, the row ceiling,
and the content-store path under the split, all over corpora built in
`tmp_path`), and the model call is exactly what `run-analytics` pays for.
`engine-smoke` is the one token-spending scenario: a single real-engine
predictor cell (the `engine` input picks which — an `all` dispatch ignores it
and runs one smoke per engine; one predict cell's spend
against the default open-event case — a resolved event also replays
evaluator cells) driven through `local-cascade` with the agent's retrieval on the
service sidecar and the cascade's own provisioning reads pinned to `ranged`
via `--corpus-backend` — the full production cell posture, including each
engine's real sandbox semantics, which is exactly the layer an engine-level
integration break (a sandbox denying localhost, a CLI behavior change) hides
in. Its codex leg additionally wires the CourtListener MCP sidecar and the
generated client config the live cells get, and uploads the cell's rollout
distilled to item shapes alone (`fedcourts codex-item-shapes` — types and key
names, never a value, with the key screen's residual and the shape cap stated
in [cli.md](cli.md), so the artifact is publishable where the transcript is
not): the retrieval parser keys on those shapes, an unrecognized one reads
exactly like a cell that called nothing, and a real transcript is the only
thing that separates the two. That distinction is why the distillation is
worth uploading at all — under code mode a manifest call is not an item but a
call written inside a freeform call's own source, so what the parser must key
on is a shape no item census would have revealed. Read the artifact against the environment the
dispatch bound: where that environment carries no CourtListener token the
sidecar runs token-free, the handshake and tool listing still succeed, and
tool *calls* error — the shapes are then an errored call's, which still
answers the question, but only a token-bearing dispatch also shows a settled
one. The job log's sidecar replay is the second witness either way: requests there
against a distillation carrying `custom_tool_call` items and no
`mcp_tool_call` / `mcp_call` ones is code mode working as designed — the
manifest calls are lifted from the freeform call's source, not from an
MCP-shaped item, which code mode never emits. No requests at all is the engine
never reaching the sidecar — a decline, or a sidecar that never came up, since
health is warn-only on this leg. Observation, not a gate — the leg's verdict is
still the cell's. Dispatch a scenario around the changes it guards: **before and after any
change to corpus access** (the read seams, `corpus_ranged`, the sidecar
composites, the blob's physical layout) **or to a corpus-consuming workflow**,
**engine-smoke around any engine CLI version bump or sandbox/config change**,
**collect around any change to the `collect-run` composite or the collect
jobs that call it**, **qp-topic around any change to the `qp-topic-measure`
composite, the labeling job, or the `qp_topics` module — and before any paid
labeling dispatch**, and as a preflight **before a release dry run** and
**before a prediction freeze** — the moments when a silent read regression
would be most expensive.

The qp-topic clause generalizes: **a new token-spending run mode lands its
token-free `integration-test.yml` scenario before its first paid dispatch,
never after.** The scenario exercises the mode's plumbing — artifact hand-off,
IO staging, guards, the publication path — over canned or fixture inputs, the
way `qp-topic` and `collect` do, so plumbing bugs surface for runner minutes
instead of across paid dispatches. `integration-test.yml`'s scenario roster
above is the checklist: a new paid surface without a scenario is an incomplete
change unless it ships an equally token-free dry-run mode of itself (the
`run:backtest` replay's stub engine is that shape, and stronger evidence than
a scenario would be), and the scenario ships in the same batch as the mode it
guards. A scenario that joins the promotion gate's **required** set moves the
run counts below and the gate's own scenario roster with it — both
maintainer-gated surfaces, so that batch is a maintainer-merged one by
construction.

The `deploy-environment` input names which deployment environment supplies the
role and remote variables, and by default resolves from the dispatching branch:
`main` dispatches use `prod`, and dispatches from `staging` use the `staging`
environment, which holds the same read-only role and remote variables plus its
own engine keys; any other branch resolves its own name — an unconfigured,
empty environment with no role variables and no keys — and an explicit choice
(the input is a closed `auto`/`prod`/`staging` vocabulary) still wins. Each
environment stays pinned to its one branch.
That is what lets a change's read seams run against real infrastructure once it
is on `staging` and before it is promoted — the capability the trigger path
structurally cannot provide.

What those staging-bound runs read is production's corpus today, and is meant
to become the **staging corpus**: a lean slice of real cases in its own
bucket/prefix pair, seeded by the dispatch-only `staging-corpus-refresh`
workflow (`fedcourts corpus-seed-slice`), so orchestration and the read/write
seams get live verification for runner minutes without anything gaining write
access to production. The scenario lane does not read it yet — a consumer
resolves the committed pointer, which names the production blob, unless the
out-of-band pointer override names the staging one (*Developer access* in
[data-pipeline.md](data-pipeline.md)), and the scenario jobs' environment
supplies no override — so provisioning it, and the repointing that remains,
are the staging corpus runbook in [security.md](security.md). Changed seams are therefore validated after the
merge to `staging` rather than on the PR branch; nothing broken reaches `main`
regardless: the gate needs the nine required integration runs — all seven real
scenarios, with engine-smoke counted once per engine, or one green
`scenario=all` run, which covers all nine because it succeeds only when each of
its eight matrix legs and its collect job does — green at exactly that staging
head, and `promotion-gate` is a required check on `main`, so it is
branch-protection-enforced rather than advisory. A `promote` dispatch carrying
`skip_engine_smoke` narrows what *that pre-flight* asks for to the six
token-free scenarios, taking a green `scenario=all-offline` run as their
whole-suite evidence — never by default. It decides nothing about the merge:
waiving the smokes at the required check is a second, separate act, the
`promote:skip-engine-smoke` label on the promotion PR, and the batch that
carries it merges with no real-engine evidence at its head sha (*Promotion:
staging → main* in [pipeline.md](pipeline.md) carries the trade). Unlabelled —
the default — the nine stand between a batch and `main`.

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
cell, copy its `prediction.json` / `reasoning.md` — and its `predicted_reasoning.md`
if the cell wrote one — under `tests/cassettes`). A cassette carrying no
`predicted_reasoning.md` replays as a prediction that names none, which is what makes
the committed cassette double as the fixture for that valid shape.

**A fixture corpus.** A tiny synthetic corpus, built deterministically by
`fedcourts make-fixture-corpus`, stands in for the S3-hosted corpus so
`provision-snapshot`, `query`, and `open-events` — and therefore the whole cascade —
run with no remote, no role assumption, and no tokens.

**A one-command cascade.** `fedcourts local-cascade --court <id> --docket <id>`
chains provision → predict → evaluate (blinded, then un-aliased) → `validate` over the fixture corpus:

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
regressions the stub can't see — not the inner loop. One step earlier,
`fedcourts predict-plan` / `evaluate-plan` ([cli.md](cli.md)) report the cell
set a fan-out **would** mint, step by step and spending nothing, so a change
that claims to protect a re-run is checked by executing it rather than by
reading the diff.

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
actions, least-privilege permissions). CodeQL
([`codeql.yml`](../.github/workflows/codeql.yml)) runs the `security-and-quality`
suite over the Python package on pushes and PRs to both integration branches —
including `py/implicit-string-concatenation-in-list`, the dropped-comma guard
AGENTS.md leans on — with results in the Security tab rather than a required
check. Beside them, a family of pytest
workflow-shape tests pins the YAML *contracts* the linters cannot see — the
label-trigger authorization shape (`test_workflow_auth_gate`: every gated
workflow's gate is the tested `authorize-trigger` command, nothing but a
credential-free checkout and the env sync may precede it, nothing
privileged runs ahead of it, and every gate pins the Bot allowance to the
data App's login), the
bot allowlists (`test_workflow_agent_bot`), the promotion-gate couplings
(`test_workflow_promote`), the collect scenario's partition
(`test_workflow_collect`), the cell invariants
(`test_workflow_cell_invariants`: the qp-topics oracle fence, the corpus-split
env pair, the forward leakage guard, the run-surface retry with its inline
copies and its still-fatal handoff writes, the 10-input `workflow_dispatch`
cap the UI enforces silently, the fail-closed shape every input gate must have
on a scheduled workflow, and the word-for-word pairing between each fail-fast
validator and the step of record that re-checks it), and the predict plan job's stranded-run
guard (`test_workflow_plan_census`: the census runs before the matrix step and
feeds it, degrades open rather than failing the job, and lets a fully-superseded
run close with the recovery note) — so deleting a load-bearing line fails a
named test instead of passing every linter. For a heavier local check of the
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

## Investigating a real docket without credentials

Diagnosing a provisioning or document-selection bug usually looks like it needs
the remote corpus, and often it does not. Two facts make a specific docket
investigable from a checkout with no S3 access and no CourtListener token:

- **A local `corpus.db` carries `docket_number`**, so a case id
  (`scotus/<internal id>`) resolves to the Court's own `<term>-<serial>` docket
  number with a point query — no remote read.
- **The supremecourt.gov per-docket JSON is publicly fetchable**, at
  `https://www.supremecourt.gov/rss/cases/JSON/<term>-<serial>.json`
  (`supremecourt.DOCKET_JSON_URL`). That is the authoritative record the live
  channel ingests, so it answers what the pipeline *should* have seen: the
  proceedings text, the distribution history, the filed-document links.

Together those cover most "why did this cell get the wrong documents" questions
directly against the real docket. Reach for a corpus pull only when the question
is genuinely about the *stored* row rather than the upstream record — and
remember the local blob is a snapshot, so its freshness is whatever the last
pull left behind (`fedcourts corpus-info` prints those dates, and AGENTS.md
asks any corpus-dependent claim to state them).

## The boundary that remains

Even with the harness, two things stay outside the fast loop by design, and that is
correct: **model judgment** (the stub is clean by construction, so prediction
*quality* is only seen in a real run) and **secret-bound infra** (the live API, the
S3 remote, the App token). Treat both as deliberate, infrequent checks — a real
`local-cascade` run and a manual workflow dispatch — rather than gaps to close. The
goal of the harness is not to run everything locally; it is to make the *common*
change — to a prompt, a schema, a cell's plumbing, an orchestration step — fail fast
on a laptop instead of in CI.
