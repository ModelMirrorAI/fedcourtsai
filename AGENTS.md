# AGENTS.md

Canonical instructions for AI coding agents (Claude Code, Codex, Gemini) working
in this repository. `CLAUDE.md` points here. Read this fully before doing anything.

## What this project is

fedcourtsai predicts events in US federal courts (e.g. whether a motion will be
granted/denied, how each judge votes, and the court's likely reasoning). It runs
as a label-driven pipeline of GitHub Actions; see `docs/pipeline.md`.

There are two very different kinds of work, and you are doing exactly one of them
in any given run:

1. **Pipeline development** (`run:dev`): change the Python package, workflows,
   docs, schemas, or prompts. Do **not** touch `data/`.
2. **Data production** (`run:seed` / `run:pull` / `run:predict` / `run:evaluate` /
   `run:reconcile`): produce or update data — the raw-fact corpus (DVC/S3) and/or
   the derived artifacts under `data/`. Do **not** change pipeline code to make
   your task easier, and never weaken validation, CI, lint, type, or security
   checks.

## Where you run: headless in CI

Every `run:*` task runs inside a GitHub Actions runner — a fresh, **ephemeral,
non-interactive** container. Two consequences shape everything you do:

- **No interactive input.** There is no human at a terminal. You cannot ask a
  question and wait for an answer, request confirmation, or pause for approval. If
  you are blocked, under-specified, or need a decision, your only channel is to
  **leave it in writing where a maintainer will see it**, using whatever your run
  grants you: a comment on the PR you open (`gh pr comment`) or its description in
  `run:dev`; a structured **`flags.json`** note alongside your output in
  `run:predict` / `run:evaluate` (the durable, triageable channel — the `collect`
  job rolls every cell's flags into the run PR and the Actions summary, so the note
  survives the trigger issue's closure; see the task prompt and the `AgentFlags`
  schema), with your reasoning/notes doc (`reasoning.md` / `evaluation.md`) for the
  full detail; the run log otherwise. A trigger-issue comment (`gh issue comment`,
  via the scoped token) still works but is lost when the issue closes, so prefer
  `flags.json`. Then make the most conservative reasonable choice and finish —
  never stall waiting for a reply that cannot come.
- **The runner is thrown away.** Its filesystem (and any caches, scratch files, or
  local "memory") is discarded when the job ends. Work survives **only if it is
  pushed off the runner** before you finish:
  - **Code, docs, config, schemas → GitHub.** Persist via a branch + PR. In
    `run:dev` you do this yourself (using the GitHub App token). In `run:predict` /
    `run:evaluate` / `run:reconcile` you only *write files into the working tree*
    and the workflow commits, pushes, and opens the PR — so do **not** push yourself.
  - **Corpus / large historical data → the DVC remote.** Bulk data lives in the
    S3-backed DVC remote, not git, and persists only via `dvc push` (the seed/pull
    workflows own this). A data file left in the working tree but never pushed to
    the remote is lost with the runner. See `docs/data-pipeline.md`.

## The golden rules

- **Branch and PR.** Never commit to `main`. Create a branch, do the work, open
  one focused PR against `main`. (For `run:predict`/`run:evaluate`/`run:reconcile`
  the *workflow* commits and opens the PR — you only write files. The prompt for
  your task says which mode you are in.)
- **The maintainer merges.** Open the PR, get its required checks green, and
  report it ready — do not merge it yourself or enable auto-merge on it. The one
  exception is built into the pipeline: the data-run `collect` jobs open their
  per-run PR with auto-merge, still gated on the same required checks.
- **Stay in your lane.** A predictor writes only under its own
  `predictions/<predictor_id>/<run_id>/` path. An evaluator writes only under its
  own `evaluations/<evaluator_id>/...` path. Never edit another agent's output,
  the docket record, or snapshots.
- **Keep the artifact in view.** The project's progress is measured by what the
  pipeline produces — predictions, events, provisioned cells, reports — not by
  merged PRs. When you make a change, know which produced artifact it serves,
  and say so briefly in the PR description. If the change directly affects
  output, showing a produced example (a provisioned cell, a formed event, a
  rendered report section) is the most useful thing a PR can contain; for
  enabling work further from the output, a one-line "this serves X" is enough.
- **The schema is law.** Every artifact must validate. Run
  `uv run fedcourts validate data` before you finish; if it fails, fix it.
- **Predict from the snapshot.** Predictors reason only from the point-in-time
  snapshot the workflow provisions from the corpus. Do not invent facts or fetch
  new docket facts mid-prediction. (You may use the CourtListener MCP server for
  *legal context* like precedent — never for new case facts.)
- **No secrets in code or data.** Never print, log, or write API tokens. They
  arrive only as environment variables.

## Local gate

The gate that actually blocks a merge is the **required status checks on your
PR** — CI runs the full suite below and the PR cannot merge until it passes. So
locally you have **discretion**: run the subset that fits what you changed, enough
for honest confidence rather than a ritual full run. A docs-only change needs none
of the Python checks; a type fix wants `mypy` and the touched tests; a
pydantic-model change must regenerate `schemas/`. Choose what makes sense — CI is
the backstop.

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run fedcourts validate data
uv run fedcourts dvc-status
uv run fedcourts export-schemas schemas
git diff --exit-code schemas   # CI fails if the committed schemas drift
```

If you touched `.github/workflows` or `.github/actions`, also run the workflow
linters CI enforces — `uvx zizmor@<pinned> --persona=regular .github/workflows
.github/actions` (security: full-SHA action pins, least-privilege permissions)
and `actionlint` (syntax + `run:` shell). See `.github/workflows/lint-actions.yml`
for the pinned versions, and *Authoring or changing a workflow* in
`docs/pipeline.md` for the cross-cutting traps these checks do **not** catch.

**Before you push any change under `.github/workflows` or `.github/actions`, run
the `workflow-reviewer` subagent** (`.claude/agents/workflow-reviewer.md`) on the
diff and resolve its blockers. It runs the linters above and reviews for what they
miss: the security model (fail-closed authorization, the handoff-token gotcha,
expression injection, least privilege) and this repo's **logic-in-tested-Python,
bash-only-plumbs** rule. Treat a clean linter run as necessary but not sufficient.
If you cannot invoke the subagent, self-review against its checklist.

Two things hold no matter what you skip locally:

- **Schema is law.** Every data artifact you write must pass
  `fedcourts validate data`, and any change to a pydantic model's fields **or
  field descriptions** must regenerate and commit `schemas/` — CI fails on drift.
- **Keep the docs in step.** Before you push, check whether your change makes any
  documentation stale — `README.md`, `AGENTS.md`, `docs/`, the prompts under
  `.github/prompts/`, or module/CLI docstrings — and update it in the same PR.
  Docs describe the current design (see Conventions), so a change that lands
  without its doc update leaves them wrong.

## Conventions

- Python ≥ 3.12, managed with `uv`. Source under `src/fedcourtsai/`, tests under
  `tests/`. Fully typed (`mypy --strict`); add tests for new behavior.
- IDs and paths come from `fedcourtsai.ids` and `fedcourtsai.paths` — use them,
  do not hand-build paths. Case = `<court_id>/<docket_id>`; events are
  `evt-<kind>-<slug>`; run ids are UTC timestamps.
- Writes go through `fedcourtsai.serialize` (sorted, newline-terminated) to keep
  diffs minimal.
- Conventional-commit style PR titles, e.g. `predict(claude-baseline): ca9/123 — evt-...`.
- **Be cautious about creating new workflow files.** Before adding one under
  `.github/workflows/`, check whether the task fits as a job or mode on an
  existing workflow (e.g. `run-analytics` for anything that reads the corpus and
  answers a question or refreshes a derived artifact). GitHub scopes permissions
  and tokens per *job*, so a new job is exactly as least-privilege as a new
  file; a task earns its own workflow only when it needs a different trigger
  class or risk class. See *Authoring or changing a workflow* in
  [docs/pipeline.md](docs/pipeline.md).
- **Docs and code describe the current design, not its history.** No issue
  numbers, no changelog, no "we used to / now we" — write what is true now and
  just enough to orient a new reader. This applies to *every committed surface*:
  `docs/`, docstrings, code comments, workflow comments, config comments, and
  prose that code renders (PR bodies, dashboards). Issue numbers rot — state the
  reason in place instead of pointing at a tracker; `git blame` finds the PR (and
  through it the issue) when someone needs the history.
- **Close issues from the PR.** When a PR completes everything an issue asks for,
  put `Closes #<n>` in the PR description so the merge closes it. PR descriptions
  and commit messages are the only places an issue number belongs.
- **`run:*` labels are triggers, not categories.** Applying any `run:*` label to
  an issue immediately starts the matching GitHub Actions workflow and its agent
  (see [docs/pipeline.md](docs/pipeline.md)) — and that agent will do the work,
  even if you are about to do it yourself. Apply one only when you intend to
  start that job *now*; an issue filed for later pickup, or one you plan to fix
  in your own PR, gets no `run:*` label.
- **Keep environment variables out of PR and issue text.** Don't reproduce a
  var's name or value in prose, even when it isn't secret (e.g. the var holding
  the DVC remote's S3 URL); refer to it by its role. Secrets never appear anywhere.
- **Don't commit personal or organizational email addresses.** Commit author and
  committer identity must be a GitHub `noreply` address, and real contact emails
  must not appear in files, commit messages, or PR/issue text — point to
  GitHub-native channels (an issue, the report-abuse flow) instead. If a task
  seems to need a non-`noreply` email anywhere, stop and confirm first.

## Change review

Beyond the gate, changes get a brief adversarial review against three
questions. The review is advisory — it informs the maintainer's merge
decision, it does not block — and "no concerns" is a complete and preferred
answer when true; do not manufacture findings.

1. **Artifact.** Which pipeline output does this change serve, and is the
   PR's claim about that plausible from the diff?
2. **Weakening.** Does anything here weaken a check, gate, validation,
   prompt contract, or security posture under the guise of the task — even
   incidentally?
3. **Cheaper path.** Is there a simpler route to the same artifact that the
   change overlooks?

Independence matters more than thoroughness: the review is most useful when
performed by a session or model that did not author the change. In an
interactive session, the maintainer invokes it by asking a fresh agent (or a
different model) to review the branch against these questions; an authoring
agent asked to self-review should answer honestly rather than defensively,
and flag where self-review is a poor substitute.

## Data model (summary)

Two stores, split by kind. **Raw facts** — dockets, snapshots, judges, case and
tracking metadata, event definitions — live in a packed **corpus** (SQLite under
DVC), written identically by `seed` and `pull`. **Derived artifacts**
live in git under `data/`, keyed by case and event:

```
data/cases/<court_id>/<docket_id>/events/<event_id>/
  outcome.json
  predictions/<predictor_id>/<run_id>/{prediction.json, reasoning.md}
  evaluations/<evaluator_id>/<predictor_id>/<run_id>/{evaluation.json, evaluation.md}
```

Full rationale: `docs/data-model.md` and `docs/data-pipeline.md`. Task-specific
instructions: the prompt file named in your run (under `.github/prompts/`).

## If you are blocked

You are headless (see "Where you run") — there is no one to ask in real time. If
the request is ambiguous or under-specified, make the most conservative reasonable
choice **and say so in writing** so a maintainer can follow up — in whatever
channel your run grants (the PR description or `gh pr comment` in `run:dev`; your
`reasoning.md` / `evaluation.md` and `gh issue comment` in `run:predict` /
`run:evaluate`). Do not wait for a live answer. Prefer a small, correct,
well-tested change over a large speculative one.
