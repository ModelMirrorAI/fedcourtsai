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

Prefer a small, correct, well-tested change over a large speculative one. If the
request is ambiguous or under-specified, say so in the PR description and make the
most conservative reasonable choice rather than guessing widely.
