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
  that depends on which model is added: a prediction run measures about $1.36
  on the claude predictor and $2.64 on the gemini one, and projects to about
  $2.08 on the codex one.

At today's `P = 3` with three evaluators, one fully predicted and evaluated
event is budgeted at roughly **$16**, the basis everything below scales from.
It is the projected cost from 2026-12-01, when gemini's rate doubles: an
event on the current models comes to about $11.20 until then and to about
$15.80 from that date. Those two figures are part
measured and part projected, engine by engine.

- **Claude, measured.** The `claude-fable-5-2` cells on `main` (at
  `f3754248d`, 2026-11-18, every cell from the first on 2026-11-12) come to
  about $1.36 a prediction (41 runs) and $1.38 a grading run (43), at
  $8 / $40 with cache reads at $0.20.
- **Gemini, measured at the introductory rate.** The `gemini-4-carbon` cells
  over the same span come to about $2.64 a prediction and $1.97 a grading run
  (41 each), at $2 / $10 with $0.10 cached. That is about twice what
  `gemini-4-argon` spent on its cells at the same rate ($1.40 and $0.93), so
  Carbon spends more tokens on the same kind of cell. The rate doubles from
  2026-12-01, which at equal tokens, and with the cached rate assumed to
  double too, makes the runs about $5.28 and $3.94. Carbon's rate is the one
  reported at its release, not yet read from an invoice.
- **Codex, projected.** `gpt-6.2-astra` runs from `proc-v24` and has no
  measured cell. It is priced at $8 / $40 with cached input at $0.40, four
  times `gpt-6.1-sol`'s $2 / $10 and $0.10 in every bucket (Astra's rate as
  reported at its release, not yet read from an invoice). The `gpt-6.1-sol`
  cells on `main` at `f3754248d` (266 prediction runs and 83 grading runs
  from 2026-10-20 on) measure about $0.52 and $0.44, and repriced at Astra's
  rates, token for token, about $2.08 and $1.78. The projection holds only if
  Astra spends tokens as Sol did. Most of those cells ran on Codex CLI
  releases before the pinned one, and the pinned CLI gives Astra a
  272,000-token context window against Sol's 500,000, so a long cell compacts
  sooner; either can move its token counts.

One run of each predictor is then about $6.08 and one of each judge about
$5.13, $11.20 an event; from 2026-12-01 they are about $8.72 and $7.10,
$15.80 an event. Those are per run, and an event costs more than one run of
each wherever a cell is retried. None of the 41 events forecast on the
current claude and gemini models was (40 of them by all three predictors), but the 213 events forecast between
2026-10-20 and 2026-11-11 took 683 prediction runs, about 7% above one run a
predictor. The stage moves the figure as well: over the 40 forecast by all three, one
run of each predictor (codex still on Sol) came to about $4.45 on a cert
petition at distribution (13 events) and $6.80 on an argued case (3). Both
samples are small, a week of cells: the grading runs are mostly cert-stage
gradings, which read less than a merits one, and the figures are owed a
re-measure once Astra has cells and the doubled rate is on the ledger.
The evaluator count holds at 3 as `P` grows.
Per-run token usage and cost are recorded on the ledger (`usage.json`, rolled
up by `fedcourts usage-summary`), so the rates can be re-anchored from
measurement rather than assumed. Re-anchoring is a deliberate edit to the pinned
rate table the plans price against, never a drift: the figures move when someone
moves them. That table (`src/fedcourtsai/planning_rates.py`) prices a fully
predicted and evaluated event at about $24.64, above both figures. The review
hold's per-round auto-release reads the table, and a round priced above
`auto_release_usd_per_round` waits for a release, so a row above its engine's
cost errs toward holding and a row below it lets a larger round through. The
rows do not sit evenly against the engines. Its claude-code
rows, $4.27 a prediction and $5.92 a grading run, are set from the
pre-cutover measurements and anchors, about three and four times the measured
cells. Its codex rows, $3.00 and $2.20, are the 90th percentile of the
`gpt-6.1-sol` cells repriced at Astra's rate as above ($2.98 and $2.19),
rounded up. Its gemini rows, $5.30 and $3.95, are Carbon's measured cells
doubled for the rate in force from 2026-12-01 and rounded up, so they hold
across that change and until then price a gemini cell at about twice its
cost.
[milestones.md](milestones.md) prices its plan at the table.

