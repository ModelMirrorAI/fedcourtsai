# Case summaries

A plain-language account of each predicted case — what happened, what the
Court is being asked, where it stands — for site readers who do not already
know the case. The forecasts assume a reader who does; a summary is the page
that makes them legible. Summaries are **display material**: nothing scores
one, and no metric, leaderboard or board artifact reads one.

## The artifact

One markdown file per case per record:

```
data/cases/<court_id>/<docket_id>/summaries/<YYYY-MM-DD>.md
```

named for the corpus snapshot day it was generated from
(`CasePaths.summary`). It sits beside `record/`, not inside it: `record/` is
gitignored so a snapshot can never be committed, while a summary is committed
and published.

The front matter is written by the harness, never by the model
(`CaseSummaryFrontMatter`, exported as
`schemas/case_summary_front_matter.schema.json`):

```yaml
---
case_id: scotus/9026000239
snapshot: '2026-09-20'
record_digest: sha256:…     # the record the body was written from
model: claude-sonnet-5
prompt_digest: sha256:…     # .github/prompts/summarize.md as sent
generated_at: '2026-09-23T04:02:11Z'
usage:
  input_tokens: 48210
  output_tokens: 391
  estimated_cost_usd: 0.100330
---
```

The body carries exactly three sections, in this order, about 250 words in
all:

- `## What happened` — the dispute and how it reached the Court (~100 words).
- `## What the Court is being asked` — the question, restated without a
  "Whether…" construction or citations.
- `## Where it stands` — the posture in one or two sentences.

`fedcourts validate data` checks every committed summary: the name is a day,
the front matter validates, its `case_id` and `snapshot` match the path, and
the body meets the contract's shape — the three headings in order with nothing
before the first, no empty section, no paragraph opening with "Whether", and
none of the markup below. A hand edit on the refresh PR is held to the same
rules; only the length band is left to generation time.

## The summarizer's contract

The prompt is `.github/prompts/summarize.md`. Its rules:

- **Grounded in the record only.** The request carries the prompt and the
  staged record — the snapshot and the stored documents — and nothing else: no
  tools, no retrieval, thinking off. So a summary cannot carry a post-snapshot
  development, commentary, or an outcome the record does not show; the model is
  also told not to add what it may know from training.
- **Neutral.** Both sides' positions; no prediction, no view on the merits, no
  characterisation of the case's importance.
- **Glossary terms.** Where a legal term is unavoidable, one of cert, relist,
  CVSG, GVR, emergency application, merits, reverse/vacate, explained in
  passing. The repository holds no site glossary, so the prompt defines each
  term itself, minimally; a site glossary, once it exists, is the definition to
  align the prompt with.
- **Accurate to the record.** An allegation only one side's filing makes is
  attributed to that filing; a question presented is restated without changing
  who made the rule, whom it binds, or which way it cuts; routine docket
  entries are left out, and one that matters to the posture is named as the
  docket names it; a request the docket shows only as filed is not reported
  as granted; dates and counts are as the entries give them.
- **People.** Named only as the caption and filings name them; initials stay
  initials; no personal detail beyond the dispute.

`record/context.json` is **not** sent. It carries the pipeline's conditioning
state for a cell — the salience band among it — which is not a fact about the
case, and a band is exactly the importance signal the neutrality rule keeps out
of a summary.

The harness accepts a response only if it ended normally (`end_turn`), has
exactly the three headings in order with nothing before the first, runs
120–450 words (a tolerant band around the 250 asked for), opens no paragraph
with "Whether", carries no markup — no HTML tag or autolink, no markdown link or
image, no URL, no list item, no bold or code formatting — and passes the secret
scan. The markup rule is the harness's, not only the prompt's: a summary
reaches a public page, its text derives from third-party filings, and an
instruction injected into a filing that survived into the output could
otherwise place a script, a tracking image or a link there. Anything else is
not written; the case is reported skipped with the reason, and the cost of the
call is still counted.

## Which cases, and when

**Eligible:** every case with at least one committed prediction
(`store.iter_predicted_events`) — summarized only while its newest snapshot is
the Court's own supremecourt.gov docket JSON (it carries the proceedings list,
`ProceedingsandOrder`). A case whose newest snapshot is a CourtListener REST
docket is counted in the plan (`not_live_shaped`) and not summarized: the
staged record crosses a public artifact and the summary is published, and
CourtListener's content is CC BY-ND, which no public surface of this project
carries ([data-sources.md](data-sources.md)). The Court's docket JSON and the
supremecourt.gov filings are public records. `summarize` refuses a staged
snapshot of the other shape too.

