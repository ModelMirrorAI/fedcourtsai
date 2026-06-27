# FedCourtsAI

[![CI](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/ci.yml/badge.svg)](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/ci.yml)
[![lint-actions](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/lint-actions.yml/badge.svg)](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/lint-actions.yml)
[![Python ≥3.12](https://img.shields.io/badge/python-%E2%89%A53.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Agentic AI system to predict events in US federal courts — for example, whether
a motion before a court of appeals or the Supreme Court will be granted or
denied, the likely vote of each judge or justice, and a detailed prediction of
the court's reasoning.

> **Status:** early scaffold. The pipeline shape, data contract, and automation
> are in place; most feature work is done by AI coding agents via the
> label-driven workflows below.

> **Not legal advice.** Outputs are experimental model predictions — they may be
> wrong, carry no affiliation with or endorsement by any court, and are not legal
> advice or a forecast you should rely on for any decision.

## How it works

The project runs as a **label-driven pipeline of GitHub Actions**. Work is
represented as GitHub issues; applying a `run:*` label triggers the matching
workflow. When a stage needs to hand off, it opens (or labels) an issue to
trigger the next stage. Several stages delegate to agentic coding tools
(Claude Code and Codex), which branch, do the work, and open a pull request.

| Label          | Workflow        | Does                                                                 | Engine |
|----------------|-----------------|----------------------------------------------------------------------|--------|
| `run:dev`      | `run-dev`       | Normal development on the pipeline codebase                          | Claude Code |
| `run:seed`     | `run-seed`      | Ingest initial dockets from CourtListener into the corpus            | Script |
| `run:pull`     | `run-pull`      | Refresh tracked dockets (also runs on a daily schedule)             | Script (agent only if ambiguous) |
| `run:reconcile`| `run-reconcile` | Confirm a decided event's `outcome.json` from the docket when pull can't | Claude Code |
| `run:predict`  | `run-predict`   | Predict open events with **multiple competing predictors** (fan-out) | Claude Code + Codex |
| `run:evaluate` | `run-evaluate`  | Score past predictions against realized outcomes (evaluator × predictor) | Claude Code + Codex |

Plus `run-ops`, a read-only daily health & cost dashboard that has no `run:*`
label — it runs on a schedule (or manual dispatch). See [`docs/pipeline.md`](docs/pipeline.md).

```
run:seed ──▶ seed dockets ──▶ (merge)
                                 │
        daily schedule / run:pull│
                                 ▼
                          refresh dockets ──changed?──▶ open issue: run:predict
                                                                │
                                                                ▼
                                          predict (matrix over predictors) ──▶ PRs
                                                                │
                                       (outcome lands via pull, or run:reconcile)
                                                                ▼
                                       run:evaluate ──▶ score every predictor ──▶ PRs
```

Longer term, an automated-research harness (in the spirit of Anthropic's
[automated alignment researchers](https://www.anthropic.com/research/automated-alignment-researchers))
proposes new predictor designs, registers them as new entries in the predictor
registry, and lets them compete — so `run-predict` tracks a growing field of
agents and `run-evaluate` is the tournament that ranks them.

## Data model

State lives in two stores, split by kind. **Raw facts** — dockets, snapshots,
judges, case and event metadata — go into a packed **corpus** (SQLite under
DVC/S3), written identically by `seed` and `pull`. **Derived artifacts** are
versioned as files in git, organized **case-centrically** so everything we
conclude about a single predictable event lives together:

```
data/cases/<court_id>/<docket_id>/events/<event_id>/
  outcome.json                   # ground truth, once the event resolves
  predictions/<predictor_id>/<run_id>/
    prediction.json              # quantitative: granted 1/0, P(granted), votes
    reasoning.md                 # qualitative: predicted reasoning
  evaluations/<evaluator_id>/<predictor_id>/<run_id>/
    evaluation.json
    evaluation.md
```

Every git artifact validates against a pydantic model in `fedcourtsai.schemas`
(exported to `schemas/*.schema.json`). See [`docs/data-model.md`](docs/data-model.md)
for the rationale and [`docs/data-pipeline.md`](docs/data-pipeline.md) for the
corpus.

## Develop

Requires [uv](https://docs.astral.sh/uv/). A devcontainer is included
(`.devcontainer/`) and is the recommended way to work in Codespaces.

```bash
uv sync                       # install deps into .venv
uv run fedcourts --help       # CLI
uv run fedcourts export-schemas
uv run fedcourts validate data

# the local gate CI also runs:
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```

`seed` and `pull` are single-docket REST helpers that fetch one case from the
CourtListener REST API into the corpus through the shared ingestion core, so they
need a free API token. `seed` onboards a docket; `pull` refreshes one and reports
whether it changed:

```bash
export FEDCOURTS_COURTLISTENER_API_TOKEN=...   # https://www.courtlistener.com/help/api/rest/
uv run fedcourts seed --court ca9 --docket <docket_id>   # onboard one docket into the corpus
uv run fedcourts pull --court ca9 --docket <docket_id>   # refresh one docket; report changes
```

The historical mass is loaded by `seed-backfill`, what the `run-seed` workflow
runs: deterministic, no-agent ingestion of CourtListener **bulk data** (no API
token, no API budget) into the *same* corpus through the *same* core. It loads
one chunk of the tracked courts per run against a resumable cursor
(`config/seed-progress.yaml`), chunked until complete:

```bash
uv run fedcourts seed-backfill --report seed-report.json   # load the next bulk chunk
```

See [`docs/seed-backfill.md`](docs/seed-backfill.md) and
[`docs/data-pipeline.md`](docs/data-pipeline.md).

## For AI agents

Start with [`AGENTS.md`](AGENTS.md) — it is the canonical instruction file and
defines the branch-and-PR workflow every agent follows. `CLAUDE.md` points to it.

## Repository layout

```
src/fedcourtsai/    library: CourtListener client, schemas, paths, registry, CLI
config/             predictor & evaluator registries, tracking settings
data/               tracked cases (versioned)
schemas/            JSON Schema exported from the pydantic models
docs/               architecture, data model, pipeline, security
.github/workflows/  the label-driven pipeline + CI + workflow linting
.github/prompts/    engine-agnostic prompts used by both Claude Code and Codex
```

## Documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data-model.md) · [Data pipeline](docs/data-pipeline.md) (the corpus)
- [Pipeline & labels](docs/pipeline.md)
- [Seed-backfill](docs/seed-backfill.md)
- [Budget](docs/budget.md)
- [Milestones](docs/milestones.md)
- [Security](SECURITY.md) · [setup runbook](docs/security.md)
- [Agent workflow](docs/agent-workflow.md) · [Contributing](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