**The plain-language case summaries also spend outside `events × cost per
event`** ([case-summaries.md](case-summaries.md)). It is one non-agentic
call per predicted case (a second when a rejected response is retried) on
Claude Sonnet 5, written only when a case's record
changes, on the environment's Anthropic workspace behind the `review` hold or its
budgeted auto-release.
Measured, from the usage each committed summary records (`main` at
`d7840ec19`): 1,278 summaries across 402 cases since the first on
2026-09-23 cost $199.68 in all, a mean of $0.16 and a median of $0.13 each.
The trailing 30 days hold 733 of them at $137.27 with the one ruling summary, and the trailing 14 days 229
at $41.62, so the lane runs at roughly $90–135 a month, 16 to 24 summaries a
day. That counts toward the model-spend envelope below, and is
bounded by the key's cap whatever a plan owes. The same runs summarize the AI watchlist's
rulings, one call each on the ruling's text alone: a few cents for a short
order, under $0.10 for an opinion at the per-document cap. One ruling summary
is committed so far, at $0.01. The AI-cases feed and the two other weekly
updates are rendered from committed data and call no model, so those summaries
are the feeds' whole model spend.

**The topic labeler spends outside it too** ([qp-topic.md](qp-topic.md)). One
headless Claude Code session labels a batch of up to 1,200 questions-presented
texts, weekly per frame (petitions and applications) behind the `review` hold
or its budgeted auto-release, and standing down on a week with nothing new to
label. Measured basis: a full 1,200-row petitions batch at the default
`claude-opus-5-5` has run at $8.87, $9.00 and $9.09 on the spend record (and
at $10.01 before the record began), an application batch of 668 to 1,068 rows
at $6.12 to $7.48; at `claude-fable-5` two full batches ran at $37.48 and
$60.16. A round is priced before it runs at $0.02 and $0.06 a row
(`fedcourtsai.planning_rates`), against a measured $0.007 to $0.010 at the
default. Every run's spend is recorded under `data/qp-topics/spend/`, a run
refused at the reference gate included: the record's 20 runs, from its first
on 2026-10-30 to 2026-11-11, cost $90.67, of which $61.90 was eight label
batches, $25.98 the ten replicate runs that measure the labeler's
repeatability, and $2.79 the side coder below. Those batches are backlog
work on the two frames. Once a backlog is labeled, a week labels only what
is new or stands down, so the steady state is an estimate, not a measurement: about
$20–40 a month at one part batch a frame a week with no replicate runs, and
about $70 if every week ran a full batch on both. A `claude-fable-5` dispatch
of a full 1,200-row batch prices at $72, just under the $75 per-round cap, so
it too can auto-release.
The same lane runs the merits side coder
([merits-alignment-baseline.md](merits-alignment-baseline.md)) weekly over new
merits grants, priced at a provisional $0.06 a row at the default model. Its first run
coded the backlog of 302 grants for $2.72, about $0.009 a row, and a later
week codes the few new grants (one so far, at $0.08) or stands down.

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
  planning table's predict rows ($4.27 claude-code + $3.00 codex + $5.30
  gemini, $12.57 an event) a case prices at about $25.14, and the dispatch cap
  of 20 cases at about $503. The
  arm has no `review` hold, so the dispatch is the release: the 1–20 case cap,
  which the job's timeout sets, is its only bound.
- **A back-test comparison** (`fedcourts cert-backtest-compare`,
  `fedcourts merits-backtest-compare`) runs one predictor's cell twice on
  each drawn case: two cells a petition at cert and four a case at merits,
  two moments an arm. At the planning table's claude-code predict row ($4.27)
  the cert default of 20 petitions prices at about $171 and the merits
  default of 10 cases at about $171, where both arms run a model that row
  describes; a candidate model the rate table does not carry has no planning
  rate of its own, and that row stands in for it. A `run-backtest` dispatch
  (`replay: cert-compare` or `merits-compare`) caps the draw at those
  defaults and has no `review` hold, so the dispatch is the release.
- **The pilot round** (`run-evaluate`, `mode: reasoning-pilot-merits`) grades
  the briefed moment's kept forecasts for up to 15 cases, one grading run per
  evaluator per event. At the table's evaluate rows ($5.92 + $2.20 + $3.95,
  $12.07 an event) that is about $181. The round is always held for a release
  and never auto-released. It reads every writing of the decision, as every
  evaluate cell does, and the evaluate rows were measured on cert-stage
  gradings that read no opinion and graded no forecast document, so the figure
  reads low.

Together, a 20-case replay and its pilot round (grading 15 of those cases)
come to roughly $685, once. Both rates come from the planning table, not a
measurement, and neither round's cells reach the committed ledger, so
`fedcourts usage-summary` never counts what they spent. What they spent is
measured apart, with the rest of the test and staging spend below. No merits
replay or pilot round is on that record yet; the one cert replay on it, a
single claude-code leg on 2026-11-10, cost $3.17. The back-test's other work,
walking past Terms into the corpus and scoring the deterministic baselines
over them, calls no model: it draws on the CourtListener request budget, not
this one.

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

