# AGENTS.md

Canonical instructions for AI coding agents (Claude Code, Codex) working in this
repository. `CLAUDE.md` points here. Read this fully before doing anything.

## What this project is

fedcourtsai predicts events in US federal courts (e.g. whether a motion will be
granted/denied, how each judge votes, and the court's likely reasoning). It runs
as a label-driven pipeline of GitHub Actions; see `docs/pipeline.md`.

There are two very different kinds of work, and you are doing exactly one of them
in any given run:

1. **Pipeline development** (`run:dev`): change the Python package, workflows,
   docs, schemas, or prompts. Do **not** touch `data/`.
2. **Data production** (`run:seed` / `run:predict` / `run:evaluate`): produce or
   update artifacts under `data/`. Do **not** change pipeline code to make your
   task easier, and never weaken validation, CI, lint, type, or security checks.

## Where you run: headless in CI

Every `run:*` task runs inside a GitHub Actions runner — a fresh, **ephemeral,
non-interactive** container. Two consequences shape everything you do:

- **No interactive input.** There is no human at a terminal. You cannot ask a
  question and wait for an answer, request confirmation, or pause for approval.
  Every `run:*` job hands the agent a **scoped GitHub token**, so when you are
  blocked, under-specified, or need a decision you can **leave it in writing where
  a maintainer will see it**: comment on the triggering issue
  (`gh issue comment <n>`) or on the PR you open (`gh pr comment`). For
  `run:predict` / `run:evaluate`, also record durable reasoning in your output doc
  (`reasoning.md` / `evaluation.md`). Then make the most conservative reasonable
  choice and finish — never stall waiting for a reply that cannot come.
- **The runner is thrown away.** Its filesystem (and any caches, scratch files, or
  local "memory") is discarded when the job ends. Work survives **only if it is
  pushed off the runner** before you finish:
  - **Code, docs, config, schemas → GitHub.** Persist via a branch + PR. In
    `run:dev` you do this yourself (using the GitHub App token). In `run:predict` /
    `run:evaluate` / `run:seed` you only *write files into the working tree* and
    the workflow commits, pushes, and opens the PR — so do **not** push yourself.
  - **Corpus / large historical data → the DVC remote.** Bulk data lives in the
    S3-backed DVC remote, not git, and persists only via `dvc push` (the seed/pull
    workflows own this). A data file left in the working tree but never pushed to
    the remote is lost with the runner. See `docs/data-pipeline.md`.

## The golden rules

- **Branch and PR.** Never commit to `main`. Create a branch, do the work, open
  one focused PR against `main`. (For `run:predict`/`run:evaluate` the *workflow*
  commits and opens the PR — you only write files. The prompt for your task says
  which mode you are in.)
- **Stay in your lane.** A predictor writes only under its own
  `predictions/<predictor_id>/<run_id>/` path. An evaluator writes only under its
  own `evaluations/<evaluator_id>/...` path. Never edit another agent's output,
  the docket record, or snapshots.
- **The schema is law.** Every artifact must validate. Run
  `uv run fedcourts validate data` before you finish; if it fails, fix it.
- **Predict from the snapshot.** Predictors reason from the committed
  `record/snapshots/<date>.json` only. Do not invent facts or fetch new docket
  facts mid-prediction. (You may use the CourtListener MCP server for *legal
  context* like precedent — never for new case facts.)
- **No secrets in code or data.** Never print, log, or write API tokens. They
  arrive only as environment variables.

## Local gate (must pass before every PR)

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run fedcourts validate data
```

If you changed the pydantic models, regenerate schemas and commit them:
`uv run fedcourts export-schemas schemas` (CI fails if they drift).

## Conventions

- Python ≥ 3.12, managed with `uv`. Source under `src/fedcourtsai/`, tests under
  `tests/`. Fully typed (`mypy --strict`); add tests for new behavior.
- IDs and paths come from `fedcourtsai.ids` and `fedcourtsai.paths` — use them,
  do not hand-build paths. Case = `<court_id>/<docket_id>`; events are
  `evt-<kind>-<slug>`; run ids are UTC timestamps.
- Writes go through `fedcourtsai.serialize` (sorted, newline-terminated) to keep
  diffs minimal.
- Conventional-commit style PR titles, e.g. `predict(claude-baseline): ca9/123 — evt-...`.

## Data model (summary)

```
data/cases/<court_id>/<docket_id>/
  case.yaml
  record/{docket.json, snapshots/<YYYY-MM-DD>.json}
  events/<event_id>/
    event.yaml
    outcome.json
    predictions/<predictor_id>/<run_id>/{prediction.json, reasoning.md}
    evaluations/<evaluator_id>/<predictor_id>/<run_id>/{evaluation.json, evaluation.md}
```

Full rationale: `docs/data-model.md`. Task-specific instructions: the prompt file
named in your run (under `.github/prompts/`).

## If you are blocked

You are headless (see "Where you run") — there is no one to ask in real time. If
the request is ambiguous or under-specified, make the most conservative reasonable
choice **and say so in writing** so a maintainer can follow up: comment on the
triggering issue (`gh issue comment <n>`) or the PR (`gh pr comment`), and record
durable reasoning in your `reasoning.md` / `evaluation.md` where the task has one.
Do not wait for a live answer. Prefer a small, correct, well-tested change over a
large speculative one.
