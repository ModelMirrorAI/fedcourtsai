# Data model

The project's state lives in two stores, split by **kind of data**:

- **The corpus** — all *raw facts*: dockets, point-in-time snapshots, judges,
  case metadata and tracking state, and event definitions. A packed, queryable
  store — a single **SQLite** database (`corpus/corpus.db`) — versioned with
  **DVC** (the blob in the DVC remote, its pointer in git). Every ingestion
  channel writes it, in one shared format through one shared ingestion
  core (`fedcourtsai.corpus`).
- **The ledger** — the small, *derived* artifacts under `data/`: outcomes,
  predictions, and evaluations, plus the reasoning that explains them. Plain git,
  validated by the pydantic models in `fedcourtsai.schemas` (exported to
  `schemas/*.schema.json`), reviewed in PRs, and checked by `fedcourts validate
  data` in CI. The layout below shows the shape of a single event's subtree.

The line is deliberate: raw facts are bulk and regenerable, so they live in the
packed corpus; derived judgments are tiny, critical, and worth reading in a diff,
so they live in git.

## The ledger layout (case-centric)

Everything in git is keyed by `case_id` / `event_id`, so a single event's story
sits in one subtree:

```
data/cases/<court_id>/<docket_id>/events/<event_id>/
  outcome.json                    # Outcome: realized ground truth, once resolved
  predictions/<predictor_id>/<run_id>/
    prediction.json               # Prediction: granted 1/0, P(granted), votes
    reasoning.md                  # predicted reasoning (qualitative)
    usage.json                    # ModelUsage: measured tokens + estimated cost
    retrieval_log.json            # RetrievalLog: harness-captured tool calls + manifest
    flags.json                    # AgentFlags: structured feedback (optional)
    tooling.json                  # AgentToolingFeedback: tooling self-report
  evaluations/<evaluator_id>/<run_id>/
    usage.json                    # ModelUsage for the evaluator's run (all predictors)
    retrieval_log.json            # RetrievalLog for the evaluator's own retrieval
    flags.json                    # AgentFlags: structured feedback (optional)
    tooling.json                  # AgentToolingFeedback: tooling self-report
  evaluations/<evaluator_id>/<predictor_id>/<run_id>/
    evaluation.json               # Evaluation: correctness, Brier, vote acc, quality
    evaluation.md                 # qualitative critique
```

Each `usage.json` records one matrix cell's token usage and an estimated USD cost
(rates in `fedcourtsai.pricing`, kept in sync with [budget.md](budget.md)). The
workflow captures it from the engine's own run log — never the agent's word — so a
maintainer can roll it up (`fedcourts usage-summary`) into a measured \$/run. It
also carries the cell's **pipeline provenance**: `pipeline_sha` is the git commit
of the checkout that ran the cell (`GITHUB_SHA` in CI, the local HEAD otherwise),
pinning the prompt templates, harness, and registry in force at run time — the
cell's `prediction.json` / `evaluation.json` identify the acting
*predictor/evaluator design* (`predictor_id` / `evaluator_id`) and the *model*
(`model`); the sha identifies the *system version*. Records written before the
field existed carry no sha (as does a run where no sha is resolvable).

The optional `flags.json` (an `AgentFlags`) is a cell's **durable feedback
channel**: a headless predictor/evaluator writes one only when it has a structured
note to surface — a data-quality problem, a scope question, an ambiguous event, or
the reason it was blocked. Each flag is a typed `{category, severity, message}`.
The `collect` job rolls every cell's flags (predict **and** evaluate)
into the run PR body, the Actions summary, and one long-lived **agent-feedback**
tracking issue (reading even a blocked cell that produced no judgment), so the note
survives the trigger issue's closure — and even a fully-failed run that opens no PR
— and a maintainer sees it without opening every `reasoning.md`. The tracking issue
is the single latched issue pattern of `ops-dashboard` / `data-validation`:
find-or-create one issue under a non-triggering `agent-feedback` label, then post
each flagged run's roll-up as one comment (a hidden per-run marker keeps a
`collect` re-run from duplicating it). Once committed, the `run-ops` dashboard also
surfaces *recent* flags under its **agent signals** section, windowed to the last
two weeks so old, fixed notes age out of the summary (older ones are counted as
archived) — the latched `agent-feedback` issue and the raw `flags.json` ledger keep
the full history. The agent token stays comment-only: the file is written locally
and the trusted `collect` job does the surfacing.

