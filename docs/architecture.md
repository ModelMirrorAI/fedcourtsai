# Architecture

fedcourtsai is a **label-driven pipeline** of GitHub Actions over two stores — a
**packed raw-fact corpus** (DVC/S3, written identically by seed and pull) and a
**git-versioned ledger** of derived outcomes, predictions, and evaluations — with
**multiple competing coding agents** producing the predictions and evaluations.

## Components

- **Library (`src/fedcourtsai/`)** — the deterministic core:
  - `courtlistener/` — REST API v4 client (docket + entries) for pull's
    CourtListener enrichment; owns the API-budget throttle.
  - `supremecourt.py` — the SCOTUS live-channel client (per-docket JSON +
    filed-document PDFs; polite, budget-free) and the live identity scheme.
  - `corpus.py` / `corpus_ranged.py` — the packed raw-fact store (rows, events,
    snapshots, documents, tracking cursors) and its ranged read backend that
    queries the blob in place on the DVC remote.
  - `schemas.py` — the pydantic data contract (also exported to `schemas/*.json`).
  - `paths.py` / `ids.py` / `store.py` — the on-disk layout and queries over it.
  - `registry.py` / `matrix.py` — the predictor/evaluator registries (including
    the MCP tool manifest) and the Actions fan-out matrix built from them.
  - `mcp.py` / `retrieval.py` — the cells' MCP client configs emitted from the
    manifest, and the harness-side tool-call transcript capture
    (`retrieval_log.json`) that grounds the evaluators' leakage grading.
  - `pipeline/` — ingestion and contract helpers: the shared normalizer
    (`ingest.py`), pull, the live poller (`live.py`), the past-Term loader
    (`seedlive.py`), document fetch/extraction (`documents.py`), event
    definition, resolution detection, and the predict/evaluate seams.
  - `cli.py` — `fedcourts`, the entry point used by scripts and workflows.
- **Workflows (`.github/workflows/`)** — orchestration; see `pipeline.md`.
- **Prompts (`.github/prompts/`)** — engine-agnostic task instructions shared by
  Claude Code, Codex, and Gemini.
- **Config (`config/`)** — the predictor/evaluator registries and tracking knobs.
- **Data (`data/`)** — the git ledger of derived outcomes, predictions, and
  evaluations. Raw facts (dockets, snapshots, judges, case and event metadata)
  live in the DVC/S3 corpus, not here.

## Why this shape

- **Determinism where it matters.** Docket fetching and scoring are code, so they
  are reproducible and reviewable; only genuinely judgment-heavy work (predicting,
  qualitative evaluation) is delegated to agents.
- **The registry is the source of truth for "which agents exist."** Adding a
  competitor is a one-line config change. This is the seam the future
  hypothesis-generation harness plugs into.
- **Files in git** for the derived ledger give free history, diffing, review, and
  rollback, and let agents load everything concluded about one event from one
  directory. Bulk raw facts would choke git, so they live in a packed corpus
  instead — one format shared by seed and pull.

## Future: automated predictor research

The long-run goal is a harness (in the spirit of Anthropic's
[automated alignment researchers](https://www.anthropic.com/research/automated-alignment-researchers))
that proposes new predictor designs, registers them as new entries in
`config/predictors.yaml` (new prompts/configs), and lets `run-predict` /
`run-evaluate` run the tournament that ranks them. Nothing in the current data or
control flow needs to change for that — a predictor is just an id, an engine, and
a prompt.