As of 2026-11-11 the record holds 101 legs, the first from 2026-11-01, at
$26.40 in all: $20.67 the `engine-smoke` legs, $2.30 the `engine-actions-smoke`
legs and their canary, $3.17 the cert replay and $0.26 one labeler smoke;
$22.14 of it on staging keys and $4.25 on production keys. At that pace test
and staging traffic costs about $70–80 a month, most of it the promotion
gate's suites (*Scenario 1*, below).

## Scenario 1: Bootstrapping

The current state. Three predictors (Anthropic, OpenAI, Google), each graded
by three judges, forecast a salience-ranked slice of the paid SCOTUS cert
docket plus every interim and merits event it leads to.

**What is forecast.** Twelve moments are declared and every one is forecast
(`fedcourtsai.pipeline.moments`); each is its own event, with its own frozen
record and its own score:

| Stage | Moment | Event |
|---|---|---|
| Cert | First distribution for conference | `evt-petition-disposition` |
| Cert | Arrival, for the sampled arrival cohort | `evt-petition-arrival-disposition` |
| Cert | Call for a response | `evt-order-call-for-response-disposition` |
| Cert | First relist | `evt-order-relist-disposition` |
| Cert | Call for the views of the Solicitor General | `evt-order-cvsg-disposition` |
| Cert | The Solicitor General's invited brief | `evt-brief-sg-disposition` |
| Interim | Arrival of the application | `evt-motion-disposition` |
| Interim | Response requested | `evt-order-response-requested-disposition` |
| Interim | Response filed | `evt-brief-response-disposition` |
| Merits | Cert grant | `evt-order-judgment` |
| Merits | Briefed | `evt-brief-judgment` |
| Merits | Argued, once the transcript is out | `evt-argument-judgment` |

Which cases reach those moments is the salience gate's choice
([salience.md](salience.md)): up to 12 petitions of a regular conference's
cohort and 24 of the long conference's, less the interim reserve's slots in
use, a 1-in-20 sample of paid petitions at
arrival, and a reserve of five interim applications at a time. The AI-case
watchlist's five district-court moments are forecast beside them, by the
slice's own three predictors and three judges, from the moments' switch-on
day ([trial-stage.md](trial-stage.md)); this scenario's figures do not cost
them. Not forecast: the watchlist's appeal moments and a listed case's
Supreme Court events outside the gate, which are designed and not registered
([appeal-stage.md](appeal-stage.md)), and the late-Term authorship re-forecast
([milestones.md](milestones.md)).

**How many events.** The ledger on `main` (at `d7840ec19`, 2026-11-11) holds
603 forecast events on 401 cases since the first round in July 2026. The
trailing 30 days first forecast 251 of them, 52 in the one-time backlog that
came with the call-for-response moment, and graded 102 as their outcomes
arrived. Outside that backlog, a week from 2026-10-12 on first forecast 34 to
51 events, about
150–220 a month. Held across the nine months from October through June, that
pace comes to roughly 1,400–2,000 events a Term, before the summer's few. The
range is an extrapolation from six weeks, not a count, and its spread is the
choice of weekly pace, not an interval: the first relists (15 of the 17 came
in one week) may be start-up fill, and a full Term on the ledger settles it.

| | Monthly | Yearly |
|---|---:|---:|
| Model API spend | $3,000 | $36,000 |
| Other spend | $600 | $7,200 |
| **Total** | **$3,600** | **$43,200** |

The model line is the **envelope**, not today's run rate. Measured committed
spend over the trailing 30 days, the one total the `spend` backstop and the
auto-release budget read (`main` at `f3754248d`, as of 2026-11-18 15:30Z):

| Lane | Trailing 30 days | Counted in the envelope |
|---|---:|---|
| Predict cells (three predictors) | $808.73 | yes |
| Evaluate cells (three judges) | $296.41 | yes |
| Case and AI-ruling summaries | $122.18 | yes |
| Topic labeler and merits side coder | $103.06 | yes |
| **Measured total** | **$1,330.38** | |
| Integration smokes, promotion gate, replays (recorded 2026-11-01 to 2026-11-11) | $26.40 | no, reported separately |

By engine the cells are $581.14 gemini, $336.72 claude-code and $187.27
codex. Most of the window ran on the engines' previous models: 304 of its 388
claude-code cells are `claude-opus-5-5`, 303 of its 389 gemini cells
`gemini-4-argon`, and every codex cell but four is `gpt-6.1-sol`. So the
total reads well below what the same work costs on the current models. The
window holds none of the long-conference campaign of early October, the
month whose cells came to $2,283. It first forecast 257 events and graded
116.