A sibling channel, `tooling.json` (an `AgentToolingFeedback`, schema
`schemas/agent_tooling.schema.json`), is **solicited every run** rather than
written only on a problem: every predict/evaluate cell is invited to file
a short self-report on its *environment and tooling* — `used_corpus_query` (did it
use the `fedcourts` corpus-query CLI, e.g. `query` / `open-events`), `used_base_rates`
(did it use the `stats` base-rate CLI), `tools_used`, `helpful` abilities, `gaps`
(missing or wished-for tools), and optional `notes`. It
lives alongside the cell's other output (`predictions/<predictor>/<run>/tooling.json`,
`evaluations/<evaluator>/<run>/tooling.json`) and is
committed with that output like `usage.json`, **not** rolled into the per-run
PR/issue. Instead the `run-ops` dashboard scans committed `tooling.json` into a
**tooling feedback** digest under its agent-signals section (also windowed to
recent runs) — how many reports used the corpus-query and base-rate CLIs and the
most-mentioned `helpful` abilities and `gaps`. It is subjective and advisory, and
never gates anything.

The raw facts an event is predicted from — its docket, the snapshot, the event
definition itself — live in the corpus, not here. Predictors and evaluators read
them from the corpus, provisioned read-only for their run.

## Identifiers

- **case_id** = `<court_id>/<docket_id>` using the CourtListener court id and the
  stable integer docket id (e.g. `ca9/64512345`).
- **event_id** = `evt-<kind>-<slug>` (e.g. `evt-motion-stay`).
- **run_id** = UTC timestamp (`YYYYMMDDThhmmssZ`) namespacing one agent run.

Always derive these via `fedcourtsai.ids`/`fedcourtsai.paths`; never hand-build.

## Why case-centric

Everything derived about one event — every predictor's prediction, the realized
outcome, and every evaluation — lives under one `events/<event_id>/` directory:

- **Evaluation context is local.** An evaluator reads one directory to see all
  predictors' outputs plus the outcome.
- **Diffs are local.** A new prediction touches only its own run directory.
- **Context loading is simple.** "Everything we've concluded about this event" is
  one subtree.

Predictions from different predictors live together under
`events/<event_id>/predictions/<predictor_id>/` rather than in a separate
per-predictor tree. Co-locating keeps one event's story in one place; the cost is
that a cross-predictor leaderboard is a glob/index rather than a flat scan — a
cheap trade, served by a `fedcourts leaderboard` command.

## The corpus (raw facts)

The historical backlog (all of SCOTUS + the 13 circuits) and the fresh facts
`pull` fetches are far too large to hold as per-case files — millions of YAML
files would choke `git` even under LFS. They land instead in one packed,
normalized, **labeled** corpus, written identically by every channel —
`pull` (the CourtListener REST API) and the supremecourt.gov
live + historical channels (docket JSON) — through one shared normalizer. Each row carries
the realized `disposition`, so the corpus doubles as a back-testing set and a
retrieval source for prediction context. Beside the rows sit the dated
point-in-time snapshots, the predictable-event definitions, per-Term discovery
cursors, and a `documents` table of pipeline-extracted filed-document text
(petition, questions presented, brief in opposition) that provisioning
materializes into a cell's `record/documents/`.

The pydantic models are the contract for the ledger; the corpus is governed by
its own normalized schema (`CorpusRow` in `fedcourtsai.corpus`). The packed store
is a SQLite DB under DVC, but the format is internal — the references the ledger
relies on (ids, dispositions) stay stable regardless. See
[data-pipeline.md](data-pipeline.md) and [corpus/README.md](../corpus/README.md)
for the corpus schema and how the ingestion channels produce it.
