# FedCourtsAI

Agentic AI system to predict events in US federal courts — for example, whether
a motion before a court of appeals or the Supreme Court will be granted or
denied, the likely vote of each judge or justice, and a detailed prediction of
the court's reasoning.

> **Status:** early scaffold. The pipeline shape, data contract, and automation
> are in place; most feature work is done by AI coding agents via the
> label-driven workflows below.

> **Not legal advice.** Outputs are experimental model predictions, not legal
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
| `run:seed`     | `run-seed`      | Pull initial dockets from CourtListener and start tracking them      | Script |
| `run:pull`     | `run-pull`      | Refresh tracked dockets (also runs on a daily schedule)             | Script (agent only if ambiguous) |
| `run:predict`  | `run-predict`   | Predict open events with **multiple competing predictors** (fan-out) | Claude Code + Codex |
| `run:evaluate` | `run-evaluate`  | Score past predictions against realized outcomes (evaluator × predictor) | Claude Code + Codex |

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
                                            (outcome lands via pull)
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
judges, case and event metadata — go into a packed **corpus** (Parquet or SQLite
under DVC/S3), written identically by `seed` and `pull`. **Derived artifacts** are
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

The `seed` and `pull` CLI commands are single-docket helpers that fetch one case
from the CourtListener REST API, so they need a free API token:

```bash
export FEDCOURTS_COURTLISTENER_API_TOKEN=...   # https://www.courtlistener.com/help/api/rest/
uv run fedcourts seed --court ca9 --docket <docket_id>   # fetch one docket, start tracking
uv run fedcourts pull --court ca9 --docket <docket_id>   # refresh one tracked docket
```

The pipeline's `run-seed` workflow is a different path: it backfills the
historical corpus from CourtListener **bulk data** (no API budget). See
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
- [Data model](docs/data-model.md)
- [Pipeline & labels](docs/pipeline.md)
- [Security](SECURITY.md)
- [Agent workflow](docs/agent-workflow.md)

## License

MIT — see [LICENSE](LICENSE).
