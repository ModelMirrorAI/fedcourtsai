# FedCourtsAI

[![CI](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/ci.yml/badge.svg)](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/ci.yml)
[![lint-actions](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/lint-actions.yml/badge.svg)](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/lint-actions.yml)
[![codeql](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/codeql.yml/badge.svg)](https://github.com/ModelMirrorAI/fedcourtsai/actions/workflows/codeql.yml)
[![Python ≥3.12](https://img.shields.io/badge/python-%E2%89%A53.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Agentic AI system to predict events in US federal courts — for example,
whether a petition for certiorari will be granted or denied, the likely vote
of each justice, and the court's reasoning.

> **Status:** the pipeline is live. Ingestion runs daily across the Supreme
> Court and the thirteen courts of appeals, the supremecourt.gov live channel
> tracks pending cert petitions in production, and the forward record begins
> with the OT2026 cert cycle: the open ledger under `data/` holds SCOTUS
> events and realized outcomes, with predictions and evaluations accumulating
> toward the OT2026 long-conference cert release ([milestones](docs/milestones.md)).

> **Not legal advice.** Outputs are experimental model predictions — they may
> be wrong, carry no affiliation with or endorsement by any court, and are not
> legal advice or a forecast to rely on for any decision. Predictions of how
> individual judges or justices may vote describe *likely outcomes* — not
> assertions of fact, and not statements about how anyone should decide.

## How it works

The project runs as a **label-driven pipeline of GitHub Actions**: work is
represented as GitHub issues, applying a `run:*` label triggers the matching
workflow, and a stage hands off by opening (or labeling) an issue for the next
stage. The judgment-heavy stages delegate to **multiple competing coding
agents** (Claude Code, Codex, and Gemini), whose artifacts land as
auto-merge-gated pull requests.

| Label          | Workflow        | Does                                                                 | Engine |
|----------------|-----------------|----------------------------------------------------------------------|--------|
| `run:pull`     | `run-pull`      | Three scheduled writer jobs: targeted CourtListener enrichment, the **supremecourt.gov live poll** (discovers pending petitions, tracks conference distribution, records outcomes, provisions filed-document text), and the daily **historical Term walker** for base rates and back-testing | Script |
| `run:predict`  | `run-predict`   | Predict open events with **multiple competing predictors** (fan-out) | Claude Code + Codex + Gemini |
| `run:evaluate` | `run-evaluate`  | Score past predictions against realized outcomes (evaluator × predictor) | Claude Code + Codex + Gemini |
| `run:backtest` | `run-backtest`  | Maintainer-triggered cert back-test: replay predictors over decided petitions (outcomes hidden), land `metrics/cert-backtest.json` as a reviewed PR | Claude Code + Codex (replay) |

Plus `run-ops` (a read-only daily dashboard with a weekly digest) and
`run-analytics` (corpus analysis and metrics refresh), both schedule/dispatch
only. The cascade runs pull/live → corpus → `run:predict` (fired on a
conference distribution or a changed open case) → `run:evaluate` (fired when an
outcome lands on a predicted event); full label/workflow mechanics and the
cascade diagram: [`docs/pipeline.md`](docs/pipeline.md).

### Why this shape

**Determinism where it matters**: ingestion, event definition, and quantitative
scoring are code — reproducible and reviewable; only genuinely judgment-heavy
work (predicting, qualitative evaluation) goes to agents. **The registry is the
source of truth for "which agents exist"**: adding a competitor is a one-line
config change (`config/predictors.yaml`), and long term an automated-research
harness (in the spirit of Anthropic's
[automated alignment researchers](https://www.anthropic.com/research/automated-alignment-researchers))
proposes new predictor designs on this same seam, with `run-evaluate` the
tournament that ranks them. **Files in git** for the derived ledger give free
history, diffing, review, and rollback; bulk raw facts would choke git, so they
live in the packed corpus instead (see *Data model*).

## Prediction scope

Ingestion covers all fourteen courts, but the agentic predict/evaluate stages
are **deliberately narrower** — prediction runs only where the event model fits
and ground truth is recoverable. The scope is **SCOTUS dockets only**
(`predict.scope=scotus_docket`: the corpus row's `court == "scotus"`), minus a
set of deterministic exclusions applied from the corpus at the prediction
matrix: **pre-1925 mandatory-jurisdiction matters** (heard as of right, so the
discretionary-cert event model does not apply), **stale, unresolvable
petitions** (decades-old stubs whose ground truth the corpus can never
recover), **non-cert SCOTUS docket forms** (stay/emergency applications and
original-jurisdiction matters resolve as stays or merits rulings, not cert
grant/deny), **decided-on-paper-only cases** (a published opinion with no
machine-readable disposition), and **internally inconsistent dates** (a docket
that reads decided before it was filed).

Originating court-of-appeals dockets — including remand activity after a grant
— are ingested for context and retrieval but not predicted. This is a scope
dial, not a permanent limit; widening is a cost-data-driven decision
([`docs/budget.md`](docs/budget.md), [milestones](docs/milestones.md)), and
the mechanics live in [`docs/data-pipeline.md`](docs/data-pipeline.md).

## Data model

State lives in two stores, split by **kind of data**:

- **Raw facts → the corpus.** Dockets, point-in-time snapshots, judges, case and
  tracking metadata, and event definitions, written identically by every
  ingestion channel through one shared core. The corpus has two halves: a
  small, **payload-free SQLite index** (`corpus/corpus.db`, versioned with DVC
  — the blob in a private S3 remote, the pointer in git) serving queries,
  scans, scope gating, and base rates; and a browsable, **write-once per-case
  content store** (an access-gated S3 store, `fedcourtsai.casestore`) holding
  the bulk payloads — dated snapshots, extracted filed-document text, opinion
  bodies — keyed to mirror the ledger's `data/cases/<court>/<docket>/` shape.
  Only changed cases upload, so storage scales with case churn, not run count,
  and forward predict/evaluate cells provision their case record from the
  store. (The `FEDCOURTS_CORPUS_SPLIT` flag selects these split read/write
  paths; it is on in the production `runner` environment and defaults off, so
  a dev environment without the store works against a self-contained blob.)
- **Derived judgments → the git ledger.** Outcomes, predictions, and
  evaluations under `data/`, organized **case-centrically** so everything
  concluded about a single predictable event lives in one subtree:

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

The line is deliberate: raw facts are bulk and regenerable, so they live in
the packed, access-gated corpus (per-case content objects stay behind index
pointers, never git tree entries); derived judgments are tiny, critical, and
worth reading in a diff, so they live in git, validating against the pydantic
models in `fedcourtsai.schemas` (exported to `schemas/*.schema.json`). Full
design: [`docs/data-pipeline.md`](docs/data-pipeline.md).

## Develop

Requires [uv](https://docs.astral.sh/uv/). A devcontainer is included
(`.devcontainer/`) and is the recommended way to work in Codespaces.

```bash
uv sync                       # install deps into .venv
uv run fedcourts --help       # CLI (full reference: docs/cli.md)
uv run fedcourts validate data
# the local gate CI also runs:
uv run ruff format --check . && uv run ruff check .
uv run mypy && uv run pytest
```

`pull` fetches one case from the CourtListener REST API into the corpus
through the shared ingestion core (needs a free API token); `historical-terms`
loads decided SCOTUS petitions from the supremecourt.gov docket JSON (no API
budget):

```bash
export FEDCOURTS_COURTLISTENER_API_TOKEN=...   # https://www.courtlistener.com/help/api/rest/
uv run fedcourts pull --court ca9 --docket <docket_id>
uv run fedcourts historical-terms --report historical-report.json
```

## For AI agents

Start with [`AGENTS.md`](AGENTS.md) — the canonical instruction file; it
defines the branch-and-PR workflow every agent (and human) change follows.

## Repository layout

```
src/fedcourtsai/    library: clients, corpus + casestore, schemas, registry, CLI
config/             predictor & evaluator registries, tracking settings
data/               the git ledger of derived judgments (versioned)
schemas/            JSON Schema exported from the pydantic models
docs/               data pipeline, sources, security, budget, milestones
.github/workflows/  the label-driven pipeline + CI + workflow linting
.github/prompts/    engine-agnostic prompts shared by the three engines
```

## Documentation

- [Data pipeline](docs/data-pipeline.md) (the corpus & ingestion) · [Live sources](docs/live-sources.md) · [Data sources, terms & PII](docs/data-sources.md)
- [Pipeline & labels](docs/pipeline.md) · [CLI reference](docs/cli.md)
- [Budget](docs/budget.md) · [Milestones](docs/milestones.md)
- [Security](SECURITY.md) · [setup runbook](docs/security.md)
- [Testing](docs/testing.md) · [Contributing](CONTRIBUTING.md)

## Data & attribution

Court data comes from [CourtListener](https://www.courtlistener.com/), a
project of the [Free Law Project](https://free.law/) — via the CourtListener
REST API — and from **supremecourt.gov**'s per-docket JSON and filed-document
PDFs, public records served by the Court itself. A great deal of this project
rests on Free Law Project's work; please review and support it. Use of their
data is governed by
[CourtListener's terms](https://www.courtlistener.com/terms/) (CC BY-ND 4.0 for
CourtListener's own content; the underlying federal records are public domain),
with attribution also recorded in the top-level [`NOTICE`](NOTICE).

The derived corpus is **not** publicly republished — it stays in an
access-gated store; only our model-generated judgments over those public
records reach public git. We ingest only public-record dockets and never sealed
or privileged material. See [docs/data-sources.md](docs/data-sources.md) for
the full position on terms, redistribution, the API budget, and PII.

FedCourtsAI is independent and is **not** affiliated with or endorsed by the
Free Law Project or any court. Court records are public records of the U.S.
federal courts; the predictions and evaluations in this repository are
model-generated and are not official court records.

## License

MIT — see [LICENSE](LICENSE).
