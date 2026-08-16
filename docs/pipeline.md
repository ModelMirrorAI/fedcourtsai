# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. A stage hands off by creating/labeling an issue for the next
stage.

| Label           | Workflow         | Trigger(s)                          | Engine(s)            |
|-----------------|------------------|-------------------------------------|----------------------|
| `run:pull`      | `run-pull`       | daily schedules (pull + live jobs), label, manual (+ dispatch-only `enrich-opinions` mode) | script (no agent)    |
| _(none)_        | `run-seed`       | daily schedules (4 dead-zone windows), manual | script (no agent)    |
| `run:predict`   | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex + Gemini |
| `run:evaluate`  | `run-evaluate`   | issue labeled                       | Claude Code + Codex + Gemini |
| `run:backtest`  | `run-backtest`   | issue labeled, manual dispatch (replay/engine/limit/terms params; `replay: salience-gate` runs the token-free gate replay instead of the predictors) | Claude Code + Codex + Gemini (replay) |
| _(none)_        | `run-ops`        | daily schedule (+ a weekly digest tick), manual | script (no agent)    |
| _(none)_        | `run-analytics`  | manual dispatch + weekly schedule   | script; the `qp-topic-label` mode runs one Claude Code labeler |
| _(none)_        | `integration-test` | manual dispatch                 | script; the engine-smoke scenario runs one real agent cell |
| _(none)_        | `promote`        | manual dispatch                     | script (no agent)    |
| _(none)_        | `sync-staging`   | daily schedule + manual dispatch    | script (no agent)    |

