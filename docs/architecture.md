# Architecture

fedcourtsai is a **label-driven pipeline** of GitHub Actions over a **git-versioned
data store**, with **multiple competing coding agents** producing predictions and
evaluations.

## Components

- **Library (`src/fedcourtsai/`)** — the deterministic core:
  - `courtlistener/` — REST API v4 client (docket + entries) for seed/pull.
  - `schemas.py` — the pydantic data contract (also exported to `schemas/*.json`).
  - `paths.py` / `ids.py` / `store.py` — the on-disk layout and queries over it.
  - `registry.py` / `matrix.py` — load the predictor/evaluator registries and
    build the Actions fan-out matrix from them.
  - `pipeline/` — seed, pull, and the predict/evaluate contract helpers.
  - `cli.py` — `fedcourts`, the entry point used by scripts and workflows.
- **Workflows (`.github/workflows/`)** — orchestration; see `pipeline.md`.
- **Prompts (`.github/prompts/`)** — engine-agnostic task instructions shared by
  Claude Code and Codex.
- **Config (`config/`)** — the predictor/evaluator registries and tracking knobs.
- **Data (`data/`)** — the versioned record of cases, predictions, evaluations.

## Why this shape

- **Determinism where it matters.** Docket fetching and scoring are code, so they
  are reproducible and reviewable; only genuinely judgment-heavy work (predicting,
  qualitative evaluation) is delegated to agents.
- **The registry is the source of truth for "which agents exist."** Adding a
  competitor is a one-line config change. This is the seam the future
  hypothesis-generation harness plugs into.
- **Files in git** give free history, diffing, review, and rollback, and let agents
  load full context for one case from one directory.

## Future: automated predictor research

The long-run goal is a harness (in the spirit of Anthropic's
[automated alignment researchers](https://www.anthropic.com/research/automated-alignment-researchers))
that proposes new predictor designs, registers them as new entries in
`config/predictors.yaml` (new prompts/configs), and lets `run-predict` /
`run-evaluate` run the tournament that ranks them. Nothing in the current data or
control flow needs to change for that — a predictor is just an id, an engine, and
a prompt.
