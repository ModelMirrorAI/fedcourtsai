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
2. **Data production** (`run:seed` / `run:pull` / `run:predict` / `run:evaluate`):
   produce or update data — the raw-fact corpus (DVC/S3) and/or the derived
   artifacts under `data/`. Do **not** change pipeline code to make your task
   easier, and never weaken validation, CI, lint, type, or security checks.

## Where you run: headless in CI

Every `run:*` task runs inside a GitHub Actions runner — a fresh, **ephemeral,
non-interactive** container. Two consequences shape everything you do:

- **No interactive input.** There is no human at a terminal. You cannot ask a
  question and wait for an answer, request confirmation, or pause for approval. If
  you are blocked, under-specified, or need a decision, your only channel is to
  **leave it in writing where a maintainer will see it**, using whatever your run
  grants you: a comment on the PR you open (`gh pr comment`) or its description in
  `run:dev`; your reasoning/notes doc (`reasoning.md` / `evaluation.md`) plus a
  comment on the triggering issue (`gh issue comment`, via the scoped token the
  workflow provides) in `run:predict` / `run:evaluate`; the run log otherwise.
  Then make the most conservative reasonable choice and finish — never stall
  waiting for a reply that cannot come.
- **The runner is thrown away.** Its filesystem (and any caches, scratch files, or
  local "memory") is discarded when the job ends. Work survives **only if it is
  pushed off the runner** before you finish:
  - **Code, docs, config, schemas → GitHub.** Persist via a branch + PR. In
    `run:dev` you do this yourself (using the GitHub App token). In `run:predict` /
    `run:evaluate` you only *write files into the working tree* and the workflow
    commits, pushes, and opens the PR — so do **not** push yourself.
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
- **Predict from the snapshot.** Predictors reason only from the point-in-time
  snapshot the workflow provisions from the corpus. Do not invent facts or fetch
  new docket facts mid-prediction. (You may use the CourtListener MCP server for
  *legal context* like precedent — never for new case facts.)
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
uv run fedcourts export-schemas schemas
git diff --exit-code schemas   # CI fails if the committed schemas drift
```

The last two lines mirror CI's schema-drift check: any change to a pydantic
model's fields **or field descriptions** regenerates `schemas/` — commit the
result, or the gate fails.

## Conventions

- Python ≥ 3.12, managed with `uv`. Source under `src/fedcourtsai/`, tests under
  `tests/`. Fully typed (`mypy --strict`); add tests for new behavior.
- IDs and paths come from `fedcourtsai.ids` and `fedcourtsai.paths` — use them,
  do not hand-build paths. Case = `<court_id>/<docket_id>`; events are
  `evt-<kind>-<slug>`; run ids are UTC timestamps.
- Writes go through `fedcourtsai.serialize` (sorted, newline-terminated) to keep
  diffs minimal.
- Conventional-commit style PR titles, e.g. `predict(claude-baseline): ca9/123 — evt-...`.
- **Docs describe the current design, not its history.** No issue numbers, no
  changelog, no "we used to / now we" — write what is true now and just enough to
  orient a new reader.
- **Close issues from the PR.** When a PR completes everything an issue asks for,
  put `Closes #<n>` in the PR description so the merge closes it. The PR
  description is the one place an issue number belongs.
- **Keep environment variables out of PR and issue text.** Don't reproduce a
  var's name or value in prose, even when it isn't secret (e.g. the var holding
  the DVC remote's S3 URL); refer to it by its role. Secrets never appear anywhere.

## Data model (summary)

Two stores, split by kind. **Raw facts** — dockets, snapshots, judges, case and
tracking metadata, event definitions — live in a packed **corpus** (Parquet or
SQLite under DVC), written identically by `seed` and `pull`. **Derived artifacts**
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