Projected, not measured, at the per-run figures above. The window's runs
(about 270 predictions and 85 to 115 gradings an engine) at the current
models' cost come to about $2,190 of cells once Astra is live, and with the
window's summaries and labeler runs to about $2,400 a month, inside this line.
From 2026-12-01 gemini's share doubles and the same runs come to about $3,140
of cells and $3,350 in all. The last seven days ran slower (41 events
forecast, 43 graded), and their spend on every lane, with the cells repriced
the same way, comes to about $1,950 a month before that date and $2,850
after; that week holds 10 codex gradings against 43 claude ones, so it reads
low by the missing codex runs. Every figure here rests on a week of cells
whose cost varies widely run to run, and is rounded to the nearest $50. So an
in-Term month projects to roughly $1,950–2,400 until 2026-12-01 and
$2,850–3,350 from it: inside this line until December, and from then on
either side of it and under the `spend` backstop's ceiling. It is inside the
auto-release budget below except near the range's top, where the allowance
for rounds in flight brings routine rounds to the hold. The trailing window reaches those figures
gradually, since each day at the new cost replaces one at the old. A month
above the range's top, a long conference's campaign among them, has every
round wait for a release. Over a Term, 1,400–2,000
events at $11.20–15.80 is ≈$16–32K before retries, and ≈$22–32K at the
figure in force for most of it, against the $36K envelope and before the
summaries and the labeler add their ≈$1.3–2.1K a year at the rates above;
the annual figure sits below twelve in-Term months because the summer
forecasts little. On the projection the envelope holds across the event
count: about $2K to spare at its top once retries are added, and under $1K
once the summaries and the labeler are. Milestone 2's AI-case watchlist
(≈$1–2K, [milestones.md](milestones.md)) fits in that margin except at the
very top of the count.

The limits read the ledger, and the ledger prices each cell's tokens at the
rate table in `src/fedcourtsai/pricing.py` as it stands when the cell is
recorded. Gemini's doubling therefore reaches the measured total only once
that table's gemini rows are edited, which is owed on 2026-12-01; a gemini
cell recorded after that date and before the edit is recorded at half its
bill.

The envelope is also what unattended spend is held to. A predict, evaluate,
case-summary or topic-label round skips the maintainer's release only while
measured spend over the trailing 30 days (the committed `usage.json` ledger,
each committed summary's recorded usage, and each topic-labeler run's spend
record — the same total the `spend` backstop sums), plus an allowance for rounds released in
the last day, plus the round's own estimate, stays within
`auto_release_budget_usd` in `config/review-hold.yaml`, $3,500, set $500
above this monthly figure so a campaign's spend still in the window does not
hold every routine round; past it, every round waits for a human release. A single round
also auto-releases only when its estimate is within
`auto_release_usd_per_round`, $75, which at the planning table is a predict
round of five events. The `spend` backstop
in `config/tracking.yaml` sits above the budget, at $4,000 over the same
30-day window, and stops minting outright
([pipeline.md](pipeline.md), *Auto-release*).

One more unattended spend sits outside that budget: the promotion train's
integration `gate` suite, run on the staging environment's engine keys once
per promotion candidate and dispatched with no review hold. It is bounded on
its own terms — once per candidate head, never re-dispatched by the train,
and at most `max_gate_dispatches_per_day` suites a UTC day
(`config/promotion-train.yaml`, code-owned like the review hold's caps)
([pipeline.md](pipeline.md), *Promotion: staging → main*). Its measured cost
is the report's promotion-gate table (*Test and staging spend, reported
separately*, above), which counts toward no budget either: the eleven
gate runs on record (`promote/2026-11-01` to `promote/2026-11-09`) cost $1.53
to $2.26, a median of $1.86, each a lower bound wherever a leg's record was
lost. At about one promotion a day and about 1.4 paid suites a
promotion ([testing.md](testing.md)) that is roughly $80 a month, and the
per-day cap of two suites holds the worst case near $110.

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
subscription and Codespaces, with a buffer. The interactive and scheduled
development sessions (issue sweeps, effect checks) run on that subscription,
and the back-test's walk of past Terms draws on the CourtListener membership's
request budget, so neither adds a line here. It is a rough estimate from current
bills, not re-measured with the model figures above; the scaling figure allows
for the items expected to grow past bootstrapping. GitHub Actions is $0 on the public repo. Automated runs always
bill pay-per-token to the providers' API accounts — through an API key, or, for
Claude, the federated sign-in to the environment's Anthropic workspace — and the flat development subscription is never used for CI.