`run-ops` is not part of the issue cascade: it is a read-only daily roll-up of
operational analytics, consolidated so it reads as a summary — pipeline health
(the Actions run history, dormant workflows folded into one line), **substance**
(is the machine producing: scored cells by stratum with deltas against the
week-old snapshot when one exists — else the newest,
replay calibration vs the modern-cert deny base rate with the sample size beside
every number, per-predictor evaluation-score distributions, and live-frontier
readiness — each sub-block shown only once its feed exists), **spend & cost**
(the `usage.json` ledger + Actions minutes from run durations), **agent signals**
(the committed `flags.json` / `tooling.json` and evaluator leakage gradings,
scoped to a recent window so old, fixed flags age out of the summary — the
`agent-feedback` issue and the raw ledger still keep every flag), and **open
trigger issues** (still-open `run:*` fan-out triggers = stalled runs, oldest
first, so an orphaned issue never sits invisible) — rendered by
`fedcourts ops-report`. It surfaces the current view in one long-lived "Ops
dashboard" issue and appends each JSON snapshot to a dedicated **`ops-metrics`
branch** (an orphan time-series that never merges to `main`, so the default
branch stays clean and a prior snapshot backs the substance deltas). On the
Monday schedule tick it additionally posts the short **weekly digest** comment
to the dashboard issue — the same numbers as fixed questions demanding a
reaction ("Replay calibration on N scored cell(s): lift over always-deny — do
you believe it?"), with the daily dashboard staying the reference view. It triggers
nothing and touches neither `main` nor the corpus. It reports the **promoted**
state: scheduled runs execute from the default branch, so the dashboard describes
the tree that is actually running rather than the one staged for the next batch —
and the lag is confined to code and config, since the substance and spend
sections read `data/` and `metrics/`, which the writers commit to `main`
directly. One reading note the dashboard now carries itself: `promote` is
level-triggered, so its failures are unsatisfied-gate reports rather than
incidents, and its success rate counts promotion attempts.

It is also the **presenter** of the published corpus-side artifacts (see *Data
validation* in [data-pipeline.md](data-pipeline.md)): the corpus-writer path
produces a correctness verdict and the live-frontier readiness snapshot where
the corpus is already pulled, and `run-ops`
renders them as the **data-health** section and the substance section's
watchlist view, escalating a failing verdict to one
long-lived issue — so the dashboard surfaces run-health, data-health, and
substance while staying a read-only presenter that never touches the corpus.

`run-analytics` is the **corpus analysis & derived metrics** surface, also outside
the cascade: every task that reads the corpus and answers a question or refreshes a
derived artifact is a mode here (dispatch `mode` input, or the weekly schedule),
each as its own least-privilege job holding only the credentials its mode needs:

- **`corpus-stats`** (dispatch) assumes the read-only S3 role, pulls the
  corpus (`fedcourts corpus-pull`), and runs `fedcourts stats` to aggregate disposition base-rates (overall,
  filtered to one SCOTUS Term via the `term` input, or grouped by court / topic /
  judge / SCOTUS Term / disposition / originating circuit / decade era, with a
  cert-stage cut restricted to modern discretionary-cert dockets). Read-only: results go
  to the Actions step summary and run log, nothing else.
- **`metrics-refresh`** (weekly schedule, or dispatch) keeps the committed metrics
  artifacts from drifting stale: `metrics/claim-scores.json` (input: the `data/`
  evaluations ledger), `metrics/leaderboard.json` (the same ledger plus the
  committed `metrics/statpack.json`, which its realized-Term skill column is
  scored against — so it regenerates *after* the pack)
  and `metrics/backtest.json` / `metrics/statpack.{json,md}`
  (input: the corpus) are deterministic stage commands that otherwise change
  only when someone reruns them locally. It reruns those tested
  `fedcourts` commands and — only when an artifact actually changed (they are
  byte-stable, so a no-op refresh diffs empty) — opens a **reviewed** PR rendered
  by the tested `metrics-refresh-plan` command: never a
  direct commit to `main`, never auto-merged. It mints the dev App token to do
  so; `qp-topic-label` below is the only other job here that does. The branch is fixed
  (`metrics/refresh`) and force-pushed, so an unmerged refresh PR is updated in
  place by the next tick rather than stacking.
- **`tool-usage`** (dispatch) rolls every committed `retrieval_log.json` into an
  **offered-vs-called** report: which configured MCP tools were never called,
  which are used by some engines and not others, and call counts per tool /
  engine / actor. The same walk adds per-engine result observability (whether an
  engine's transcript captures the answer side at all), cuts by mode / role /
  actor, calls beside each cell's estimated cost, and call volume against the
  evaluators' Brier scores — that last one scoped to blessed processes like any
  grade-bearing surface, and a denominator table with an under-powered verdict
  until a population clears the cell floor its module pre-declares. The dispatch
  takes the default scope, so while no committed cell is inside the freeze the
  usefulness section renders as empty and says so; the diagnostic read over every
  process version is `fedcourts tool-usage --all-versions`, run locally. It reads
  `data/` only — no corpus, no network — so it binds no
  environment and assumes no role, and the same `fedcourts tool-usage` runs
  locally and in the gate. Results go to the step summary; it commits nothing.
- **`qp-topic-label`** (dispatch) runs the `qp-topic-v0` topic labeler over every
  questions-presented text the pulled corpus carries and lands the measured
  per-case labels file
  (`data/qp-topics/qp-topics.json`) as a **reviewed** PR to `main` — fixed
  branch `qp-topics/refresh`, force-pushed, never auto-merged. It is the only
  mode that runs an agent, and therefore the only one **split across two jobs**,
  because `corpus-readonly` exports the assumed role's credentials job-wide:
  `qp-topic-extract` holds the read-only S3 role and writes the extract
  (`fedcourts qp-corpus`, under `$RUNNER_TEMP` — the command refuses an `--out`
  inside the checkout) to a one-day Actions artifact; `qp-topic-label` assumes
  no role at all, downloads that artifact, and runs the labeler with no cloud
  credential in its environment and no MCP config (the vocabulary is text-only,
  so the extract is the agent's entire evidentiary input). The labeler's
  turn-by-turn transcript is scanned and published as a second one-day
  artifact, `qp-label-transcript` — the thing to open when a run reports
  success but writes no labels (disclosure argued in
  [qp-topic.md](qp-topic.md)). It applies the same
  structural prohibition the cell workflows do — `data/qp-topics/` is moved out
  of the tree for the duration of the agent step, since reading the reference
  set would not improve the labels, only destroy the measurement — and restores
  it from the commit afterwards, then asserts the tree is otherwise untouched
  (the gate constants live in the checkout too). After the agent, the
  tested `fedcourts qp-topics` measures the labels against the hand reference
  set and enforces the agreement/coverage gate — below it, nothing is written,
  the measured block still reaches the step summary, and the job fails. The
  `label_model` dispatch input picks the labeler's model. See
  [qp-topic.md](qp-topic.md).

`integration-test` is the infrastructure preflight, also outside the cascade:
a manual-dispatch, strictly side-effect-free scenario runner over the **corpus
read backends, the two sidecars, cascade cells, the collect writer, and the
qp-topic measure path**,
against the real corpus remote for every scenario but collect and qp-topic —
the tested `fedcourts corpus-integration-check` read set, a
cell's-eye probe of the service sidecar, the tokenless CourtListener MCP
sidecar under the tested `mcp-integration-check` client, a stub
`local-cascade` cell, the `collect-run` composite over synthetic cell
artifacts (corpus-free and environment-free; every write surface stubbed or
diverted on the runner), the `qp-topic-measure` composite over canned labels
built from the committed reference set (token-free and credential-free), or
(the one token-spending scenario) a single real-engine cell over the service
sidecar — dispatched around changes to corpus access, the sidecars, engine
CLIs, the collect contract, or the corpus-consuming workflows and before
releases — from main, or via the `staging` deployment environment (collect
binds none; qp-topic binds one it never reads) from the `staging` branch, which
is the only branch that environment accepts (those runs are the promotion
gate's freshness evidence; see *Promotion: staging → main* below). The deployment environment resolves from
the dispatching branch by default — `main` gets `prod`, `staging` gets
`staging`, any other branch an empty environment holding no role variables
and no keys — and a `scenario=all` dispatch
fans the gate's whole required suite (every real scenario — collect rides the
run as its own environment-free job — with engine-smoke once per engine, so
three cells' token spend) out of one run. `scenario=all-offline` is that same
suite with the three engine-smoke legs dropped: token-free end to end, and
whole-suite evidence only for a pre-flight that skipped them (*The
engine-smoke skip* under *Promotion: staging → main* below).
See *Infra-bound integration* in [testing.md](testing.md).

**run-seed** runs the **historical Term walker** (supremecourt.gov, budget-free),
accumulating resolved outcomes reverse-chronologically by Term for the statpack's
per-Term base rates and the cert back-test set. It is a corpus writer split out
of run-pull so the backfill runs on a denser schedule (four dead-zone windows a
day); it shares the `corpus-write` concurrency group, so it still serializes with
run-pull's forward writers. **run-pull**'s **pull** job does targeted
CourtListener enrichment from the rate-limited **REST API** (the live job owns
SCOTUS freshness for free). One other consumer shares that REST budget:
**run-pull**'s dispatch-only **enrich** job (`mode=enrich-opinions`, sized by
the `max_cases` input) walks granted SCOTUS rows to their published opinion
cluster and lands the reporter citations and opinion body
(`fedcourts enrich-opinions`; scope and arithmetic in
[data-pipeline.md](data-pipeline.md)). It is the pass's only production lane —
never scheduled, and dispatched into a dead zone between pull windows so it
neither queues on the corpus-write lock nor stacks API spend onto a pull
window's. run-seed also runs seven
maintenance sweeps, each gated to one window a day and each converging rather
than one-shot — a re-run over an unchanged corpus does nothing. In order: the
**live-duplicate dedupe** (`fedcourts dedupe-live-rows`), which merges and drops
any SCOTUS petition carrying both a CourtListener-keyed row and a live-minted
reserved-range row — the pair shape a docket-number spelling leaves when it
defeats the channels' identity join; the **predict-scope reconcile**
(`fedcourts reconcile-scope`), which latches out-of-scope cases (the
shared exclusion rules — era, staleness, docket form, date consistency, and the
snapshot-aware bare opinion-import profile) in the corpus so they leave the
predictable set at the source; the **application-baseline relabel**
(`fedcourts relabel-application-events`), which converges application dockets
whose baseline event predates the motion/interim minting rule; the
**merits-judgment backfill** (`fedcourts backfill-merits-judgments`), which
parses each merits-bound grant's stored snapshot for the judgment entered,
feeding the statpack's merits section; the **merits-event backfill**
(`fedcourts backfill-merits-events`, preceded in the same step by the
moment-column stamp `fedcourts backfill-event-moments`), which mints the open
merits forecast events — corpus rows plus their ledger `event.yaml` files,
staged in the one pointer commit — onto granted, undecided dockets the live
mint never opened; and the **attribution repairs** (`fedcourts
remove-unmintable-events` then `fedcourts reopen-misattributed-outcomes`),
which converge the misattribution shape an earlier single-open-event
attribution shortcut wrote and its cause — removal first, clearing the
entry-pinned case of the reopen sweep's baseline-pair triage in the same
window, each bounded by a per-run blast-radius cap; and, last, the
**bulk-cluster scrub** (`fedcourts scrub-bulk-cluster-fields`), which
converges the stored circuit slice onto the ingest projection's carve-out —
the bulk export's misjoined cluster fields are withheld from a re-served
bulk row, and the scrub drops them from the rows nothing re-serves, keyed
on the fields no channel could have written to a non-SCOTUS row (the only
other writer, the opinion enrichment, is SCOTUS-scoped) and bounded by its
own blast-radius cap. The dedupe runs first so the
latch pass weighs deduped rows, and the event mint runs immediately after the
judgment backfill so pendency is judged on judgment columns as latched as the
stored snapshots allow; each then pushes the blob and commits the pointer like
any other corpus write. Two further writer steps are **not** among the seven and
never run on a schedule, each gated behind its own dispatch input and on the
dedupe succeeding. `unlatch-overselected` (the `unlatch_overselected` input)
clears the pre-resize `salience_selected`
overhang a capacity change leaves behind (`docs/salience.md`) — the latch's one
`1 → 0` writer, a
deliberate one-time act rather than a converging sweep, gated on the
dedupe so an unmerged twin cannot re-latch a cleared case.
`backfill-questions-presented` (the `qp_backfill` input) re-derives the stored
questions-presented rows under the current extractor: a `dry-run` dispatch
prints the reason-class triage ledger to the run summary and writes nothing;
an `apply` dispatch rewrites the safe classes, verifies its own convergence by
re-running the dry-run (under the corpus split the durable write is the
content store's, so the pointer alone cannot witness it), and pushes. The
dry-run ledger is a maintainer's reading, so the intended procedure is two
dispatches: `dry-run`, read, then `apply`. The full
design — sources, budget boundary, the
corpus/ledger storage split, and the historical corpus — is in
[data-pipeline.md](data-pipeline.md).

A Term walked to its frontier is invisible to every later run, so run-seed's
**manual dispatch** carries `refresh_terms` (blank by default, and blank on every
scheduled window) to re-open past Terms when the pipeline learns to read
something the walk did not capture. It runs `fedcourts refresh-historical
--apply` after the pull and before the loop, so the reset and the re-walk it
implies are one serialized operation under the `corpus-write` lock rather than a
local corpus edit racing a cron window. The reset reaches the remote only through
the loop's checkpoint push, so a failure before the first checkpoint leaves the
upstream cursors untouched. `refresh_streams` picks the numbering sequence: IFP
is ~70% of the probe cost and feeds no scored segment, so the paid stream is the
default.

## Cascade

```
daily ×4 → run-seed → walk Terms newest-first, ingest every decided petition
                              └─ checkpointed: corpus-push + pointer commit per chunk
   daily ×4 / run:pull → run-pull (pull job) → push fresh facts to the corpus
                                 ├─ refresh active cases (oldest-first, budget-capped)
                                 ├─ detect resolution → write outcome.json when the
                                 │  disposition is machine-readable (git ledger);
                                 │  else queue an unrecorded outcome, surfaced
                                 │  per-case on the pipeline-runs dashboard
                                 └─ create issues  ← APP TOKEN
                                    ├─ run:predict    (changed case with open forecastable events,
                                    │                  unless the docket already looks
                                    │                  decided — skipped + surfaced;
                                    │                  held if PREDICT_HANDOFF_ENABLED=0)
                                    └─ run:evaluate   (predicted event that gained
                                                       an outcome, or an owed grading
                                                       the backlog deriver surfaces;
                                                       held if EVALUATE_HANDOFF_ENABLED=0)
   daily ×4 → run-pull (live job) → push fresh facts to the corpus
                                 ├─ probe supremecourt.gov docket-number frontier
                                 │  → onboard new petitions + applications
                                 │    (per-(Term, stream) cursors)
                                 ├─ re-poll the live cert watchlist (recent Terms first)
                                 ├─ re-poll unresolved interim applications (capped;
                                 │    substantive + changed + in scope → predict handoff)
                                 ├─ detect resolution from the proceedings text
                                 │  → write outcome.json (git ledger); else queue an
                                 │    unrecorded outcome, surfaced per-case on the
                                 │    pipeline-runs dashboard
                                 └─ create run:predict / run:evaluate issues  ← APP TOKEN
                                    (held per-channel by PREDICT_HANDOFF_ENABLED /
                                     EVALUATE_HANDOFF_ENABLED)
       run:predict → plan (build matrix) → predict[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft for partials;
                                              a facts-only PR when a run lands nothing)
       run:evaluate → plan → evaluate[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft for partials;
                                              a facts-only PR when a run lands nothing)
```

Run logging creates nothing on the happy path. Every `run-pull` window (pull
and live, success or failure) that reaches checkout lands its row on the single
long-lived **Pipeline runs** dashboard issue — label `run-log-dashboard`,
non-triggering and never declared in an issue form's `labels:` (the same
discipline as every operational label here), edited in place like the Ops
dashboard, its state carried as a fenced JSON block in its own body
(`.github/actions/run-log-dashboard`): a rolling 14 days of window × outcome ×
handoff counts, plus the per-case unrecorded-outcome triage list. A window that
fails or is stopped mid-run (timeout or a human's cancel — the shared lock
never cancels an in-flight run; a stopped window gets only the alarm, no
dashboard row) opens (or reuses, for the same day) a `pull-log` / `live-log`
issue and leaves it open for a human — so an open run-log issue means exactly
"a window broke": the issue list is the alarm surface, the dashboard the
reference view, and neither depends on a later window firing to stay honest.

To run the predict → evaluate → validate cascade for one case **locally** — off
Actions, over the fixture corpus, offline by default — use `fedcourts
local-cascade` (see [cli.md](cli.md)). It reuses the same engine-runner seam and
registries, so a green local run mirrors a green CI run.

## ⚠️ The handoff token gotcha

Events created with the default `GITHUB_TOKEN` **do not trigger other workflows**
(GitHub's loop-prevention). So every cross-workflow handoff (e.g. run-pull creating
a `run:predict` issue) and every PR that must trigger CI is made with a **GitHub
App installation token** (`actions/create-github-app-token`), not `GITHUB_TOKEN`.
See `docs/security.md` for the one-time App setup.

## Authoring or changing a workflow

**Prefer a job or mode on an existing surface over a new workflow file.** GitHub
scopes permissions, secrets, and minted tokens per **job**, so a new job on an
existing workflow is exactly as least-privilege as a new file — a new file adds
surface area without adding isolation. A task earns its own workflow only when it
needs a different *trigger class* (the `run:*` issue-label cascade vs
schedule/dispatch) or a different *risk class* (the agentic fan-outs, the corpus
writers). Everything else — a new analysis, a new derived
artifact, a new maintenance sweep — should land as a mode/job on `run-analytics`
(or the closest existing surface), reusing the shared composite actions
(`setup-python-env`, `corpus-readonly`, `corpus-ranged`, `corpus-sidecar`,
`mcp-sidecar`, `configure-git-identity`).

When you add a new `run:*` workflow or edit one, the existing workflows are the
canonical reference — each handles these cross-cutting traps inline, so copy the
pattern rather than rediscovering it:

- **Concurrency is evaluated before the job `if`.** An `issues: labeled` event
  fans out to *every* workflow that listens for it, and the job-level label filter
  runs only after the concurrency group is assigned. A label-reachable corpus
  writer job (pull, live, historical — the dispatch-only enrich job never sees
  a label)
  must therefore join the shared `corpus-write` group **only** when its own label
  matched — otherwise an unrelated label cancels a real writer. See the
  `concurrency:` expression in `run-pull.yml`. To dispatch one of
  these reliably, prefer `workflow_dispatch` over labeling.
- **`git add data/` aborts when `data/` is absent.** No `outcome.json` is written
  on most runs, so `data/` often does not exist; under `set -euo pipefail` the add
  fails the step before the no-op guard. Stage the always-present pointer
  unconditionally and guard the rest with `if [ -d data ]; then git add data/; fi`
  (see `run-pull.yml`). The same shape lives in run-predict/evaluate.
- **Long-running jobs outlive their credentials.** A GitHub App installation token
  has a hard 1h life and an AWS OIDC session defaults to 1h. A corpus-writer loop
  must therefore stay within that hour, or re-mint the App token before it ages
  out and raise `role-duration-seconds` to cover the run. `run-seed`'s walk takes
  the first path: each window is a bounded chunk (≤40 min; the daily sweep window walks 25
  to fund its trailing sweeps) under one token, so it
  needs no re-mint — a deliberate simplification over a longer walk that would.
- **The runner is ephemeral, so fixed per-run costs are re-paid every run.** Build
  expensive shared state once per job and reuse it across a loop's chunks rather
  than per chunk.
- **A step that calls a cloud provider can hang far longer than it can fail.**
  `aws-actions/configure-aws-credentials` retries a failed AssumeRole 12 times by
  default, and an unreachable STS endpoint fails each attempt on a multi-minute
  TCP connect timeout rather than promptly — so the default policy outlasts every
  job budget here and the job is killed mid-retry instead of returning an error.
  A window is then spent entirely on hanging, and a `cancelled` result gets
  attributed to whatever the job was *supposed* to be doing. Every call site
  passes `action-timeout-s`; note that a composite action cannot put
  `timeout-minutes` on its own steps, so the action's own timeout input is the
  only bound available inside one. The same question is worth asking of any step
  that talks to an external service: what is its worst case, and is it shorter
  than the job budget?
- **The CI uv pin and the lockfile format are coupled.** `setup-python-env`
  installs with `uv sync --locked`, which refuses a lock it cannot read as
  current — so a lock written by a *newer* uv than the action's pin fails every
  job that installs dependencies, including the scheduled data runs, and the
  trigger is a local tooling upgrade rather than any dependency edit. The
  devcontainer's uv is not pinned to the same version, so relock with the pinned
  uv, or bump the pin in the same change. `scripts/gate.sh lock` catches the
  drift half of this locally; the version half only shows up in CI.
- **A branch built during a long job must be based on a freshly fetched remote
  tip, not the job's own checkout.** The deterministic writers commit to `main`
  throughout, so a matrix that runs for an hour finishes holding a stale local
  `main`; a branch cut from it carries commits that are no longer on the remote —
  including any merged `.github/workflows/*` change — into the push pack, and a
  token without `workflows` permission has the whole push rejected. `collect-run`
  carries the worked reasoning and the fetch-then-branch shape; copy it in any
  job that pushes a branch it built while other jobs were writing.

Validate any `.github/` change locally with the linters CI enforces (see the
local gate in [AGENTS.md](../AGENTS.md)), and run the **`workflow-reviewer`**
subagent (`.claude/agents/workflow-reviewer.md`) on the diff before pushing — it
runs those linters and reviews for what they miss (the security model and the
logic-in-tested-Python convention above).

## Promotion: staging → main

Code and config land on `staging`; `main` is the official pre-registration
record and takes code only in reviewed **promotion batches**. Data never waits
on promotion: the deterministic writers (pull, seed, live) and the data-run
collect PRs land on `main` directly.

Why the indirection: two classes of bug are invisible to per-PR CI but caught
by an integration pass over real infrastructure — a workflow that is never
invoked, and a workflow-file change that reaches `main` mid-matrix and changes
what a running fan-out's later jobs execute (the collect-recovery section
below describes the damage). The promotion gates target exactly those two.

The mechanics:

- **Feature PRs target `staging`** (AGENTS.md), and the routing is enforced:
  `main`'s required checks are exactly `gate`, `paths`, `promotion-gate`, and
  **`main-base`**. `main-base` is the merge-routing jail — it runs, and fails,
  only on a PR to `main` whose head is not `staging` or a reviewed non-feature
  lane (the collect run branches, the maintainer's cleanup sweep, the
  metrics-refresh, cert-backtest, and salience-replay PRs, and the qp-topic
  labeling run's `qp-topics/refresh` PR); on those
  legitimate lanes it reports `skipped`, which satisfies the requirement. Its
  definition lives in `main`'s own ci.yml, so the context reports on every
  lane into `main` (docs/security.md inventories this).
  Rulesets cannot constrain a PR's source branch, which is why the routing
  lives as a check at all, and why the check deters mistakes while the human
  merge is what catches sabotage: a PR that edits ci.yml runs the edited
  definition. Dependabot targets `staging` for the same reason. The `staging`
  ruleset itself requires a pull request plus the status checks that can report
  on a staging-targeted PR — `gate` and `paths`; `main`'s other two,
  `promotion-gate` and `main-base`, key on a base of `main` and are always
  `skipped` here — with the **repository admin
  role as its sole bypass actor** — a
  required-checks rule blocks direct pushes of commits that carry no passing
  check runs, so the admin role is the only identity that can land the sync
  merge below — the role an interactive agent session borrows, which is why
  `AGENTS.md` carries the discipline rule against using it. Neither GitHub App *bypasses* `staging`: the scheduled
  `sync-staging` workflow holds a write token to it but opens an ordinary PR
  that must satisfy the same required checks, and `promote` itself performs no
  write at all.
- **Scheduled sync.** `staging` never owns data, so it falls behind `main`
  as the writers and bot lanes commit there. The `sync-staging` workflow
  merges `main` into `staging` daily by opening a PR that auto-merges once
  the staging ruleset's checks pass — gated like any other change, not
  bypassed. Syncing on a schedule rather than at batch time is what keeps the
  cost off the promotion path: the same merge done at promotion moves
  `staging`'s head, and integration freshness is per-SHA, so every scenario
  would have to be re-dispatched for a merge whose content is
  already-gated main history joined with already-gated staging history.
  `promote` still checks the ancestry, and still prints the manual
  merge-and-push commands for the maintainer's admin bypass — the escape
  hatch for a conflicting sync the schedule could not land on its own. The
  sync defers itself while a promotion PR is open, so it never moves the head
  a batch in flight is being tested against. **Ordering:** `schedule` and
  `workflow_dispatch` both read the file from `main`, and the `prod`
  environment is `main`-only, so an edit to `sync-staging` takes effect only
  once it promotes.
- **Two gates, one definition.** `scripts/promotion-gate.sh` checks
  *quiescence* (no `run:predict` / `run:evaluate` / `run:backtest` fan-out in
  flight — no open trigger issue, no unfinished run) and *freshness* (every
  required integration scenario green at exactly the staging head being
  promoted — one green `scenario=all` run, which succeeds only when every
  matrix leg and its collect job does, satisfies all nine required runs at
  once, engine-smoke counted once per engine). The `promote` dispatch runs
  it as pre-flight; ci.yml's `promotion-gate` job runs it as a required
  check on the promotion PR.
  Re-run that check right before merging — quiescence is point-in-time.
- **The engine-smoke skip, and how far it reaches.** `promote`'s
  `skip_engine_smoke` input drops the three engine-smoke runs from that
  dispatch's freshness check and accepts a token-free `scenario=all-offline`
  run as whole-suite evidence instead. It costs the only evidence that real
  engine cells still run in the production posture at the sha being promoted,
  so it is reserved for batches that cannot affect a cell — docs, analytics,
  non-cell code — and the default is the full suite.
  **It narrows the pre-flight only.** ci.yml's `promotion-gate` job sets the
  variable nowhere, so the required check on the promotion PR still demands
  all nine runs at the head sha, and `main`'s ruleset has no bypass for it —
  the data App's deterministic writers are its only bypass actor. A skipped
  batch therefore reaches a green summary and a mergeable PR only once the
  smokes have run too; what the input buys is a cheap answer to *is anything
  else missing* before paying for them.
- **The loop.** Dispatch `promote`; it gates and prints exactly what is still
  needed — the sync commands when staging is behind, the scenario dispatch
  commands when freshness is unmet, or, when green, the `gh pr create` command
  for the promotion PR. The workflow performs no write itself: a PR created with a
  workflow's own token triggers no `pull_request` checks, so the maintainer
  creating it is what makes the required checks real. Merge promotions with a
  **merge commit**, never squash — `staging` and `main` must share history or
  every later sync re-merges rewritten commits.

The full path of a change, operator's view:

1. Branch off `staging`, work, run the relevant gate stages and reviewers,
   open the PR against `staging`; review and merge. The change is now staged
   but **not live** — production jobs execute from `main`.
2. When a batch is worth promoting: dispatch `promote`; if it asks, run the
   sync — dispatch `sync-staging` and let its PR land, or, if that PR
   conflicts, run the printed commands (your admin-bypass push) — then
   re-dispatch.
3. Dispatch the required integration scenarios at staging's post-sync head —
   one `scenario=all` dispatch covers the whole suite, or per-scenario runs
   add up to it (the summary prints both forms) — then re-dispatch `promote`.
   On a cell-inert batch, `promote -f skip_engine_smoke=true` first: it prints
   the `all-offline` form and tells you whether anything *else* is missing
   before you pay for the smokes, which step 4 still needs.
4. Green promote hands you the `gh pr create` for the staging→main PR; its
   `promotion-gate` check re-verifies quiescence + freshness. Re-run that
   check right before merging, and merge with a **merge commit**; tag the
   merge commit `promotion/<YYYY-MM-DD>` (annotated; `-2` for a same-day
   second batch — the *Tags* subsection below). Live on the next workflow
   run.

One-time setup (maintainer): create the branch from main (`git push origin
main:staging`); add the `staging` ruleset — require a pull request plus the
checks that can report on a staging-targeted PR (`gate` and `paths`),
**repository admin role as the only bypass actor** (docs/security.md
inventories it); and add `promotion-gate` — and, once the *Adding a required
status check* procedure below clears it, `main-base` — to `main`'s required
checks alongside `gate` and `paths`. Each reports `skipped`, which satisfies
the requirement, on every PR it does not gate; requiring a context before its
producing job reaches `main` strands every collect auto-merge PR, which is
what the procedure's ordering prevents.

The `staging`
*deployment environment* the freshness runs deploy to (deployment branches
restricted to `staging`, read-only role trust, per-environment engine keys) is
separate wiring, described in docs/security.md.

### Tags

Annotated tags on `main` record the project's public reference points, in
three namespaces:

- **`prereg/<label>`** — a pre-registration freeze commit, e.g.
  `prereg/proc-v1` on the commit that fills `FROZEN_PROCESS_DIGESTS` and sets
  `FROZEN_SINCE` (docs/process-version.md carries the freeze procedure).
- **`promotion/<YYYY-MM-DD>`** — a staging→main promotion merge commit; a
  `-2` suffix distinguishes a same-day second batch.
- **`results/<term>-<milestone>`** — the commit carrying a published metrics
  refresh, e.g. `results/ot2026-longconf`.

One-time setup (maintainer): before the first tag is minted, add a tag
ruleset blocking update and deletion on all three namespaces — a movable
pre-registration marker defeats its purpose. Creating a tag is likewise a
maintainer step, like the promotion merge it usually accompanies.

### Adding a required status check

The ordering is forced, and getting it wrong stops data production rather than
failing loudly: a context nothing on `main` produces leaves every PR into
`main` pending forever, and the auto-merging collect PRs hang first.

```bash
scripts/promotion-gate.sh contexts <candidate>   # the context you want to require
```

It reads `main: require PR`'s live required contexts and `main`'s own workflow
files, fails if anything already required has no producing job, and reports each
candidate as ready or not-yet. It is **not** part of `all`: reading a ruleset
needs repository-administration read, which `GITHUB_TOKEN` cannot hold at all,
so automating it would mean handing a CI job the repo's most powerful scope to
report an advisory fact. Run it with your own token.

1. Land the job on `staging` and let it promote to `main` in an ordinary batch.
2. `scripts/promotion-gate.sh contexts <candidate>` — proceed only on *ready to
   require*.
3. Confirm a real PR of the kind you are gating reports the context. For a
   context that must report on the bot lanes, that means watching one of their
   PRs, since those auto-merge and are what a mistake strands.
4. Add the context to the ruleset. Re-run step 2 afterwards: it now checks the
   context you just added.
5. Update the surfaces that record the required set — the pinned list in
   `tests/test_required_checks.py`, which is the only part of this that runs
   unattended, plus the inventories in docs/security.md and the promotion
   section above. If the pinned list lags the ruleset, a later promotion that
   renames the newly-required job hangs collect PRs with nothing red to show
   for it.

The same ordering applies to `staging`'s ruleset, which gates the unattended
`main`→`staging` sync PR. The stage above reads `main`'s; check `staging` by
hand until there is a reason to parameterize it.

## The predict/evaluate matrix

`plan` parses the issue body's ` ```json ``` ` case block and runs
`fedcourts predict-matrix` / `evaluate-matrix`, which expands the **registry ×
cases × events** into a GitHub Actions matrix. When prediction scope is gated
(`predict.scope=scotus_docket`) the builder reads each case's corpus row (only a
SCOTUS docket is in scope, minus the shared exclusion reasons), so `plan` first
pulls the corpus; with the gate on
and no corpus on disk the build fails loud rather than emit an empty matrix. Each
matrix cell routes to Claude Code, Codex, or Gemini by the entry's `engine`. The
agent writes files only. The workflow's `strategy.max-parallel` throttles the
whole fan-out, however many cases it spans. After scope filtering the builder
also applies a **salience-independent volume cap**
(`predict.max_predict_cells_per_run`, default 240): a hard backstop on the number
of cells queued into one matrix, below GitHub's 256-job ceiling, that holds even
if salience selection fails open. Overflow cases are deferred **whole** (never
splitting a case's engines) in a deterministic case-id order, with the deferred
count surfaced as a `::warning::` and in the plan's step summary; a deferred case
stays in the predict queue and re-runs next cycle, so the cap defers rather than
drops. This is the numeric backstop, distinct from the coarse
`PREDICT_HANDOFF_ENABLED` on/off pause below. One interaction to know: a
forward cell the provisioning gate refuses produces no output, so collect
records a failure fact that counts toward `predict.max_attempts_per_cell`.
For a record-gate refusal that terminal state is right — a decided event must
never re-queue (and the plan-time openness re-check drops it anyway). For a
*staleness* refusal it means a poller stalled for five predict cycles quietly
retires those cells; the recovery is to fix the poller and re-queue with a
fresh `run:predict` issue, or clear the committed attempt facts in a reviewed
PR where the cap itself was the problem. Distinguishing refusal kinds in the
failure fact so a staleness refusal never burns the cap is open follow-up
work.

On `run:predict`, `plan` also refuses to re-mint a cell that already ran. A cell
spends its tokens before `collect`, the run's single durability step, so a
failed collect leaves every prediction in a cell artifact and nothing in the
ledger the already-predicted gate reads — and the next live cycle re-derives the
same events and re-spends the whole run. Before building the matrix, `plan`
lists the cell artifacts of this workflow's completed runs from the last 48
hours whose `collect` did not conclude success, and **withholds** any cell
already sitting in one, naming the stranded run and `gh run rerun <id> --failed`
per cell: the remedy is to recover that run, not to re-run this one (the
collect-recovery section below carries the order). The match is per predictor ×
case × event and keys on the artifact's *existence*, not on whether that cell
produced anything — a cell that spent its tokens and delivered nothing is
withheld too, because collecting the run is how anyone learns which of the two
it was, and the event re-queues normally once the ledger is honest. A cell with
no artifact — never queued, or dead before upload — still runs. The census step
fetches and filters only: every decision is in `fedcourts predict-matrix`
(`--stranded-file`), and it degrades open at two grains rather than blocking a
legitimate run, since the failure this guard prevents is expensive rather than
dangerous — a run it cannot read after three attempts drops out of the census
with a `::warning::`, and a failure leaving nothing usable empties it
altogether. The guard also releases itself: a run leaves the census once its
`collect` concludes success on the latest attempt, and ages out of the window
regardless. A maintainer who wants a fresh run *sooner* makes that an explicit
act rather than a new trigger — delete the stranded run's cell artifacts (`gh
api -X DELETE repos/<owner>/<repo>/actions/artifacts/<artifact_id>`), then
re-queue.

If the matrix comes back **empty** — every queued case was out of scope (or already
predicted) — the `predict`/`evaluate` and `collect` jobs are skipped, so nothing
would otherwise close the trigger issue; the `plan` job closes it with a note
instead of leaving it orphaned open. (Pull avoids filing such all-out-of-scope runs
in the first place; this is the backstop for a manually-filed or partial one.) Note
the volume cap above can also empty the matrix (when it defers *every* case);
so can the ex-post spend backstop (`spend.ceiling_usd` in `config/tracking.yaml`
— armed, see [budget.md](budget.md)) when the trailing window's measured spend
reaches the ceiling; and so can the plan-time openness re-check, when every
event the trigger listed has resolved since the issue was queued. The close
step cannot tell any of those from scope-empty, so it closes with the
out-of-scope note in all four cases. On `run:predict` the stranded-run guard is
the one exception: when it withholds *every* cell, `predict-matrix` writes the
close note itself (`--stranded-note-file`) and the step posts that instead, so a
fully-superseded run says recover the uncollected run rather than reporting
nothing was in scope. Each surfaces its own escalated `::error::` for correct
attribution, and the close is safe in each case for its own reason: a cap- or
spend-deferred case stays in its queue and re-queues next cycle, a resolved
event needs an evaluate run rather than a re-queue, and a withheld event
re-queues on a later cycle for as long as no prediction is committed for it. A
spend-breach deferral clears on its own when the window rolls past the burst
that tripped it (or when the maintainer raises `spend.ceiling_usd`). A breach
driven by a sustained *rate* rather than a burst — a capacity knob left
non-binding, which at the current planning rate runs above the ceiling
([budget.md](budget.md)) — does not clear that way: it re-trips each cycle, and
the fix is the capacity knob or the ceiling, not waiting.

### The evaluate cell grades blind

An evaluate cell brackets its agent with two deterministic harness steps
(`fedcourtsai.blinding`, and *Semantic claims* in
[outcome-decomposition.md](outcome-decomposition.md)): `fedcourts
provision-blinded-predictions` stages each predictor's latest prediction under an
opaque alias with its identity masked, and `fedcourts unblind-evaluations`
renames the evaluator's alias-keyed output back onto the real predictor ids. The
staging area lives under the case's gitignored `record/`, so it rides the cell
artifact and never reaches the ledger.

**The un-aliasing runs before the stamp, and the ordering is load-bearing.**
`stamp-cell --role evaluator` joins each evaluation to the prediction it scored
on the `predictor_id` field; under an alias the join misses and the cell's
`claim_scores` block is *silently* absent rather than wrong (so is
`base_rate_salience_version`, unless the evaluation records a `risk_set` basis,
which fails the stamp instead, and so is an interim cell's harness-stamped
`segment_base_rate`, which reads the application Term off that same
prediction). `validate`'s
evaluation-target check resolves the same join and does fail loudly, so it is the
backstop rather than the detector. The cell's order is therefore: blind →
agent → capture usage → capture retrieval log → **un-alias** → stamp → validate.
Wiring those two steps anywhere else in the sequence produces a run that looks
green and quietly drops a scoring block.

How a cell's output becomes a PR is the same across **`run:predict`** and
**`run:evaluate`**: each cell validates its own output and
uploads it (plus a status file) as an artifact rather than opening a PR, and a
final **`collect`** job unions the run's artifacts into **one PR** — auto-merged
once `gate` + `paths` are green, and closing the triggering issue on merge — with
any salvageable partial output split into a single companion **draft** PR. So a
fan-out of dozens of cells yields one (or two) PRs for the run, not one per cell.
The append-only `data/` path jail (`fedcourts assert-paths`) is enforced in
`collect` before the commit and again as the required `paths` check, so an
auto-merged PR can only add artifacts under `data/`; a schema re-validation and a
secret scan (`fedcourts scan-diff-for-secrets`) run beside it producer-side —
a validation failure downgrades the PR to a draft, while a secret-scan hit
**withholds the branch entirely** (nothing pushed; a redacted report lands on
the trigger issue) since the push itself would publish the secret (see
[security.md](security.md)).

For `run:predict` and `run:evaluate`, `collect` also rolls up any
agent feedback (`flags.json`) the run surfaced and posts it three ways — each
gated on the run's secret scan, since flag messages are agent free text — the run PR
body, the Actions summary, and one long-lived **agent-feedback** tracking issue (the
single latched-issue pattern of `ops-dashboard` / `data-validation` / `pipeline-health`) — so a note
reaches a durable, centralized home even when a fully-failed run opens no PR.
The `run-seed` historical walker has its own instance of that pattern: a `guard`
job raises one long-lived **pipeline-health** issue if the checkpointed walk is
ever cancelled or fails (e.g. a chunk overran the job's hard timeout), and clears
it when a later walk finishes clean — so a silent, PR-less writer failure still
reaches a durable home.
Separately, every cell may also write a `tooling.json` self-report on its
environment/tooling, committed with the cell's output rather than rolled into the
per-run PR/issue; the `run-ops` dashboard scans these into a tooling-feedback
digest. See the `flags.json` and `tooling.json` channels in
[data-pipeline.md](data-pipeline.md).

To trigger prediction/evaluation for **one** case, open an issue whose body
contains a single object and apply `run:predict` (or `run:evaluate`):

    ```json
    {"court": "ca9", "docket": 64512345, "events": ["evt-motion-stay"]}
    ```

To trigger **many** cases from one issue (e.g. a whole SCOTUS long-conference
list of petitions), use a JSON array of the same objects:

    ```json
    [
      {"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]},
      {"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}
    ]
    ```

`events` is optional per case: omit it (or pass `[]`) to target the case's
default events — its **open** events for `run:predict`, its **resolved** events
for `run:evaluate`, so already-resolved events are skipped. Every listed case is
multiplied by the registry and its events to produce one matrix cell per
predictor/evaluator × case × event — which `run:predict` and `run:evaluate`
collect into one PR for the run.

`predictors` is also optional per case and narrows the `run:predict` fan-out to
the named registry ids:

    ```json
    {"court": "scotus", "docket": 24001, "predictors": ["codex-baseline"]}
    ```

This is the **engine backfill** path: when one engine's cells failed (a quota
or provider outage) while the others delivered, re-firing the full registry
would re-run — and duplicate the committed predictions of — the healthy
engines: only resolved events are excluded (via default open-event
resolution), so an open event re-mints cells for every enabled predictor
regardless of which engines already committed a prediction. Naming an id that is
not an enabled predictor fails the plan job rather than silently skipping the
engine. `run:evaluate` ignores the field: an evaluator always scores every
committed prediction for its event.

## Unrecorded outcomes: what pull's outcome detection leaves behind

`run-pull` records `outcome.json` itself only when a decided docket is
unambiguous (a machine-readable disposition, a decision date, and a single open
event). Everything else — an unreadable/absent disposition, no decision date, or
a case-level disposition that cannot be attributed across several open events —
becomes an **unrecorded outcome** (it does not guess): the case lands on the
runner-local unrecorded queue (`unrecorded-queue.json`, the `UnrecordedOutcome`
detection in the library) instead of the git ledger. No issue is filed for
these. Both the pull and live jobs surface each one per-case on the pipeline-runs
dashboard's triage list ("court/docket — reason"), with the count on
the Actions step summary, for maintainer triage — recording nothing beats a
guess.

## Recovering a run whose `collect` failed

`collect` is the single writer for a run's agent output, so an all-or-nothing
failure would discard the whole run — one transient artifact download can carry
dozens of successful cells with it. It therefore degrades per artifact, and
what it could not collect is named rather than silently dropped. Two gaps, two
remedies:

| the PR body / run log says | what happened | fix |
|---|---|---|
| *artifact did not transfer* | the cell likely succeeded; its output still exists | **re-run the `collect` job** |
| *no cell output at all* | the cell died before it could report | **re-queue** — no rerun helps |

Either gap keeps the trigger issue open, so a run never auto-merges presenting
itself as complete while omitting cells.

A **wholesale-failed run** — every cell died, so no ready or partial PR opens —
still records one `attempt.json` fact per failed cell via a small auto-merging
**facts-only PR** (`<role>/run-<run_id>-facts`, no `Closes #`, so the trigger
stays open for the re-queue). That is what lets the per-cell attempt cap advance
for a persistently-failing cell even when the run itself produced nothing.

**Re-running collect is safe and repeatable.** `gh run rerun --failed`
re-executes only the failed job; the artifact listing is per-run, so it re-lists
and re-fetches the original attempt's uploads. The loop force-pushes its
run-scoped branch, finds-or-updates the PR (reconciling draft state), and
marker-dedupes the trigger-issue reports, so nothing stacks or aborts on a
second pass. A kind whose PR already merged is skipped.

Three caveats:

- **Cell artifacts are retained 7 days.** After that a transfer-lost cell is
  gone and only a re-queue recovers it.
- **`--failed` also re-runs failed *cells*,** and `upload-artifact` rejects a
  duplicate artifact name within a run, so those re-run cells fail at upload.
  `--failed` is the recovery for a *collect-only* failure; when cells failed
  too, land `collect` first and let the re-queue pick the rest up.
- **On `run:predict`, collect first — a re-queue will not stand in for it.**
  The stranded-run guard above withholds every cell that uploaded an artifact to
  an uncollected run, so re-applying `run:predict` inside its 48-hour window
  queues nothing and closes the new trigger issue saying so. Rerun `collect`,
  which commits what the cells produced; the guard then releases that run, and
  any event still holding no prediction — including a cell that ran and
  delivered nothing — re-queues on a later cycle. That costs one round trip
  where re-queueing first would cost a whole fan-out's tokens to reach the same
  ledger.

A rerun discards hand-edits to an unmerged draft branch — it is rebuilt from the
artifacts. Finish a draft by merging it, not by editing and then re-running.

## Graceful degradation on limits

Agent steps (predict, evaluate) are bounded by a step-level
`timeout-minutes` set below the job's, so a run that overruns trips the *step* —
not the job. A step timeout (or a max-turns stop) fails only that step and leaves
the runner alive, so the salvage step still runs (`if: !cancelled()`) and the
agent's partial work survives instead of being discarded with the cancelled job.

What salvage looks like is uniform across **`run:predict`** and
**`run:evaluate`**: each cell records its status and uploads its output
(`if: !cancelled()`); the `collect` job then routes a cell that did not finish
cleanly — or whose output failed schema validation — into the run's **draft** PR
(never the auto-merging ready one), and a cell that produced nothing is warned
about rather than committed. A run that finished cleanly is
unaffected: the draft path only triggers when the agent stopped early.

## Pausing the tournament without pausing ingestion

`seed`/`pull`/`live` (cheap, API-budgeted) and `predict`/`evaluate` (the model
spend) can be run independently. Two variables hold each fan-out at its handoff
seam:

| Variable | Unset | Effect when `0` or `false` |
|---|---|---|
| `PREDICT_HANDOFF_ENABLED` | `1` — files | `run:predict` issues are not filed |
| `EVALUATE_HANDOFF_ENABLED` | `1` — files | `run:evaluate` issues are not filed |

Set either in the `prod` environment (a repository-level variable of the same
name works identically, unless an environment-level one shadows it). Both
default to filing, so an unset or mistyped variable keeps the tournament
running: the failure that costs coverage is the quiet one. Ingestion is
untouched — the corpus keeps refreshing and outcomes keep being recorded, so a
pause costs prediction/grading coverage for that window, never data. A full
tournament pause needs both variables set to `0` — holding only one leaves the
other channel's trigger issues arriving on their own.

**Holding predict is lossless, and resuming needs no backfill.** The predict
queue lives in the corpus, not in the issue — the issue is only a trigger
carrying a snapshot of it. A **selected** case stays queueable for as long as any
enabled predictor still *owes* an open event, and the live channel's selection
sweep re-polls exactly that set each cycle (`pipeline/live.py`, gated per
`(predictor, event)` on `event_has_predictions(predictor_id=...)` from
`matrix.py`), debounced to daily by `predict_queued_at`. Owed is per cell, so a
case where two of three engines committed a prediction and one quota-failed is
still swept for the missing engine — the same grain the `predict-matrix` plan
gate uses to re-mint only the not-yet-predicted engines. So a held window never
needs its issue re-filed or re-opened.

The drain is paced, not instant: the sweep is capped at
`salience.sweep_cases_per_cycle` (25 in `config/tracking.yaml`) and works stalest
first, so a backlog larger than the cap spreads over the following cycles — the
same behaviour [salience.md](salience.md) describes. A case that is unselected or
latched out of scope is never re-queued at all. The per-cell owed check also
honors `predict.max_attempts_per_cell` via the ledger-derived failure facts
(described below for evaluate), so one `(predictor, event)` cell that fails every
attempt cannot re-queue forever while a sibling engine still owed the same event
is swept normally.

Held windows are marked **held** on the pipeline-runs dashboard row, the run
log, and the step summary rather than reported as dispatched, so a growing
backlog is legible as a paused channel and not misread as a stalled fan-out.

### The evaluate queue is level-triggered too

The poll seams queue `run:evaluate` off *this cycle's* resolutions — events that
`result.resolved` reports as newly closed — and `upsert_events` is
resolved-latching, so no later poll re-emits them. On its own that would make a
failed or dropped evaluate run lossy: the corpus push and the outcome commit both
land before the handoff, so the outcomes and predictions would exist with nothing
left to grade them.

The **evaluate backlog deriver** (`pipeline.pull.evaluate_backlog`) closes that.
Each `pull-all` / `live-poll` cycle re-derives owed gradings straight from
committed ledger state — a resolved event that has a prediction and is missing at
least one enabled evaluator's evaluation — and appends them to the same evaluate
queue the fresh-resolution path feeds. So a run that is dropped, fails, or is
never dispatched is picked up on a later cycle; the trigger issue is a trigger,
not load-bearing state.

It mirrors the predict selection sweep, with one deliberate difference and one
deliberate similarity:

- **Different:** it is purely local (git ledger + corpus, no network), so its
  `evaluate.backlog_cases_per_cycle` cap bounds model spend and PR volume, not
  request rate.
- **Same:** an `evaluate_queued_at` corpus column debounces re-derivation to
  daily and drains the backlog stalest-first, so an in-flight or failed run PR is
  not re-queued every cycle. That column is scheduling metadata only — the queue
  itself is re-derivable from git — so losing it costs at most a duplicate trigger
  issue, never a grading.

The daily debounce paces re-queuing but has no ceiling, so a cell that fails
*every* attempt (a persistent quota wall, a malformed record) would re-queue
forever. The **ledger-derived failure facts** are the backstop: the corpus-blind
`collect` job writes one committed `attempt.json` per failed cell into the git
ledger, and the deriver counts them (`matrix.cell_failure_count`). Once a cell
reaches the `evaluate.max_attempts_per_cell` cap the deriver stops re-deriving it.
The count keys on **cell identity** (actor + event at a seam), not process
version, so a cell retried under a newer version still counts against the same
cap; and it is keyed per (evaluator, event), so one exhausted cell never
suppresses a sibling evaluator still owed the same event. The facts live in the
git ledger, not the corpus, so ingestion never touches them; a wholesale run
failure that opens no PR commits no facts (that tail is left to the loud stall
comment) — losing a would-be fact costs at most a duplicate trigger, never a
grading.

Re-queueing costs nothing but latency: the scoring surfaces count one grading per
(case, event, predictor, evaluator) — newest by harness clock — so a re-grade
supersedes rather than double-counts, and the `evaluate-matrix` plan gate drops a
cell whose judge has already graded the event (per evaluator) so a re-derivation
spends model tokens only on the *missing* judges. The gate works at (evaluator,
event) grain, which carries one accepted limitation: a prediction committed
*after* a judge graded the event is not re-scored by that judge. What the coarse
grain buys is the spend, and what it costs is a coverage gap that falls
differentially — an engine whose cells backfill late accumulates fewer scored
events than one that ran on time. The leaderboard publishes that gap rather than
leaving it to a ledger scan: every entry carries its own `events_scored` against
the board's union, and `fedcourts leaderboard` warns when they are unequal
(`metrics/README.md`).

An `EVALUATE_HANDOFF_ENABLED` pause switch mirrors `PREDICT_HANDOFF_ENABLED`:
holding it costs latency alone — a held window re-derives on resume rather than
being lost — so a full pause of both channels needs both variables set to `0`.

### Disabling the workflow is not the same as holding the handoff

Disabling `run-predict` / `run-evaluate` in the GitHub UI stops the *runs* but
not the *issues*. The issues keep arriving and sit unconsumed — and `run-ops`
lists every still-open `run:*` issue as a **stalled fan-out**, so a
workflow-disabled-only pause steadily reddens the ops dashboard with what looks
like broken runs. Holding the handoff avoids that; for a full pause of either
channel, hold the handoff *and* disable the workflow.

## Snapshot sequencing

`run-pull` pushes factual snapshots **to the corpus** — the per-case content
store plus the `corpus-push` of the index — before it queues `run:predict`, so
`run-predict` — a read-only corpus consumer (its plan job reads the index in
place over the ranged backend; its cells provision from the content store and
query the index through the credential-holding corpus sidecar) — sees the
snapshot it must predict from. Raw facts never go through PRs (they are
CourtListener data, not agent output); agent outputs (predictions, evaluations)
always do.
