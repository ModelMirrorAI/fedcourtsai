# Budget

A cost forecast; the one figure here that also acts as a limit is the bootstrap
model-API envelope, which bounds unattended spend (*Scenario 1*). Figures are
USD and rough by design: they size the project at two funding levels so scope
can be chosen with the bill in view. What each increment of funding buys, step by step, is in
[milestones.md](milestones.md).

## What drives cost

**Model API spend is the dominant cost and the only one that scales.** Every
prediction and every evaluation is an agentic run — a model reads the case
record, retrieves, and writes its artifacts over many tool-use turns — billed
per token on each provider's on-demand API. Everything else (CourtListener
membership, AWS storage, development tooling) is small by comparison and close
to flat.

Model spend is `events × cost per event`, and two dials set it:

- **`N` — how many events are forecast.** An event is one case at one
  prediction moment (a cert petition at first distribution, an argued case
  after oral argument, and so on). `N` grows by covering more of the docket or
  by adding moments. Cost scales linearly with it.
- **`P` — how many predictors forecast each event.** A judge grades every
  predictor for its event in one run, so a fully covered event is `P + 3` agent
  runs rather than the `P + 3P` a per-(predictor, evaluator) grading would cost:
  adding a predictor buys one more prediction run and makes each of the three
  grading runs a little larger. So `P` raises the cost *per event*, by an amount
  that depends on which model is added: prediction runs spanned roughly $0.58 to
  $3.04 across the three as last measured.

