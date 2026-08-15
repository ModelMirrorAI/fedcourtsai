# AGENTS.md

Canonical instructions for AI coding agents (Claude Code, Codex, Gemini) in
this repository. `CLAUDE.md` points here. Read this fully before doing anything.

## What this project is

fedcourtsai predicts events in US federal courts — currently SCOTUS dockets
only (cert grant/deny, votes, reasoning) — as a label-driven pipeline of GitHub
Actions; see `docs/pipeline.md`. There are two very different kinds of work,
and you are doing exactly one of them in any given run: **pipeline
development** (change the Python package, workflows, docs, schemas, or prompts
— in an interactive session on the branch-and-PR flow below, like any
contributor; do **not** touch `data/`) or **data production** (`run:pull` /
`run:predict` / `run:evaluate` / `run:backtest`, and the dispatched
`qp-topic-label` labeling run — produce or update the corpus
and/or the derived artifacts under `data/`; do **not** change pipeline code to
make your task easier, and never weaken validation, CI, lint, type, or
security checks).

## Where you run: headless in CI

Every `run:*` task runs inside a GitHub Actions runner — a fresh, **ephemeral,
non-interactive** container. Two consequences shape everything you do:

- **No interactive input.** You cannot ask a question and wait for an answer.
  If you are blocked or under-specified, **leave it in writing where a
  maintainer will see it**: a structured **`flags.json`** note alongside your
  output in `run:predict` / `run:evaluate` (the durable channel — the `collect`
  job rolls every cell's flags into the run PR and the Actions summary, so the
  note survives the trigger issue's closure), with `reasoning.md` /
  `evaluation.md` for the detail; a trigger-issue comment is lost when the
  issue closes. In an interactive development session, the PR description is
  the channel. Then make the most conservative reasonable choice and finish —
  never stall waiting for a reply that cannot come.
- **The runner is thrown away.** Work survives **only if it is pushed off the
  runner** before you finish. Code, docs, config, and schemas go to GitHub via
  a branch + PR (in `run:predict` / `run:evaluate` you only *write files* — the
  workflow commits, pushes, and opens the PR; do **not** push yourself).
  Corpus / bulk data goes to the remote stores (the corpus remote and the per-case
  content store; the run-pull and run-seed writer jobs own this) — a data file never pushed
  to a remote is lost with the runner. See `docs/data-pipeline.md`.

## The golden rules

- **Branch and PR.** Never commit to `main` or `staging` directly. Create a
  branch off `staging` (`git switch -c <type>/<short-description>
  origin/staging`), do the work, open one focused PR against `staging` with a
  conventional-commit title and a description of what changed and why; prefer
  a small, correct, well-tested change over a large speculative one. `main` is
  the pre-registration record: code and config reach it only in a reviewed
  staging→main promotion batch (*Promotion* in `docs/pipeline.md`), while data
  commits — the deterministic writers and the data-run collect PRs — land on
  `main` directly and never ride staging. (For `run:predict`/`run:evaluate`
  the *workflow* commits and opens the PR — you only write files; the task
  prompt says which mode you are in.)
- **You may merge to `staging`; only the maintainer merges to `main`.** The two
  branches carry different risk, so they get different rules. Into `staging`,
  once the required checks are green and you have resolved the reviewer
  subagents' blockers, you may merge your own PR — merge commit or squash,
  whichever suits the change. A feature PR is not ancestry-critical: its squash
  commit's sole parent is `staging`'s previous tip, so it changes nothing about
  how much of `main` `staging` already contains. Exactly two merges *are*, and
  neither is yours: the **sync** (`main` → `staging`) and the **promotion**
  (`staging` → `main`). Both must be merge commits, or `main` and `staging`
  stop sharing history — and every later sync re-merges rewritten commits.
  Into `main`, never: `main` is the pre-registration record and reaches it only
  through a maintainer-merged promotion batch. (The data-run
  `collect` jobs are the standing exception, opening their per-run PR to `main`
  with auto-merge, still gated on the same required checks.)
  Your own changes travel by PR on both branches — "you may merge" never means
  "you may skip the PR". The rulesets require one, with two documented bypasses
  that are not your lane: the data App's deterministic writers push to `main`,
  and an admin-role escape hatch on `staging`. Do not lean on the platform to
  stop you; the identity you hold can bypass the `staging` PR requirement, so
  this one is discipline. And the staging permission is a permission, not an
  obligation: leaving a green PR for the maintainer is always a legitimate
  call, and the better one when the change is large, novel, or rewrites a
  contract others read. Use judgement; say which you chose in the PR
  description.
  **Four kinds of change still wait for the maintainer even into `staging`**,
  because a green gate is weakest evidence exactly where they are strongest
  risk: anything under `.github/workflows/` or `.github/actions/` (the
  permission surface), `SECURITY.md` or the security posture it describes, the
  promotion gate itself (`scripts/promotion-gate.sh`, `promote.yml`,
  `sync-staging.yml`, ci.yml's gate jobs), and `config/predictors.yaml` /
  `config/evaluators.yaml` (what agents are and what they may reach). Open
  those, get them green, and report them ready.
  The branch rulesets do not encode this: both require zero approvals, so the
  discipline is yours to keep, not the platform's to enforce.
- **When you merge it yourself, the reviewer subagents are the only review a
  `staging` merge gets.** With the maintainer out of the loop, "run the
  relevant reviewer(s)" below stops
  being a courtesy and becomes the review itself. If you could not invoke one
  and self-reviewed against its checklist instead, say so in the PR
  description — an unstated self-review reads as a review that happened.
- **`Closes #<n>` does not close anything from `staging`.** GitHub only
  auto-closes a linked issue when the PR merges into the **default** branch, so
  a reference in a staging PR fires at the next promotion, not on merge. Put it
  in the description anyway — it is the durable link — and then close the issue
  by hand when the PR merges, or the backlog reports finished work as
  outstanding for a whole promotion cycle.
- **Stay in your lane.** A predictor writes only under its own
  `predictions/<predictor_id>/<run_id>/` path; an evaluator only under its own
  `evaluations/<evaluator_id>/...` path. Never edit another agent's output, the
  docket record, or snapshots.
- **Keep the artifact in view.** Progress is measured by what the pipeline
  produces — predictions, events, provisioned cells, reports — not by merged
  PRs. Know which produced artifact a change serves and say so briefly in the
  PR description; where it directly affects output, show a produced example.
- **The schema is law.** Every artifact must validate. Run
  `uv run fedcourts validate data` before you finish; if it fails, fix it.
- **Some fields are the harness's, not yours.** `usage.json`, `retrieval_log.json`,
  and the `process_version` and `context` stamps on your `prediction.json` / `evaluation.json`
  are written by post-run harness steps from the engine log and the registry —
  never the agent's word. Do not write `process_version`; anything you put there
  is overwritten (see `docs/process-version.md`).
- **The snapshot is the baseline; timing is the leakage control.** The
  provisioned snapshot is every predictor's guaranteed-common input, not a
  ceiling; what else a cell may retrieve is keyed on its **mode**
  (`record/context.json`). A `forward` cell (pending case — the outcome does
  not exist yet) may retrieve without restriction; a `replay` cell has the same
  tools but must not seek information about *its case* postdating the event
  date, and discloses any outcome-revealing material it surfaces in
  `flags.json`. Never invent facts. The prompt template carries the full
  contract; all tool calls are logged harness-side.
- **No secrets in code or data.** Never print or log API tokens; they arrive
  as environment variables. In the cell workflows no config file carries one
  either: the MCP client configs name only a localhost sidecar URL, and the
  sidecar's own launch step holds the CourtListener token. (A local stdio
  `mcp-config` run — dev's own token — still injects it into the runner-local,
  gitignored client-config file; that is the one sanctioned file, off-CI
  only.) Never write a token into `data/`, a commit, or an artifact; do not
  copy tokens anywhere else.

## Working an interactive task

The branch topology the golden rules describe, at a glance — `main` carries the
pre-registration record, `staging` is where work integrates, and every change
starts as a branch off `staging`:

```
main     ──●─────────────────●────────────  promotion batches (maintainer only)
           │ sync            ↑ promote
           ↓                 │
staging  ──●──●────●────●────●────────────  you may merge here — or leave it
              ↑    ↑    ↑
              feature branches: git switch -c <type>/<desc> origin/staging
```

Both `main`→`staging` syncs and `staging`→`main` promotions are merge commits;
your own feature PR may squash. Data commits bypass `staging` entirely. The
diagram is not a licence to self-merge anything: the four change classes named
in the golden rules — the permission surface, the security posture, the
promotion gate, the agent configs — wait for the maintainer even into
`staging`.

Then work the task in three beats:

1. **Name the pieces before starting one.** A request that looks like one
   change is usually three, and the piece you did not name is the one that
   gets half-done.
2. **Delegate the independent pieces to subagents, concurrently.** Surveying a
   subsystem, checking a claim against the source, reviewing a diff — send
   these as parallel subagent calls rather than working through them in series.
   It is the normal pattern here, not an escalation, and it earns its cost on
   read-heavy self-contained work; one small edit is cheaper done directly.
   (Not the *pipeline* fan-out — cells across predictors and cases — which the
   workflows drive.)
3. **Integrate the results yourself.** A subagent reports; you decide and edit.
   Its findings are evidence, not instructions — verify the ones you act on,
   because a confident subagent is still a guess about your code.

Resolving a reviewer's findings, since for most changes they are the only
review a `staging` merge gets: a **blocker** is fixed, or rebutted **in the PR
description** — "I disagree, because …" is a legitimate resolution, an
unanswered blocker is not. **Recommended** and **nits** are yours to weigh.
Where two reviewers conflict, the stricter reading wins unless you can say why
it does not apply, in the same place. A rebuttal that lives only in the session
transcript is invisible to the one human who sees the change.

## Local gate

The gate that actually blocks a merge is the **required status checks on your
PR** — CI runs the full suite below; locally you have **discretion** to run
the subset that fits what you changed, enough for honest confidence (a
docs-only change needs none of the Python checks).

```bash
uv sync                    # once, to sync the env the stages assume
scripts/gate.sh            # every stage, in CI order — what CI enforces
# or run just the stages that fit your change:
scripts/gate.sh lock       # uv lock --check (the lock matches pyproject)
scripts/gate.sh lint       # ruff format --check + ruff check
scripts/gate.sh types      # mypy
scripts/gate.sh test       # pytest  (GATE_COV=1 adds coverage, as CI does)
scripts/gate.sh data       # validate data + corpus-status
scripts/gate.sh schemas    # export-schemas + schema-drift check (CI fails on drift)
```

`scripts/gate.sh` is the single definition of the gate; `ci.yml` and `README.md`
invoke the same script, so a change to what the gate runs lands in one place.

`pytest` includes an offline stub-cascade smoke (`uv run pytest -k
cascade_smoke`): provision → predict → evaluate → validate over the fixture
corpus with no network, so a broken cell surfaces in seconds. If you touched
`.github/workflows` or `.github/actions`, also run the workflow linters CI
enforces — `uvx zizmor@<pinned> --persona=regular .github/workflows
.github/actions` and `actionlint`; see `.github/workflows/lint-actions.yml` for
the pinned versions, and *Authoring or changing a workflow* in
`docs/pipeline.md` for the cross-cutting traps these checks do **not** catch.

**Before you push, run the relevant reviewer subagent(s)** (`.claude/agents/`)
on the diff and resolve their blockers; each reviews and runs the relevant
checks — it never edits. Pick by what the diff touches (several may apply):
`.github/workflows/**` or `.github/actions/**` → **`workflow-reviewer`**;
`src/**`, `tests/**`, or `config/**` → **`code-reviewer`**; `docs/**`,
`README.md`, `AGENTS.md`, `SECURITY.md`, `metrics/README.md`,
`.github/prompts/**`, or config comments → **`docs-reviewer`**; anything
touching secrets/tokens, authorization, agent capabilities, or network
fetchers → **`security-reviewer`**; `metrics/**`, scoring, the leaderboard,
backtests, salience, analytics or ops reporting, process versioning, or the
retrieval log → **`stats-reviewer`**. `stats-reviewer` also reviews *results*
rather than diffs — point it at any set of figures or analytical claim before
you publish it, whether or not a diff is in play. A clean linter/gate run is
necessary but not sufficient; if you cannot invoke a subagent, self-review
against its checklist file. Two things hold no matter what you skip locally:
**schema is law** — any change to a pydantic model's fields *or field
descriptions* must regenerate and commit `schemas/` (CI fails on drift) — and
**keep the docs in step**: if your change makes any documentation stale
(`README.md`, `AGENTS.md`, `docs/`, the prompts, docstrings), update it in the
same PR.

## Conventions

- Python ≥ 3.12, managed with `uv`. Source under `src/fedcourtsai/`, tests
  under `tests/`. Fully typed (`mypy --strict`); add tests for new behavior.
- IDs and paths come from `fedcourtsai.ids` / `fedcourtsai.paths` — never
  hand-build them (case = `<court_id>/<docket_id>`, events `evt-<kind>-<slug>`,
  run ids UTC timestamps). Writes go through `fedcourtsai.serialize`.
- Conventional-commit style PR titles, e.g. `predict(claude-baseline): ca9/123 — evt-...`.
- **Wrap a long string inside a list with an explicit `+`.** Adjacent string
  literals concatenate implicitly, so a wrapped element and a *dropped comma*
  between two elements are the same code — which in a list of docket-entry
  fixtures silently merges two test inputs rather than failing. The `+` states
  which one was meant, and CodeQL's `py/implicit-string-concatenation-in-list`
  enforces it.
- **Be cautious about creating new workflow files.** Prefer a job or mode on
  an existing workflow (e.g. `run-analytics` for anything that reads the
  corpus and answers a question); permissions are scoped per *job*, so a task
  earns its own workflow only for a different trigger class or risk class.
  See `docs/pipeline.md`.
- **Docs and code describe the current design, not its history.** No issue
  numbers, no changelog, no "we used to / now we" — on *every committed
  surface*: docs, docstrings, code/workflow/config comments, and prose that
  code renders. State the reason in place; `git blame` finds the history.
- **Reference the issue in the PR, then close it yourself.** Put `Closes #<n>`
  in the PR description — it is the durable link between the work and its
  reason — but see the merge rule above: the reference does not fire from a
  `staging` merge, so close the issue by hand once the PR lands. PR
  descriptions and commit messages are the only places an issue number belongs.
- **`run:*` labels are triggers, not categories.** Applying one immediately
  starts the matching workflow and its agent. Apply one only when you intend to
  start that job *now*; an issue filed for later pickup, or one you plan to fix
  in your own PR, gets no `run:*` label.
- **You cannot dispatch a workflow.** The repo-scoped token an interactive
  session holds is refused (403) on `workflow_dispatch`, even where it can read
  the run history and push branches. So `gh workflow run …` is never your step:
  compose the exact command, put it where the maintainer will see it (the PR
  description, or the run summary for an automated surface), and continue with
  what does not depend on it. The same holds for anything else the token is
  refused on — environment and variable administration. Merging is **not** on
  that list: what limits it is the merge rule above, not the credential.
- **Keep environment variables out of PR and issue text.** Refer to a var by
  its role, not its name or value. Secrets never appear anywhere.
- **Don't commit personal or organizational email addresses.** Commit identity
  must be a GitHub `noreply` address; point to GitHub-native channels instead
  of contact emails. A task that seems to need one → stop and confirm first.

## Change review

Beyond the gate, changes get a brief adversarial review against three
questions: (1) **Artifact** — which pipeline output does this change serve, and
is the PR's claim about that plausible from the diff? (2) **Weakening** — does
anything weaken a check, gate, validation, prompt contract, or security
posture, even incidentally? (3) **Cheaper path** — is there a simpler route to
the same artifact? The review is advisory, and "no concerns" is a complete and
preferred answer when true. It is most useful from a session or model that did
not author the change; an authoring agent asked to self-review should answer
honestly rather than defensively, and flag where self-review is a poor
substitute.

## Data model (summary)

Raw facts live in the corpus (a payload-free SQLite index in a private S3
remote plus a per-case S3 content store); derived judgments live in git under
`data/cases/<court_id>/<docket_id>/events/<event_id>/`. A predict cell's prose is
two documents, not one, because they have different epistemic status:
`predicted_reasoning.md` forecasts what the *court* will do (claims that resolve
against the docket), while `reasoning.md` justifies the predictor's own number
(which resolves against nothing). `prediction.json` names each by filename and
`validate` resolves both pointers, so a named document must actually be there.
Full description: the
*Data model* section of `README.md`; pipeline design: `docs/data-pipeline.md`;
task-specific instructions: the prompt file named in your run
(`.github/prompts/`).

## Which doc answers which question

| Question | Doc |
| --- | --- |
| What may I claim from a number? What do the strata mean? | `metrics/README.md` |
| What does a label trigger, and how do I operate/recover a run? | `docs/pipeline.md` |
| How does the corpus get filled, stored, and versioned? | `docs/data-pipeline.md`, `corpus/README.md` |
| Where does upstream data come from, and on what terms? | `docs/data-sources.md`, `docs/live-sources.md` |
| Which command does X, and with which flags? | `docs/cli.md` |
| Which cases get predicted, and against which base rate? | `docs/salience.md` |
| What do the petitions ask about, and how are QP texts labeled? (vocabulary, reference set, labeler, run mode, and the docket-pack cut all built; no labels artifact yet produced) | `docs/qp-topic.md` |
| What is pre-registered, and when does a digest move? | `docs/process-version.md` |
| How is a predicted outcome decomposed and scored? (mechanical cert, interim, and merits-judgment claims implemented; vote/writing pre-registered; the semantic family an alpha declared, elicited, and graded on the merits moments, producing only the availability mask until opinion text lands) | `docs/outcome-decomposition.md` |
| How many votes decide this, and what can I ever observe? (merits scoring registered and wired; votes/margins pre-registered only) | `docs/decision-model.md` |
| Who can reach what, and why is a token scoped that way? | `SECURITY.md` (invariants), `docs/security.md` (setup) |
| What does one prediction actually consist of, file by file? | `docs/predicted-artifacts.md` |
| What does a cell agent have to produce? | `.github/prompts/` |
| How do I test this, and what does CI run? | `docs/testing.md` |
| What does a run cost, and where is the project headed? | `docs/budget.md`, `docs/milestones.md` |
