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
into its own `cert@cvsg` block. One further round drives the evaluate lane's own
**backlog derivation** rather than a named case list: it predicts with the judges
held off, derives the
matrix from the evaluate backlog (`evaluate-matrix` with no `--body-file`, as the
plan job does), grades the cells that derivation planned, and requires the
re-derivation to come back empty — the backlog drained, which is the lane's resting
state. Run them all with `uv run pytest -k cascade_smoke`.

The `test` stage runs the suite **in parallel**, one `pytest-xdist` worker per
available CPU. No test depends on state another test left behind: the process-wide
caches are reset per test by autouse fixtures in `tests/conftest.py`, and everything
else a test needs — corpus, data root, working directory, environment — it builds for
itself under `tmp_path` and `monkeypatch`. So a test may land on any worker. The stage
distributes with xdist's `loadgroup`, which spreads per test as the default `load`
does and additionally honours `@pytest.mark.xdist_group`, so a test that ever does
need to run beside its siblings on one worker can say so where it lives instead of
needing the gate changed underneath it. Coverage is unaffected: under `GATE_COV=1`
each worker measures its own slice and pytest-cov combines them into the single
`.coverage` file the CI job's summary step reads.

Parallel workers are the wrong shape for debugging one failure — a worker has no
terminal for `breakpoint()`, and output from several interleaves — so the worker count
is overridable, and `1` drops xdist entirely:

```bash
GATE_TEST_WORKERS=1 scripts/gate.sh test   # serial, debuggable
GATE_TEST_WORKERS=4 scripts/gate.sh test   # pin the count instead of per-core
uv run pytest tests/test_salience.py       # a bare pytest run is serial anyway
```

A test that fails only under parallelism is a test leaking state, not a reason to
serialize it: give it its own `tmp_path` root rather than a shared one. An
`xdist_group` mark is for the case isolation cannot reach — a genuinely external
shared resource — and carries the reason in a comment beside it. The suite needs
none today.

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

**The agentic stages** — `run-predict` and `run-evaluate` —
are the gap. They invoke a coding agent (`anthropics/claude-code-action` and the
Codex equivalent) *inside the workflow*, so without a harness the only feedback on a
change to a prompt, the snapshot provisioning, or a finalize step is "open a PR,
have a maintainer dispatch the lane and release the `review` hold, wait for
Actions, read the logs" — slow, token-spending, and human-gated.

**Infra-bound integration** — the live CourtListener REST API, the corpus pull
from S3 over OIDC, the GitHub App token, issue comments — is deliberately
*not* part of the fast loop. It is exercised by dedicated paths and occasional
manual workflow dispatch, never on every iteration.

That infrastructure has a dedicated path:
[`integration-test.yml`](../.github/workflows/integration-test.yml) (manual
dispatch plus one daily canary, read-only role — the collect scenario none at
all — side-effect
free but for the application-repro leg's watchdog telemetry row) runs one
scenario per dispatch, or — `scenario=all` — the
promotion gate's whole required suite as one run (every required scenario, with
engine-smoke and engine-actions-smoke once per engine each, so three cells'
token spend plus three boot probes; collect rides the
run as its own environment-free job beside the matrix). `scenario=all-offline`
is that suite minus the six token-spending engine legs; the jobs that remain are
identical, environment binding included, and the run is token-free end to end.

The **canary** is the workflow's one scheduled arm (11:53 UTC daily): the three
`engine-actions-smoke` legs and nothing else, so a provider-side or action-side
flip between promotions is found by a cron rather than by the next paid round.
It runs from `main` and binds `prod`, and its run title carries no
`<scenario> / <engine>` pair — three independent reasons it can never satisfy
the promotion gate's freshness match for legs a promotion has not paid for.
GitHub cron is best-effort and drops runs under load, so a missed day is
tolerable by design: the canary shortens the window between a flip and its
discovery, and the gate, not the canary, is what stands between a broken
invocation and `main`.