At today's `P = 3` with three evaluators, one fully predicted and evaluated
event costs roughly **$10**. The claude pair's share of that is priced rather
than measured: its cells run Claude Opus 5.5, priced at the token counts the
pair recorded on the Fable tier it replaced — a mean of about $1.38 a
prediction (251 runs) and $1.16 a grading run (118 runs) — on the assumption
that Opus spends the same tokens, which the first round's `fedcourts
usage-summary` measures; the measured Opus figures below are not yet the
basis. The other four figures are
measured means: about $3.04 and $0.58 a prediction and $2.90 and $0.73 a
grading run for codex and gemini, measured on `gpt-6-astra` and
`gemini-3.1-pro-preview`. The codex and gemini engine defaults are
`gpt-6.1-sol` and `gemini-4-argon`, and their first measured cells on
`main` (at `38802b537`, 2026-10-21) are few: 5 predictions and 18 grading
runs each. Codex measures about $0.43 a prediction, in line with the $0.44
that re-pricing its earlier cells at Sol's rate projected, and $0.34 a
grading run, below the projected $0.42. Gemini measures about $1.06 and $0.64 at Argon's introductory
rate ($2 / $10, $0.10 cached), against a projected $0.46 and $0.55: its
predictions read about 2.8 times the uncached input of the earlier model's.
The rate doubles from 2026-12-01, which at equal tokens, and with the cached
rate assumed to double too, adds about $1.70 to gemini's share of an event. On those figures a fully predicted and evaluated
event comes to about $5.00 with the claude pair at its priced figure, and
about $3.75 with it at the first measured Opus 5.5 rounds on the same
commit (54 predictions at about $0.62, 47 grading runs at about $0.65). Both samples are
small. The $10 figure and everything below that scales from it stay on the
measured basis until the rates are re-anchored on the rounds on the new
models.
The evaluator count holds at 3 as `P` grows.
Per-run token usage and cost are recorded on the ledger (`usage.json`, rolled
up by `fedcourts usage-summary`), so the rates can be re-anchored from
measurement rather than assumed. Re-anchoring is a deliberate edit to the pinned
rate table the plans price against, never a drift: the figures move when someone
moves them. That table (`src/fedcourtsai/planning_rates.py`) prices a fully
predicted and evaluated event at about $16.80, well above the measured
figures. Pricing high errs toward holding: the review hold's per-round
auto-release reads the table, and a round priced above
`auto_release_usd_per_round` waits for a release. Its claude-code
and codex rows are set from the pre-cutover measurements and anchors; its gemini rows,
$2.12 a prediction and $1.29 a grading run, are the measured Argon cells
doubled for the rate in force from 2026-12-01, so they hold across that
change. [milestones.md](milestones.md) prices its plan at the table.

**The plain-language case summaries also spend outside `events × cost per
event`** ([case-summaries.md](case-summaries.md)). It is one non-agentic
call per predicted case (a second when a rejected response is retried) on
Claude Sonnet 5, written only when a case's record
changes, on the environment's Anthropic key behind the `review` hold or its
budgeted auto-release.
Measured basis: a median
staged record of ~120k characters (≈50k tokens) puts a summary at
≈$0.10–0.20. The backfill of ~195 predicted cases is ≈$20–40 once; about 4% of
predicted cases' records change on a given day (8 of 185 sampled day-pairs),
so steady state is roughly 5–10 summaries a day, ≈$1–2 a day or ≈$30–60 a
month — inside the model-spend envelope's headroom below, and bounded by the
key's cap whatever a plan owes.

**The topic labeler spends outside it too** ([qp-topic.md](qp-topic.md)). One
headless Claude Code session labels a batch of up to 1,200 questions-presented
texts, weekly per frame (petitions and applications) behind the `review` hold
or its budgeted auto-release, and standing down on a week with nothing new to
label. Measured basis: $10.01 for a full batch at the default
`claude-opus-5-5`, $37.48 and $60.16 at `claude-fable-5`; a round is priced
before it runs at $0.02 and $0.06 a row (`fedcourtsai.planning_rates`). At the
default, both frames weekly come to about $90 a month at the one measured
opus batch, and up to about $210 a month at the planning rate, less once the
frames' backlogs clear and most weeks stand down. A `claude-fable-5` dispatch
of a full 1,200-row batch prices at $72, just under the $75 per-round cap, so
it too can auto-release. Every run's spend is recorded
under `data/qp-topics/spend/`, a run refused at the reference gate included.
The same lane runs the merits side coder
([merits-alignment-baseline.md](merits-alignment-baseline.md)) weekly over new
merits grants, priced at a provisional $0.06 a row at the default model
(three times the topic labeler's, since no side-coding run has been measured):
its first run codes the backlog of about 300 grants, about $18 at that rate,
and a later week codes the few new grants or stands down.

**The merits replay and the grading pilot over it spend outside the ledger
too** ([pipeline.md](pipeline.md), *The predict/evaluate matrix*, for the
replay arm; [outcome-decomposition.md](outcome-decomposition.md), *The pilot,
and what it reports*). Neither writes under `data/`, so the trailing-spend
window the auto-release budget and the `spend` backstop read never sees them:
each is bounded on its own terms instead. (The cells, the case summaries and
the topic labeler's runs are what that window counts.)

- **The replay** (`run-backtest`, `replay: merits`) runs every routable
  predictor on each drawn case at two moments, the grant and the briefed
  moment, so with the three engine predictors a case is two events. At the
  planning table's predict rows ($4.27 claude-code + $1.88 codex + $2.12
  gemini, $8.27 an event) a case prices at about $16.50, and the dispatch cap of 20 cases at about $330. The
  arm has no `review` hold, so the dispatch is the release: the 1–20 case cap,
  which the job's timeout sets, is its only bound.
- **The pilot round** (`run-evaluate`, `mode: reasoning-pilot-merits`) grades
  the briefed moment's kept forecasts for up to 15 cases, one grading run per
  evaluator per event. At the table's evaluate rows ($5.92 + $1.30 + $1.29,
  $8.51 an event) that is about $130. The round is always held for a release
  and never auto-released. It reads every writing of the decision, as every
  evaluate cell does, and the evaluate rows were measured on cert-stage
  gradings that read no opinion and graded no forecast document, so the figure
  reads low.

Together, a 20-case replay and its pilot round (grading 15 of those cases)
come to roughly $460, once. Both rates come from the planning table, not a
measurement, and neither round's cells reach the committed ledger, so
`fedcourts usage-summary` never counts what they spent. What they spent is
measured apart, with the rest of the test and staging spend below.

## Test and staging spend, reported separately

Several lanes spend real tokens and commit nothing to `data/`: the integration
suite's engine legs (`engine-smoke`, `engine-actions-smoke` and its daily boot
canary, `codex-application-repro`, `qp-labeler-smoke`), and so the promotion
gate's `gate` runs; the staging rehearsals of the topic labeler and the case
summaries, whose publication is fenced to `main`; the cert and merits replays
(`run-backtest` on a real engine, its gemini cells excepted: they write no
log in the shared checkout to read, so their share goes unrecorded); and both reasoning-pilot rounds. Each such
leg leaves one priced **off-ledger spend record** (`OffLedgerSpend`), failed
legs included, read from the engine's own log or the cells' `usage.json` by the
parsers `record-usage` uses and priced at the same rate table. The record rides
an `off-ledger-spend-*` run artifact, so no leg holds a write credential, and
the daily `run-ops` job sweeps the artifacts onto the `ops-metrics` branch,
where they outlive the artifacts' retention ([pipeline.md](pipeline.md),
*Operational analytics*).

`fedcourts off-ledger-spend-report` gives the figure: the trailing 7 and 30
days split by environment (`staging` keys or `prod` keys) and by lane, the six
newest months with spend, and each promotion-gate run's cost, every recorded leg
of every attempt summed. A leg whose record was lost (a runner that died before
its recording step, a failed upload) is missing from that sum, so a gate figure
is a lower bound. `run-ops` appends it to its run summary daily.

**It is reported separately and counted nowhere.** Test traffic must never hold
back a production round, so these records never
join the total the `spend` backstop and the auto-release budget read; nothing
that gates spend reads the `ops-metrics` branch. The lanes keep the bounds
named beside each of them on this page instead. Records start with the first
legs that run the recording steps, so the report has no history before then.

## Scenario 1: Bootstrapping

The current state. Three predictors (Anthropic, OpenAI, Google) forecast a
salience-ranked slice of the paid SCOTUS cert docket plus every interim and
merits event it leads to — on the order of 850–1,100 events a Term.

| | Monthly | Yearly |
|---|---:|---:|
| Model API spend | $2,000 | $24,000 |
| Other spend | $600 | $7,200 |
| **Total** | **$2,600** | **$31,200** |

The model line is the **envelope**, not today's run rate: 850–1,100 events at
about $10 is ≈$8.5–11K, and the headroom above it carries the moments milestone 1
adds and milestone 2's AI-case watchlist ([milestones.md](milestones.md)).

The envelope is also what unattended spend is held to. A predict, evaluate,
case-summary or topic-label round skips the maintainer's release only while
measured spend over the trailing 30 days (the committed `usage.json` ledger,
each committed summary's recorded usage, and each topic-labeler run's spend
record — the same total the `spend` backstop sums), plus an allowance for rounds released in
the last day, plus the round's own estimate, stays within
`auto_release_budget_usd` in `config/review-hold.yaml`, set $500 above this
monthly figure so a campaign's spend still in the window does not hold every
routine round; past it, every round waits for a human release. The `spend` backstop
in `config/tracking.yaml` sits above the budget and stops minting outright
([pipeline.md](pipeline.md), *Auto-release*).

One more unattended spend sits outside that budget: the promotion train's
integration `gate` suite, estimated at about $8 of the staging environment's
engine keys per promotion candidate, dispatched with no review hold. It is
bounded on its own terms — once per candidate head, never re-dispatched by the
train, and at most `max_gate_dispatches_per_day` suites a UTC day
(`config/promotion-train.yaml`, code-owned like the review hold's caps) — so at
the measured cadence of about one promotion a day the estimate runs to roughly
$250 a month ([pipeline.md](pipeline.md), *Promotion: staging → main*). Each
gate run's measured cost is the report's promotion-gate table (*Test and
staging spend, reported separately*, above), which is where to read this figure
once gate runs are on record, and which counts toward no budget either.

## Scenario 2: Scaling

The funded target. Every paid SCOTUS petition is forecast at every prediction
moment, by seven model developers' predictors plus prompt-lens variants — the
end state of the six milestones in [milestones.md](milestones.md), both
lower-court slices included.

| | Monthly | Yearly |
|---|---:|---:|
| Model API spend | $10,000 | $120,000 |
| Other spend | $2,300 | $27,600 |
| **Total** | **$12,300** | **$147,600** |

**Other spend** in both scenarios covers the CourtListener API membership, AWS
(S3 corpus storage and egress), and development costs such as the Claude Code
subscription and Codespaces, with a buffer. It is a rough estimate from current
bills; the scaling figure allows for the items expected to grow past
bootstrapping. GitHub Actions is $0 on the public repo. Automated runs always
bill to provider API keys — the flat development subscription is never used
for CI.