**Owed a summary:** when the `record_digest` of its newest corpus record
differs from the `record_digest` in its newest committed summary's front
matter — or it has no summary. The digest is sha256 over the newest snapshot
payload in canonical JSON with its generation stamps removed
(`provision.GENERATION_STAMPS`: the pull's own timestamp), plus the sorted
`(kind, sha256(text))` pair of each stored document. Documents are in the
digest because they arrive days after the docket entry that links them, so a
record whose docket is unchanged but whose petition text has just landed is a
new record to summarize.

The rule is keyed on content, not on the snapshot day, because of what the
corpus actually holds: measured on 2026-09-23, about 100 of the 195 predicted
cases gained a new dated snapshot every day, but 177 of 185 consecutive-day
snapshot pairs were identical once the generation stamp was ignored. A
day-keyed rule would pay to rewrite an unchanged summary for half the ledger
every day; the content-keyed one writes for the ~4% of records that changed.

The run is idempotent: over an up-to-date ledger the plan is empty and nothing
is written. The first run on `main` is the backfill — every eligible case,
about 195 — and each later run writes only for changed records. Planned cases
are ordered cases-without-a-summary first, then changed records, so a
`limit` spends on the cases a reader has nothing for.

## The model

`summaries.model` in `config/tracking.yaml`: **Claude Sonnet 5**
(`claude-sonnet-5`, $2 / $10 per million input / output tokens,
`pricing.MODEL_RATES`). The task is a faithful restatement of a record, which
a mid-tier model does well at a fifth of the frontier rate, and it is outside
the prediction panel, so no summary is written by a model being scored.

Changing it is a reviewed config edit. The plan names the model it priced, and
`summarize` refuses a plan made for another model than the configured one; every
summary written after the change names the new model in its front matter, and
earlier summaries keep theirs. A model the rate table cannot price is refused
at plan time. The same section holds `max_output_tokens` (a response that
reaches it is rejected, not written) and `max_document_chars`, the
per-document cap on what the model reads, marked in the text with
`[truncated: N of M characters shown]` so one outsized brief cannot blow up a
run's cost.

## The workflow

`.github/workflows/summarize.yml` — its own workflow, because it spends model
tokens behind its own hold and runs on its own daily schedule (03:43 UTC,
clear of `run-predict` and `run-evaluate`). One run per ref at a time. Six
jobs:

| Job | Holds | Does |
|---|---|---|
| `plan` | read-only corpus role | stands down (a notice, no work) while a `run-predict` or `run-evaluate` run is executing — a round parked on its own hold or queued does not count, and the check is at plan time only, so a round can still start while this run's generate job works; counts an open `summaries/refresh` PR's summaries as written; `fedcourts summarize-plan` → the plan and the report the hold is judged on |
| `approval` | nothing (`review` environment) | the spend hold |
| `stage` | read-only corpus role | `provision-snapshot` for each planned case, into a data root under `$RUNNER_TEMP` |
| `generate` | the environment's Anthropic key, and asserts it holds no cloud credential | `fedcourts summarize`; jails, validates and secret-scans the written files; uploads them as the `case-summaries` artifact |
| `publish` | dev App token (`main` only) | opens or updates one reviewed PR from `summaries/refresh` |
| `rejected` | nothing (no environment, `permissions: {}`) | records on the run page that the hold did not release |

**Every run holds**, scheduled or dispatched, as `run-predict`'s rounds do: the
hold is the lane's one human gate before spend, and the plan report states the
case count and an estimated cost range.

**Credential separation.** The corpus credentials and the API key never share a
job, so no step holds both: the plan and stage jobs assume the read-only role,
the generate job holds the key and assumes nothing (its first step fails the
job if any AWS credential or OIDC minting is reachable), and the staged record
crosses between them as a one-day run artifact.
`tests/test_workflow_summarize.py` pins the split.

**The environment's key.** The lane spends on the bound environment's
Anthropic key — prod's on main, staging's on a staging rehearsal — the one the
other Claude lanes use. It does not compete with the cells for throughput:
provider rate limits are per model and the lane's model is outside the
prediction panel, and its plan stands down while a predict or evaluate round
is running (checked at plan time, so a hold released later can overlap a
round, harmlessly). It does share the key's provider spend limit with the
cells, so what bounds a runaway plan is the `review` hold in front of every
run and the per-document cap; [budget.md](budget.md) carries the expected
spend.

**Staged like a cell.** The record a summary reads is the one a forward predict
cell reads — `provision-snapshot`'s latest snapshot and stored documents, with
its contact-detail scrub applied to the staged text — taken without a moment
cut, since a summary describes the newest record.

**Publication.** Before anything leaves the runner, the change set must hold
summary files and nothing else (`fedcourts summary-paths --strict`), `data/`
must validate, and `scan-diff-for-secrets` must pass with the API key as a
known secret; a failure withholds both the artifact and the PR. On `main` the
`publish` job cuts `summaries/refresh` from `main`, carries the open PR's
summaries forward, adds the run's, re-runs the jail, the validator and the scan
over the whole change set, force-pushes and opens or updates the PR. It is
**never auto-merged**: the collect jails do not cover this branch family, so an
auto-merge needs a jail of its own first. `ci.yml`'s `main-base` routing admits
the branch.

The branch is rebuilt from `main` on every run, which shapes how a reviewer
works it. Only summary *additions and modifications* are carried forward: a
summary a reviewer deletes on the branch is owed again and regenerated by the
next run, so a bad summary is fixed by editing it or by closing the PR (a
closed PR's summaries are no longer carried, and every case it held is
re-planned). Each run's force-push also resets review state on the PR. And a
carried file's front matter is trusted as written: someone with write access
who edits a summary's `record_digest` to match the current record marks that
case up to date — a collaborator-only lever whose result is itself reviewed.

**Rehearsal.** A dispatch from `staging` binds the staging environment — its
read-only role, corpus pair and Anthropic key — plans, holds, stages
and generates, and leaves the summaries in the `case-summaries` run artifact.
It opens no PR. The artifact is still public (below), so a rehearsal's
summaries are downloadable for its retention.

## Leakage

**Back-test replay cells cannot read a summary.** A summary of a decided case
states the outcome. `run-backtest` removes `data/cases/` whole before its cells
run, and summaries live under it;
`tests/test_workflow_cell_invariants.py` pins that the summary path stays
inside the removed tree.

**Forward predict and evaluate cells can.** `run-predict` and `run-evaluate`
check out the ledger with summaries in it, and nothing fences them off. That is
a stated residual rather than an oversight. A summary describes the case's
newest record, which can be later than the information set a moment-placed
forward cell is provisioned with (a brief in opposition filed after the
arrival moment, say). But a forward cell may retrieve without restriction —
the live docket carries the same later record — and every summary is
committed to this public repository, so a checkout fence would withhold nothing
a cell could not fetch. The
moment cut bounds what a cell is *handed*, not what it can find. Every
predictor reads the same checkout, so a summary is common input rather than one
engine's advantage.

**The staged record is a public artifact for a day.** The `summary-stage`
artifact carries each planned case's staged record between the stage and
generate jobs: the newest snapshot payload and every stored document's text
(after the contact-detail scrub). This repository is public, so any signed-in
user can download a run artifact while it exists; its retention is the
shortest GitHub offers, one day. It rides the qp-topic extract's footing —
supremecourt.gov content only, since the plan and `summarize` both refuse a
CourtListener REST snapshot ([data-sources.md](data-sources.md)) — and is
wider than the extract in one way: every stored filing of each planned case
rather than one section of each petition. Staging runs after the review hold
and provisions whatever snapshot is newest by then, so the plan's screen alone
would let a REST snapshot stored in between reach the artifact. The stage job
therefore re-applies it to what it actually staged, before the upload and on
the side of the job boundary that holds the corpus credentials
(`summary-stage-check`), as an allowlist: a case crosses only if it was
planned and its tree holds exactly what provisioning writes — the planned day's
snapshot in the Court's own shape, `context.json`, and the documents manifest
with one text file per listed document, each fetched from supremecourt.gov. A
symlink removes the case rather than being followed, and anything else under
the stage root is removed. A removed case is reported skipped and planned again
by the next run.

**The written summaries are a public artifact for a week.** The
`case-summaries` artifact carries the generated files, after the jail and the
scan but before any human review, for seven days — the window a rehearsal's
spot check needs.

## Commands

- `fedcourts summarize-plan [--limit N] [--out plan.json] [--report plan.md]` —
  the dry run: eligible, up-to-date and owed counts, the planned cases, and an
  estimated cost range. Reads the corpus; writes nothing under `data/`; calls no
  model.
- `fedcourts summarize --plan plan.json --staged <root> [--report result.md]
  [--budget-minutes M]` — writes the planned summaries. Past the time budget it
  starts no new case and reports the rest as deferred, so the workflow's step
  returns (at 140 minutes, under its 165-minute cap) and what was written is
  still collected. Exits 1 if the plan held cases and none was written, so a
  dead key reads as a failure rather than an empty success.
- `fedcourts summary-paths --name-status-file <f> [--strict]` — the lane's path
  filter and, with `--strict`, its publish jail.

## Cost

`summarize-plan` over the live content store on 2026-09-23 planned all 195
predicted cases (every one's newest snapshot was the Court's own docket JSON,
so the supremecourt.gov-only rule excluded none), reading a median of 105k characters per case (snapshot plus
documents, each document capped at 100k), the largest 289k. At 2.5 characters
per token that median is ≈42k input tokens, so a summary costs ≈$0.10–0.20 on
Sonnet 5 and the plan priced the backfill at $13–21. The budget carries the
backfill at ≈$20–40, a margin over that estimate — the plan's range assumes
2.5–3.5 characters per token and a typical-to-capped output — until a run's
recorded usage replaces both. At ~4% of records changing a day, steady state is
roughly 5–10 summaries a day, ≈$1–2 a day or ≈$30–60 a month, each run
behind the `review` hold. See [budget.md](budget.md).

## Non-goals

- **Grading summaries.** They are display material; nothing is scored on them.
- **Summaries of earlier snapshots.** Only the newest record is summarized; a
  superseded summary stays as written, dated by its snapshot.
- **Short captions and docket numbers.** Tracked separately with the big-case
  board's `short_caption`; whether this lane should produce one is a question
  for when both exist.