The corpus-reading scenarios all run on **one case, settled once** by the
`plan` job before the matrix fans out. Left at its empty default, the `docket`
input means *resolve one*: `fedcourts corpus-integration-case` reads whichever
corpus this dispatch's environment serves and returns the first
snapshot-bearing, in-scope, still-predictable case — the shape every leg needs,
asked of the same record gate the provisioning guard applies. That is what a
static default cannot be, since each deployment environment resolves its own
corpus pair (a case in the production corpus is absent from the lean staging
one) and any case drifts out of shape as its docket resolves. The resolution is
echoed to the run summary, so a run always names its subject, and a corpus with
no usable case fails the plan job — before the engine-smoke legs spend
anything.

The primary candidate window is driven from the **blob's** snapshot index,
which is what bounds it, so a pair whose blob carries no snapshot rows leaves it
empty — a slice written *entirely* split-on is exactly that, the staging pair
included ([cli.md](cli.md)'s `corpus-integration-case` row has the full rule).
There a **second window** answers instead: the same still-predictable rows out
of the index, in the same order, with content-store snapshot presence probed per
candidate (a key listing, no payload fetch). Same screens either way, so a
staging-ref dispatch self-resolves exactly as a `main` one does, and the run
summary names which window answered. That window is not self-bounding, so it
stops at a stated candidate count and refuses loudly, naming both windows.

A non-empty `docket` pins a case instead and skips the resolver. It stays an
override, never a requirement: for aiming a dispatch at one particular case, or
for a corpus neither window can answer out of. Any refusal is immediate — the
plan job, before any leg runs.

`ranged-reads` is the tested `fedcourts corpus-integration-check`
read set — a point lookup, a priors retrieval, a snapshot provisioning —
against the real remote blob for that case, asserting every read comes back
non-empty, reporting per-read GET/byte counters to the run summary, and
exiting non-zero on a blown wall-clock budget. `corpus-service` launches the
same corpus sidecar composite the cell workflows use — with the same corpus
base URL, so the sidecar hydrates from the content store that address derives
exactly as the fleet's does — and probes it through the exact CLI
surface a cell retrieves with. `stub-cascade` first runs the production
`provision-snapshot --mode forward --refuse-terminal` command against the
settled case in an isolated data root, failing the leg on a refusal (the same
command is `continue-on-error` in run-predict, so this is where a guard
drifting to always-refuse surfaces; the case must be genuinely
open — snapshot non-terminal, corpus event unresolved, row undecided, no
committed outcome — since the guard reads the record as well as the snapshot,
which is exactly the gate the resolver asks on the dispatcher's behalf, and the
obligation a pinned case carries by hand), then runs one offline stub
`local-cascade` cell over the ranged
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
the unit suite instead (scope, the `--all` measurement form and its flat row
ceiling, the content-store path under the split, and the batch derivation the
scoped form cuts — determinism under a shuffled frame, the reference
force-include, the stratified fill's proportions, exclusion of already-published
rows, a frame clearing over repeated dispatches without relabeling a row, and
the converged and under-coverage refusals — all over corpora and frames built in
`tmp_path`), and the model call is exactly what `run-analytics` pays for.
`engine-smoke` is the first of the three token-spending scenarios: a single
real-engine
predictor cell (the `engine` input picks which — an `all` dispatch ignores it
and runs one smoke per engine; one predict cell's spend
against the run's open-event case — a resolved event also replays
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
still the cell's.

`engine-actions-smoke` is the second, and it answers the question the engine
smoke cannot. That leg drives the bare CLI through the tested runner seam,
while a production cell reaches its engine through an **invocation block** —
`claude-code-action` and `codex-action` at pinned shas, and for gemini the CLI
step `run-predict` writes out (that engine has no pinned action: the upstream
one `uses:` unpinned actions the org's SHA-pinning policy rejects). A refusal
raised in an action's own validation layer fires *before any model call*, so
the runner-driven smoke passes it unseen and it surfaces first in a paid
production cell. An action version bump is the live case: it changes what the
action does with inputs the cells have always sent, and nothing else in the
gate executes an action. A static comparison of the invocation surfaces cannot
see that class either — a bump moves every pin consistently, and only running
the action shows what it does with them. So this
scenario sends each engine the cell's own block on a prompt that asks for a
single word and asserts **acceptance** — that the invocation was taken and a
turn completed — never output quality. One boot probe per engine, per leg
(the recurring cost is a line in [budget.md](budget.md)); the fidelity of the
blocks is the whole claim, so the codex one is held in lockstep with both cell
workflows' by a test, and the two deliberate deviations — the kickoff prompt,
and handing claude the job's read-capped token instead of minting the cells'
App token — are marked in the workflow where they are made.

**The repro family** is the third token-spending class, and it exists because
the two above share a blind spot: the resolver applies no stage screen, but
what it settles on in practice is a cert-stage petition, so a defect keyed on
a *record shape* they never present is invisible to them however green they
run. Each member pins one record to the shape one diagnosed engine defect keys
on and runs a real cell against it, and the leg's own failure is the finding.
`codex-application-repro` is the first: one `codex-judge` evaluate cell —
`run-evaluate`'s codex step, its `with:` block held in lockstep with the cells
by the same test the actions smoke is — against an **application-lane** record,
a SCOTUS interim docket (the `YYAnnn` application-number lane) whose event trio
— motion / order-response-requested / brief-response — is committed here and
whose snapshot and application-kind document the leg provisions at run time,
staged exactly as a production judge cell is (snapshot and documents
provisioned, event materialized, candidates blinded, de-blinding surfaces
hidden). Its provisioning step asserts the application document is actually
there, so a corpus that stopped serving one fails the leg rather than letting
it certify an ordinary record — which also means the leg needs an environment
whose corpus carries the pinned docket, and reads as red when it does not.

Three properties are the family's, not this member's. The record is **pinned in
the scenario's own steps**, not taken from the `court`/`docket` inputs: the
record is what the scenario is, and a dispatcher who could re-point it could
make a red leg mean something else. The bounds sit **above the work envelope**
— a 70-minute watchdog deadline inside an 80-minute step backstop inside a
95-minute job cap for this leg, against a judge cell on this record shape that
runs 40–50 minutes on production cells and has been observed still mid-work
past 50 on this leg — because the defect being reproduced begins only *after*
the agent finishes: a bound inside the envelope kills a healthy mid-grading
cell and never reaches the teardown phase the leg exists to observe, and the
deadline kill can end the whole *job*, which skips the disarm and upload tail
and drops the log. That is also why the leg arms the **off-runner record** the
production codex cells keep — the comment-only telemetry channel on the
`codex-watchdog` issue — so a deadline path that destroys every runner-local
account still leaves one a cancelled job cannot erase. Two bounds on that
record, both stated where they bind: the mint's credentials live on the `prod`
environment, so a leg bound elsewhere arms no record and warns; and the token
lives an hour, so on the deadline path the record may end at its last
pre-expiry heartbeat — the armed row's fire ETA is what makes that frozen tail
readable as the deadline path. Each heartbeat carries the runner's memory
headroom and load, and a send whose failure diagnosis is new appends what it
looked like from the runner — the transport and HTTP result, plus a bounded
probe of the check-in host where the transport itself failed — to the body
the next landed send uploads whole. What that buys: the resource trajectory
up to the last landed beat, transport separated from HTTP in every failure,
and the full failure history on any recovery; a record that stays frozen
remains ambiguous between a dead watchdog process and a channel that never
came back, which only a landed later send can split. What must stay well
inside the job cap is the watchdog, since a job that runs to its cap is
*cancelled* and GitHub drops a cancelled job's logs. The leg arms the
**completion sentinel** too, so on a reproduced hang it is the *reap* that
fires — about five minutes after the cell's last write, the quiescence grace — and its capture, a
process forest and socket table taken while the work is already done, is what
names the holder. Read the markers accordingly: `REAPED` is the defect
reproducing and being handled, while `FIRED` or `STOOD_DOWN` says the completion
set was never satisfied — work still running at the deadline, or a required file
the judge never wrote — which is a finding about the cell rather than about
teardown. The bundle and the rollout's item shapes ride the run's artifact either
way. The leg reports **two halves separately**, because
the finding is that they can disagree: `outputs:` counts the cell's produced
files against the same `cell-outputs` list the watchdog's sentinel waits on, and
`step:` says whether it concluded on its own, was reaped by the watchdog, or did
not conclude — so a future regression is legible as which half broke. And the
family is **dispatch-only and observational** while its defect is open: no whole-suite
selection fans it out, and it is absent from `REQUIRED_SCENARIOS`, because a
defect reproducing on cue inside `all` would redden the run the promotion gate
matches on and block the promotion carrying the fix. A member whose defect is
closed becomes the regression test that keeps it closed, and joining the
required set is the deliberate maintainer edit described two paragraphs below.

Dispatch a scenario around the changes it guards: **before and after any
change to corpus access** (the read seams, `corpus_ranged`, the sidecar
composites, the blob's physical layout) **or to a corpus-consuming workflow**,
**engine-smoke around any engine CLI version bump or sandbox/permission/config
change, and engine-actions-smoke around any bump to an engine action, to a
cell's `with:` block, or to the codex permission profile the cells select**,
**collect around any change to the `collect-run` composite or the collect
jobs that call it**, **qp-topic around any change to the `qp-topic-measure`
composite, the labeling job, or the `qp_topics` module — and before any paid
labeling dispatch**, **a repro-family scenario around any change aimed at the
defect it reproduces, and once after the promotion that carries the fix**, and
as a preflight **before a release dry run** and
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
`run-backtest` replay's stub engine is that shape, and stronger evidence than
a scenario would be — on its scheduled path, where the engine is pinned to
`auto`, the token-free rehearsal is the cadence's own `plan` job, which pulls
the corpus and renders what a release would spend without running a cell), and
the scenario ships in the same batch as the mode it
guards. A scenario that joins the promotion gate's **required** set moves the
run counts below and the gate's own scenario roster with it — both
maintainer-gated surfaces, so that batch is a maintainer-merged one by
construction.

The `deploy-environment` input names which deployment environment supplies the
role and corpus base URL, and by default resolves from the dispatching branch:
`main` dispatches use `prod`, and dispatches from `staging` use the `staging`
environment, which holds the same read-only role and corpus base URL plus its
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
regardless: the gate needs the twelve required integration runs — all eight
required scenarios, with engine-smoke and engine-actions-smoke counted once per
engine each, or one green
`scenario=all` run, which covers all twelve because it succeeds only when each
of its eleven matrix legs and its collect job does — green at exactly that
staging head, and `promotion-gate` is a required check on `main`, so it is
branch-protection-enforced rather than advisory. A `promote` dispatch carrying
`skip_engine_smoke` narrows what *that pre-flight* asks for to the six
token-free scenarios, taking a green `scenario=all-offline` run as their
whole-suite evidence — never by default. Both engine families leave together,
and must: the whole-suite acceptance the skip unlocks is decided before the
required set is read, so keeping one family required while accepting an
`all-offline` run — which ran neither — would satisfy that requirement without
exercising it. Unsound, not stricter. It decides
nothing about the merge:
waiving them at the required check is a second, separate act, the
`promote:skip-engine-smoke` label on the promotion PR, and the batch that
carries it merges with no evidence at its head sha that a real cell runs or
that its invocation block is still accepted (*Promotion:
staging → main* in [pipeline.md](pipeline.md) carries the trade). Unlabelled —
the default — the twelve stand between a batch and `main`.

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
tests, not inline script), as do the predict/evaluate decisions: whether a cell
produced its own
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
trigger surface (`test_workflow_auth_gate`: no workflow in the directory takes a
privilege-reaching trigger an actor without repository write can fire — the
exception, `pull_request` on CI, the linters and CodeQL, is held to a shape that
makes it moot: no environment, no secret, no token mint, no role — the privileged lanes carry
nothing but the platform-gated `schedule` and `workflow_dispatch` and keep the
dispatch their recovery path depends on, every privileged job binds a deployment
environment so a dispatch cannot run it from an arbitrary ref, and every agent
job waits on the `review` hold), the
bot allowlists (`test_workflow_agent_bot`), the promotion-gate couplings
(`test_workflow_promote`), the collect scenario's partition
(`test_workflow_collect`), the cell invariants
(`test_workflow_cell_invariants`: the qp-topics oracle fence, the corpus base
URL, the forward leakage guard, the arm/disarm bracket, sentinel and deadline of the
engine hang watchdog — whose bracket must wrap *every* engine step with no other
step between them, whose arm-step env is pinned as an exact set, so a
`WATCHDOG_*_MATCH` slipped in later fails rather than silently re-aiming the
kill, whose completion sentinel is pinned to this cell's own role, to a bounded
resolution and to reaching the watchdog as environment rather than as a file the
agent could rewrite, whose reaped cell must reach `AGENT_OK` (or the fix would
convert destroyed work into demoted work) off a flag read from runner temp, and
whose comment-only telemetry mint is pinned to `issues: write`, to the codex
engine step's own gate, to the two steps that may hold it, and to
`continue-on-error`, since a mint that failed hard would skip the engine step —
the run-surface retry with
its inline copies, the absence
of any step that applies a fan-out label, the 10-input `workflow_dispatch`
cap the UI enforces silently, the fail-closed shape every input gate must have
on a scheduled workflow, and the word-for-word pairing between each fail-fast
validator and the step of record that re-checks it), and the predict plan job's stranded-run
guard (`test_workflow_plan_census`: the census runs before the matrix step and
feeds it, degrades open rather than failing the job, and lets a fully-superseded
run report the recovery note instead of a drained backlog) — so deleting a load-bearing line fails a
named test instead of passing every linter. Two of the family go further and
*run* what the YAML embeds, because a workflow string is matched against the CLI
for the first time when the job runs: `test_workflow_repair_cli_parity` reads
each of `run-repair`'s thirteen dispatch-only maintenance passes back out of the
workflow — argv, conditional flag arrays and all, via the shared reader
`tests/workflow_argv.py` — and executes it against the fixture corpus, so a
renamed flag fails here rather than as a usage error mid-dispatch (its qp
test also replays the pass's convergence re-run over a seeded corpus and
asserts the workflow's grepped literal against the summary the CLI prints —
the one coupling that lives in output wording rather than argv); and
`test_collect_issueless` executes the collect composite's own `collect-plan`
call with the sentinel it normalizes an absent issue number to, which is the
path every round takes, since no lane supplies one. `test_engine_watchdog` does
the same for the cells' hang bound: it runs `scripts/engine-watchdog.sh`
against processes whose command lines and parentage stand in for a wedged
engine, for the step that outlives its engine's death, and for the step that
never spawned one at all, because every claim about that guard is a claim about
process matching and signals on a live runner, and a wedge otherwise destroys
its own evidence. Its **completion sentinel** half is driven the same way, over
files rather than processes: a fixture cell whose required outputs are all
written has its wedged step reaped without waiting for the deadline, while a set
that is one file short, one that does not parse, one still being rewritten, and
one whose output directory does not exist yet each leave the reaper off and the
deadline as the only bound — the four ways a reap could destroy work in
progress, and the conservative direction is what each of them pins. Its safety half is the part worth reading: each discovery
route is pointed, in its own test, straight at a fixture wearing
runner-infrastructure arguments, which must survive — signalling the runner's
own worker force-kills the job the watchdog exists to save — and two more pin
the ends of the window that decides *which* step is the guarded one. Every
process the suite signals is one it spawned: the discovery patterns are
fixture-scoped and asserted to be, so it cannot reach the step running it. Its
off-runner half is driven too, against a localhost sink standing in for the
telemetry comment's REST endpoint: the PATCH sequence through arm, heartbeat,
deadline, discovery tally, fire and escalation; that every PATCH extends the
armed record rather than replacing it, so the fire ETA and the run link survive
the first heartbeat; the payload's strictness (no argv, no runner path, and no
token — which reaches the sink's Authorization header and not the watchdog's own
log, which rides the published artifact); and that a watchdog handed no check-in
URL still kills on the same terms. `test_watchdog_telemetry` covers `fedcourts
watchdog-checkin` beside the latch it is built on and off the same injectable
`gh` seam — find-or-reset, the recency window that makes the page bound search
the right end of a long-lived issue, the App-authorship test that stops a
stranger pre-claiming a record on a public repo, the channel routing (the
staging rehearsal channel's own label and issue, the production default, and
the pre-write refusal of an unregistered channel), and the
exit-zero-with-a-warning
contract a degraded API has to keep. For a heavier
local check of the
deterministic jobs (the `plan` job, matrix generation, the collect seam),
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
