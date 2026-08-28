# Budget

A cost forecast, not a spending cap: it sizes each driver so scope and cadence
can be chosen with the bill in view. Prices are USD, a mid-2026 snapshot
(re-check the linked sources before committing spend); the repo is **public**, so
figures assume the free public-repo Actions tier, and all inference is priced on
the **on-demand API**. For how the phases work, see
[data-pipeline.md](data-pipeline.md) and [pipeline.md](pipeline.md).

## The shape: a fixed floor plus one dominant scaling line

Every non-inference line — runners, storage, memberships, subscriptions — sums to
a near-constant **≈$5.5K/yr floor**. Agentic model usage for prediction and
evaluation is one to two orders of magnitude larger and scales linearly with how
many events, by how many predictors, scored by how many evaluators. So the budget
is that fixed floor plus one dominant line, and that line has **two dials**:

- **`N` — the salience gate's capacity**, the number of petitions per conference
  the tournament actually runs ([salience.md](salience.md)). `N` sets **how many
  events** are forecast.
- **`P` — the size of the predictor registry**
  ([config/predictors.yaml](../config/predictors.yaml)), the number of engines
  that forecast each event. `P` sets **what one event costs**.

The third count is deliberately *not* a dial. The evaluator registry size **`E`
holds at 3**: a new predictor is not a judge by default, because promoting an
engine to judge changes the graded process rather than the budget, and is a
separately-registered process-version decision
([process-version.md](process-version.md)). So the whole budget re-cuts as
`fixed floor + events(N) × per-case(P)`.

**The phase policy: one dial at a time.** Bootstrapping holds `P = 3` and spends
every incremental dollar on `N`. Depth before breadth — a fourth opinion on an
event the gate never selected is worth less than a first opinion on one it did,
and the coverage claims the project is judged on are claims about `N`. That
holds until `N` has nothing left to buy: **full paid-gate coverage**, the state
in which every paid petition the gate can reach is rank-filled.

Two figures name that state and they are not the same one. `N`'s **own** ceiling
is the first-distribution slice it fills — at most `1,498 × $15 ≈ $22K/yr`. The
**whole-Term bill** in that state is larger, because four channels ride beside
`N` rather than inside it: **≈$28K/yr inference, ≈$33K with the floor** (derived
under *What `N` can ever buy*). Both are upper bounds, since 1,498 is itself an
upper bound on the pool. Past that state raising `N` buys nothing — the gate can
never select more than those petitions — and **incremental dollars switch to
`P`**, which buys another engine's read of each event instead of more events.
Everything below prices one dial or the other.

The flat **Claude Max** subscription cannot absorb automated volume — it is
metered for interactive use, and per Anthropic's policy the subscription token is
meant for Claude Code / claude.ai, not CI/CD. So it covers interactive
development, while every automated stage (`run:predict`, `run:evaluate`)
authenticates to Claude via the Anthropic **API key**.

## What there is to predict: measured volumes

Per October Term. The cert and merits lines are the OT2017–2024 **paid**
census, where every row carries `sample_weight` 1: the paid stream is walked
denial-complete, so these are counts rather than reweighted estimates, and the
committed `metrics/statpack.json` carries those Terms unweighted
(`weighted_resolved == resolved` on every paid row — the property that says
"census", where the walk-frontier `complete` flag only says the serials were
covered). The IFP stream genuinely is still sampled, which is why the
IFP-inclusive figure below is an estimate and these are not. The interim line is **one**
application Term, OT2025, still open — a Term-to-date count.

| Bucket | Per Term | What it is |
|---|---:|---|
| Cert — paid modern-cert petitions | 1,498 | at most the pool the gate selects from (11,987 rows over eight Terms) |
| Merits — cert grants opening a proceeding | 65 | paid `granted`, excluding the `gvr` label, which disposes of a petition without opening a proceeding |
| Interim — substantive applications | 179 | 13.1% of OT2025-to-date's 1,365 parsed application dockets; 82.6% are extensions and 4.2% unreadable asks. An open Term over an accumulating cohort — recompute from the statpack's `interim` section rather than quoting these |

**A case is forecast more than once.** Each stage asks one question and the case
passes several points at which it can honestly be forecast, each with a
different information set. The moments are separate events, separately scored
and never pooled ([salience.md](salience.md)); each costs one fully-tournamented
case-equivalent.

| Stage | Moment | Events / Term | Coverage of the stage |
|---|---|---:|---|
| cert | first distribution | 495–522 | measured at `per_conference_capacity: 12` by the OT2022–24 gate replay **under sal-v1** — a lower bound for the active sal-v3 gate, whose federal carve-in also reaches conference cohorts (≈16.5/Term more under the active caption-v2 rule — the caption-v1 census measured ~14, caption-v2 adds ≈2.5; unmeasured until a caption-banded replay refresh): rank fill 398–413 (cumulative through resolution; 380–386 at first distribution) plus uncapped carve-outs 97–115 (below) |
| cert | CVSG | 20 | 1.33% of paid petitions — but 7.0% of the paid census's grants |
| cert | arrival | 98 | the sal-v3 arrival cohort, **beside** `N`, filling forward from the registration-fixed cohort start (the OT2026 docket-year roll — the standing pending backlog never enters): 75 from the 1-in-20 deterministic random slice over ~1,500 paid arrivals (`salience.arrival_sample_rate`) + ~23 from the federal-petitioner carve-in under `caption-v2`, whose census run passed statistical verification (8/8 complete Terms at 9.1–17.7× lift; per-Term 11–41, so a heavy government-litigation Term runs high; the caption-v1 cut carved ~20, with caption-v2 adding ≈2.5/Term — `docs/salience.md`) |
| interim | arrival | 67 | 5 reserve slots turning over at a 27.1-day mean occupancy |
| interim | response requested | 10 | 15.1% of the 67 selected arrivals — 27 of OT2025's 179 substantive applications |
| interim | response filed | 21 | 30.6% of the 67 selected arrivals, the rate measured over the 219-substantive population the moment was declared against (a different 67: 67 of those 219 drew a filed response); the response-filed timestamp is published in no artifact, so this one rate cannot be refreshed from the pack |
| merits | grant | 65 | **every** granted petition — the gate is bypassed at this stage |
| merits | briefed | 62 | 96.4% of the 65 grants reach a respondent merits brief, rounded down |
| | **total** | **838–865** | **≈$12.6–13.0K/Term** at the $15 planning rate, arrival slice + carve-in included (≈$13.2K at the bound if the federal carve-in's conference-cohort reach adds its full ~14) |

The later moments differ sharply in how much runway they leave, which is the
figure to read before trusting any of their skill numbers: a merits brief
precedes the judgment by a median 159 days (minimum 44), a requested interim
response by a median 17 (minimum 3), and a *filed* interim response by a median
of only 2 — so a material share of that last moment's cells will classify
retrospective on commit latency alone. The two interim horizons come from the
same declaration-time 219-substantive measurement as the filed rate above, and
rest on corpus-only fields no artifact republishes.

The interim rows carry two selection biases, in opposite directions. The
reserve's ladder orders on response-requested first, so the selected 67 are
enriched in exactly the property the 15.1% rates — read the 10 as biased low
for the selected slice, bounded above by the 67. Two populations answer that
rate and they differ: 15.1% is OT2025's, while the whole accumulated
substantive slice the interim estimator pools over runs about a fifth (52 of
249), which is the figure [salience.md](salience.md) quotes. And the 67 itself
divides slot turnover by the stream's 27.1-day mean occupancy, while the ladder
plausibly favors longer-lived applications (p95 110 days), which would cut
arrivals below 67.

Two denominators are easy to confuse. The **≈5,500** the gate is priced on below
counts cert decisions across both fee streams; the gate excludes IFP at Tier 0
([salience.md](salience.md)), so the pool it can ever select from is at most the
**1,498** paid petitions — an upper bound, because seven further rules in
`OUT_OF_SCOPE_RULES` cut it again, as does the snapshot-aware bare-import rule
that `out_of_scope_reason_full` adds. So the ≈$83K below is the whole-docket
ceiling, and rank-filling every paid petition once costs
`1,498 × 6 cells × $2.50 ≈ $22K`. That last figure is the **first-distribution
slice** — the most the capacity dial can ever buy — not the cost of the state it
describes: CVSG, arrival, interim and merits moments ride beside it and carry the
whole-Term bill to ≈$28K (*What `N` can ever buy*, below).

**The cap is sized to bind, and the gate replay at the shipped capacity
measures that it does.** Raw paid cohorts run a median 34 petitions (p90 82,
max 369); the pool the replay ranks — replay-reconstructable resolved paid
petitions, 1,239–1,358 a Term — runs a mean conference cohort of ~37, and at
`per_conference_capacity: 12` the cap binds **29 of each Term's 33–36
reconstructable first-distribution cohorts** across OT2022–24
(`metrics/salience-replay.json`). The comparison that sized it: a
`per_conference_capacity` of 150 would cut just **8 of 251** raw
cohorts and exclude 5.3% of petitions — selecting **~95%** of the paid docket
and funding ~$24K/Term, a ranking rather than a spend control. The shipped
`12` (long conference `24`) measures at **495–522 selected petitions a Term**
across OT2022–24: rank fill 380–386 at first distribution and 398–413
cumulative through resolution, plus floor/CVSG carve-outs of 97–115 riding
*above* `N` uncapped — landing the escalation program at ≈$11.1–11.5K at the planning
rate (≈$12.6–13.0K with the sal-v3 arrival cohort — the moments
table below). (The replay runs with no reserve occupancy; the interim reserve's slots
in use would lower the rank fill, below.) The measured coverage trade: the
selection carries **0.76–0.81** of the Term's replay-reconstructable
grant-family outcomes (grant denominators 90/108/91 for OT2022/23/24, GVRs and
summary reversals included), resting mostly on the uncapped carve-out band.
Of those grants, 4/6/3 a Term sit on blind rows — no reconstructable selection
moment, so no gate could select them — leaving selectable denominators of
86/102/88: recall of the *selectable* outcomes is 0.80–0.84, and 0.944–0.967
is the achievable ceiling at any capacity. The prior committed replay — run at
the then-shipped 150/200 caps over this same pool, so capacity is the only
delta between the two — measured exactly that ceiling: a cap of 150 selects
everything selectable and buys no coverage the blind rows do not already deny.

**A re-queue is not a re-run.** A selected cert petition re-queues on a
distribution transition outside the same-day cooldown
(`salience.relist_requeue_cooldown_days`), and petitions are distributed a raw
mean of 1.46 times each. But `predict_matrix` drops any `(predictor, event)` cell
whose predictor already committed a prediction for that event, and does so at
plan time, before any agent cell is minted. So a relist costs runner minutes,
provisioning, and poll quota — not inference. The one gap is concurrency: the
drop reads the checked-out ledger rather than taking a lock, so two runs planned
before either's collect PR merges both see an unpredicted event and both mint.
Re-forecasting a changed posture is available as a deliberate change
(`skip_predicted=False`); its multiplier is above 1.46, because the funded
population is the relist-selected slice rather than the docket-wide mean.

**The interim reserve bounds concurrency, and is sized to trade inside `N`
rather than add spend.** Substantive applications resolve in a *mean* of 27.1
days (median 13, p95 110) — the same declaration-time 219-substantive
measurement as the moment horizons above, over corpus-only fields no artifact
republishes — so OT2025-to-date's 179 arrivals need ≈13 concurrent slots
against
`interim_reserve_slots: 5` — the reserve is continuously full, and the predicted
interim slice is therefore a ladder-ordered subsample of the substantive stream
rather than the stream itself.

The reserve's slots are *defined* inside `N`: `_select_cohort` fills to
`capacity` minus the slots in use, so the subtraction costs a cert pick
wherever a conference's *eligible* non-carve-out remainder exceeds the reduced
limit. At `per_conference_capacity: 12` a full reserve leaves a rank fill of
7 — far below the ~37–38-petition mean replay-reconstructable cohort — so a full
reserve would displace a cert pick at essentially every capacity-bound
conference, as the design intends; the displacement *frequency* itself is
unmeasured, because the gate replay runs with no reserve occupancy.

That makes the reserve a materially larger share of a small `N` than of a large
one, and worth revisiting alongside it: at 12 it claims about 40% of the
rank-fill limit. Lowering `N` further without lowering the reserve would zero
the cert rank fill entirely — at `N ≤ 5` only the always-include carve-outs
would be funded.

Two things bound the interim figures. Lifespans run from each docket's first
entry to its disposing entry rather than from the `date_filed` /
`date_decided` columns, which are null on a substantial minority of the rows
and null disproportionately on the long-lived ones. An entry-based lifespan
exists only for a *resolved* application, so the measure covered 218 of the
219 rows it was taken over, the exception being the one then still pending.
The same rule against today's pack would reach 243 of the accumulated 249 (178
of OT2025-to-date's own 179) — a property of the population, not a denominator
the figures above were recomputed on. And OT2025 is open, so the arrival count is a partial year
divided into a full-year denominator — saturation is understated, not
overstated.

## Cost drivers

### 1. Model usage (the dominant cost)

Three engines run the agentic stages, routed per registry entry
([config/predictors.yaml](../config/predictors.yaml),
[config/evaluators.yaml](../config/evaluators.yaml)):

| Engine | Used by | Billing | Rate (per 1M tokens) |
|--------|---------|---------|----------------------|
| Claude Code (`claude-fable-5`) | `claude-baseline`, `claude-judge` (predict/evaluate default) | Anthropic API (workflows); Max subscription for interactive local dev | Subscription: $200/mo flat (Max 20x — dev only, in floor #5). API: $10 in / $50 out |
| Codex (`gpt-5.6-sol`) | `codex-baseline`, `codex-judge` | OpenAI API (pay-per-token) | $5 in / $30 out |
| Gemini (`gemini-3.1-pro-preview`) | `gemini-baseline`, `gemini-judge` | Gemini API (pay-per-token) | $2 in / $12 out (≤200k context; steps up beyond) |

Sources: [Claude Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan),
[Claude API pricing](https://platform.claude.com/docs/en/pricing),
[OpenAI API pricing](https://developers.openai.com/api/docs/pricing),
[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

**Per-run cost.** A predict or evaluate run is *agentic* — the agent reads the
prompt, AGENTS.md, the case snapshot, and retrieved priors, then writes its
artifacts over several tool-use turns — so effective token usage (≈280–400K
input, the large majority cache-served, plus ≈6K output) far exceeds the visible
artifacts. Every run records its tokens and estimated cost (rates kept in
`fedcourtsai.pricing`) to a `usage.json`, rolled up by `fedcourts usage-summary` —
**≈$1,395 total inference spend on the ledger to date**, across the 684 cells the
per-cell figures below draw on (636 predict, 48 evaluate).
That estimate is token-derived, so hosted web search — billed per call rather
than per token on all three APIs — sits outside it and makes a searching cell's
recorded cost a mild undercount. The ledger also counts **collected cells only**:
a cell's `usage.json` reaches `data/` on its run's collect PR, so a stranded
run — one whose cells burned tokens but whose output never landed — spends
against the provider bill and never appears here. Every measured figure below is
therefore a floor on provider-side spend, not a reconciliation of it.
Measured per-cell cost spans **≈$0.25–8.30 by model mix** (blended mean
**≈$2.04** over the 684 cells on the ledger).

**Per-cell cost is keyed on the stage.** The first predict fan-out to land after
the pre-registration freeze instant ([process-version.md](process-version.md)) —
run `20260816T111104Z`, 81 cells over 27 events — is the first measurement that
covers the arrival, interim, and merits moments rather than cert alone, and the
stages do not cost the same:

| Predict stage (moment) | Events | `claude-baseline` | `codex-baseline` | `gemini-baseline` | Per event |
|---|---:|---:|---:|---:|---:|
| cert — first distribution | 3 | $3.90 | $2.17 | $0.59 | $6.66 |
| cert — arrival | 12 | $3.85 | $1.88 | $0.58 | $6.30 |
| interim | 1 | $3.18 | $1.72 | $0.59 | $5.49 |
| merits | 11 | $4.93 | $1.82 | $0.73 | $7.47 |
| **whole run** | **27** | **$4.27** | **$1.88** | **$0.64** | **$6.79** |

(Per-event figures sum the unrounded per-engine means, so a row can differ from
its displayed columns by a cent. The merits row pools two moments the volumes
table lists separately — `evt-order-judgment`, 9 events at $7.35, and
`evt-brief-judgment`, 2 at $8.02.) Read the row `n`s before the dollars. Only
one ordering here is a finding: **merits runs ≈$1.2 an event above the cert
arrival moment**, on 11 events against 12. The other three stages are *not*
separated at these `n` — cert first distribution (3 events) and cert arrival
(12) are within noise of each other, and the interim row is **a single event**
at $5.49, which sits inside the per-event range of the cert arrival stage
($4.66–$8.94) *and* inside that of merits ($5.45–$10.77), the most expensive
stage. A single draw that is consistent with every other stage ranks nothing.
Take interim as a placeholder to be re-read at the next fan-out, not as the
cheapest stage — and the wider post-freeze population below now reads it at
**$6.41 over 12 events**, so it is *not* the cheap stage this single draw
suggested. That wider read leaves the row's one finding standing but narrows it:
merits still runs above cert, $7.60 against $6.71, by ≈$0.9 rather than ≈$1.2.

The larger-sample reference is the pre-freeze cert-era ledger — **410 predict
cells over 137 events** (an incomplete grid: 138 / 132 / 140 cells by engine,
132 events carrying all three) at claude-baseline ≈$3.65, codex ≈$1.38, gemini
≈$0.55, a per-event **$5.57** — every one of them the cert **first-distribution**
moment.

The gap between that $5.57 and the run's $6.79 is **half decomposable**. The
**mix** half is measured: the arrival moment ($6.30) and, dominantly, the merits
moment ($7.47) enter a population the pre-freeze ledger measures as
first-distribution only. The **level** half is *not* measured. At the same
moment the run's three events average $6.66, ≈+20% — but they are $5.86, $6.64
and $7.49 individually, every one inside the pre-freeze per-event range
($2.98–$10.04, mean $5.61, SD $1.25 over the 132 complete events), and drawing
three pre-freeze events at random clears $6.66 about 7% of the time. The two
cohorts also straddle a process boundary: all 410 pre-freeze cells predate
process stamping, while all 81 run cells carry the blessed `proc-v3` digest, and
that digest is defined over the prompt bytes and resolved config
([process-version.md](process-version.md)) — the very inputs that set token
count. Treat **≈+20% as an upper bound on any level effect**, not a measurement
of one. Plan against $6.79 and expect it to move.

**The wider post-freeze predict population corroborates `$6.79`, but only once
it is mix-matched.** Further fan-outs and top-up runs have landed, and pooling them raw does not
settle anything: across all post-freeze predict cells the **complete-grid**
population is 75 events at **`$7.01`** an event — but that population is ~45%
cert, ~16% interim and ~39% merits, against a Term the volumes table puts at
~73% cert, ~12% interim and ~15% merits. It is dominated by the most expensive
stage. Reweighting its own per-stage rates by the Term's event mix is the
comparison that means something:

```
complete-grid post-freeze predict, by stage   cert    $6.71  (n=34)
                                              interim $6.41  (n=12)
                                              merits  $7.60  (n=29)

reweighted by the Term's mix (613-640 cert / 98 interim / 127 merits)
                                              ≈ $6.80-6.81 an event
```

Read the raw `$7.01` as what a *merits-heavy* run costs, not as a Term rate — and
note that the same objection lands on `$6.79` itself, which is the raw mean of a
run that was 11/27 merits. Reweighted the same way, that run reads `$6.44`. The
planning anchor is a run mean, not a Term rate; what the reconstruction supplies
is the Term rate to check it against.

**And the check is not independent.** Twenty-seven of those 75 events *are* the
anchor fan-out — about a third of the population. Over the 48 events it does not
contain, the same reweighting gives:

```
non-anchor complete-grid post-freeze   cert    $6.97  (n=19)
                                       interim $6.50  (n=11)
                                       merits  $7.68  (n=18)
reweighted by the Term's mix                   ≈ $7.02 an event
```

So the honest reading is **corroboration of the magnitude, not of the point**:
independently of the anchor, a Term reweights to `$7.02`, some **3% above**
`$6.79`. That direction matters below — it eats what little headroom the planning
rate has rather than adding to it.

The evaluate side is measured on a **narrower and weaker** base, and its cohorts
do not pool — they split the same way the predict cells do:

| Evaluate cohort | Events | `claude-judge` | `codex-judge` | `gemini-judge` | Per event |
|---|---:|---:|---:|---:|---:|
| `proc-v2` stamped, pre-freeze (run `20260814T033644Z`) | 3 | $4.86 | $1.07 | $0.79 | $6.71 |
| unstamped, pre-freeze (run `20260718T000134Z`) | 1 | $4.16 | $0.92 | $0.52 | $5.60 |
| pre-freeze pooled | 4 | $4.68 | $1.03 | $0.72 | $6.43 |
| `proc-v3` stamped, post-freeze (run `20260824T231401Z`) | 6 | $4.16 | $1.51 | $0.77 | $6.44 |
| `proc-v3` stamped, post-freeze (run `20260825T024608Z`) | 6 | $4.79 | $1.22 | $0.68 | $6.69 |

The four pre-freeze events are all cert-stage, so that anchor is stage-narrow
whichever row is read; pooling across the process boundary is the same defect the
predict side is careful to avoid, and the single month-older unstamped event
pulls the pre-freeze pooled figure down ≈4%. **$6.71 is the better-matched
pre-freeze anchor and $6.43 the more cautious one**, which is why the per-case
figure below is a band rather than a point.

**The two post-freeze rows are one six-event population read twice**, not twelve
events: both runs graded the same six moments (two interim dockets × three
interim moments each), so the second adds no coverage. It is not a re-grading
either: neither run's judges could see the other's output, since each collected
before or independently of the other. They are two **independent first gradings**
of one population — which makes the `$6.44`/`$6.69` spread a clean ≈4%
run-to-run variance under one process, the only such measurement the ledger
holds.
Two passes over the same six events, so grading them actually cost `$13.13` an
event of *coverage* — not the steady state a per-case rate models, but not a
number to lose either.

Two defects and a supersession qualify these rows. **n = 6**, on two application
dockets. **One stage**: all six moments are interim, against a Term whose
forecast events run ~73–74% cert and only ~11–12% interim. And the digests —
105 of their 108 `evaluation.json` records carry `proc-v3`'s evaluator digests
(the three exceptions sit on one partial cell), so these gradings are
attributable but for three records — and attributable to a **grading process
since superseded**. `proc-v4` retired those evaluator digests over a batch of
judge-prompt changes, of which the token-count-relevant one is the
judge-workspace prune: it hides the committed `predictions/` and `evaluations/`
trees from a judge cell's working tree. A hidden tree is a tree not read. **The
first `proc-v4` grading run will re-price these cells**, in a direction the
prune's mechanics suggest is downward — which is a prediction, not a reading.

What the rows do **not** establish is the tempting reading. They are **not**
evidence that the assumed ≈+22% uplift failed to appear, because the pre-freeze
anchors they would be compared against (`$6.43`, `$6.71`) are **cert-stage**, and
no pre-freeze interim-stage evaluate measurement exists at all. What can be said
is narrower: the first post-freeze evaluate measurement comes in **below** what
the uplift assumption projects, at a stage the pre-freeze anchor does not cover —
so it bounds nothing until a cert-stage post-freeze grading exists. It is a
signal to check, not a correction to apply. That is why the figures below carry a
**measured-basis** reading beside the planning-rate one rather than replacing it.

**The ledger's $2.04 is its mix, not the design's**:
636 of the 684 cells are predict, and evaluate cells cost more, so the mean the
funding knob has to cover is the one at the design mix of three predict and
three evaluate cells per case — **$2.44–2.49** ($14.6–15.0 ÷ 6, the derivation
under *Capacity `N`* below). Read $2.04 as what has been spent per cell so far
and $2.44–2.49 as what a fully-tournamented case implies. The cheapest cells
approach ≈$0.25 only when the
byte-stable prefix (AGENTS.md + prompt template + schema) is served from the prompt
cache — automatic on all three engines, billing cached reads at ≈0.1×, and the
reason to keep that prefix stable. Budget the range, not the point: the quantity
the planning rate has to cover is the *design-mix mean*, and it is set at the
top of that mean's band ($2.50 a cell against $2.44–2.49) — not above the top of
the per-cell *range*, which no cell budget could be.

**One agentic surface sits outside the registry**, and outside the per-cell
accounting above: `run-analytics`'s `qp-topic-label` mode, which runs a single
Claude Code session over one extract of stored questions-presented texts rather
than one cell per case. It is a manual dispatch, not a scheduled or
cascade-triggered job, so it spends only when a maintainer asks for a labeling
run; its model is the dispatch's `label_model` input, defaulting to the cheapest
Claude tier because the task is classification against a fixed sixteen-label
vocabulary rather than forecasting. It writes no `usage.json` — the ledger is
keyed by cell, and a labeling run is not one — so its spend does not appear in
the totals above and has to be read off the run's own engine log until a
labeler-shaped accounting exists.

Its three model choices price like the engines above:

| Labeler model | Role | Rate (per 1M tokens) |
|---------------|------|----------------------|
| Haiku 4.5 | the `label_model` default | $1 in / $5 out |
| `claude-sonnet-4-6` | the step-up for a labeling pass the default reads poorly | $3 in / $15 out |
| `claude-fable-5` | the predict/evaluate engine, available here for a like-for-like read | $10 in / $50 out |

Same source as the engine table
([Claude API pricing](https://platform.claude.com/docs/en/pricing)), carried in
the repository as `fedcourtsai.pricing.MODEL_RATES` — the table `usage-summary`
prices every cell from, so a labeling run and a predict cell are quoted off one
set of rates. The Haiku row is the one that does not key straight into it: the
dispatch offers a **dated** Haiku 4.5 id, while the rate table holds the
undated `claude-haiku-4-5`. The rate is the same and nothing prices a labeling
run automatically today (it writes no `usage.json`), but the two spellings have
to be reconciled before one ever does.

**What one labeling run costs.** Bounded rather than measured: the extract is
capped at the labeling ceiling `fedcourts qp-corpus` enforces (1,200 rows —
`fedcourtsai.pipeline.qp_topics.LABEL_ROW_CEILING`, derived from the labeler
*step's* 40-minute cap, not from the population), so the ceiling is what a run
can cost at most. Profile of the scoped extract, measured against the dev blob
pulled 2026-08-27 whose newest stored snapshot is 2026-07-13: 1,187 rows, mean
1,088 characters, median 942, p90 ≈1,920, capped at 4,000. That snapshot stamp
is the one that bounds the figure — QP presence is a document-fetch artifact —
and the blob's stored documents predate the corpus split, so it undercounts
what the writer lane holds. Note the headroom: 1,187 against a 1,200 ceiling is
thirteen rows, so on this blob the guard is close to firing and on the writer
lane it is expected to fire.

A ceiling-sized run is therefore ≈1.3 MB of question text ≈ **0.33M input
tokens read once** (at ~4 characters a token). What it bills is a multiple of
that, and the multiple is the soft part of the estimate: the session re-sends
context across the prompt's ~120 turns, so a labeler that streams slices and
does not retain them runs a few times the once-read figure, while one that
accumulates the whole transcript runs an order of magnitude above it. Output is
roughly 0.1–0.2M — one JSONL line per row plus the turn's own prose. Across
that whole span, and with cache reads billing at a tenth of the input rate
(cache *writes* at 1.25×), the default model lands in **single-digit dollars**;
`claude-sonnet-4-6` is 3× the rate and `claude-fable-5` 10×, which puts the top
of the range in tens of dollars. Quote the tier, not a point figure. For this
mode the artifact, not the money, is what a mis-sized dispatch loses. All of it
is **unmeasured** — no `qp-topic-label` dispatch has produced an artifact yet,
so these come from the extract profile and the prompt's own turn budget rather
than from an engine log, and the first completed run replaces them.

**Scope: the SCOTUS-docket gate.** The pilot predicts and evaluates only SCOTUS
dockets. Ingestion is unchanged — the channels still assemble all fourteen courts
deterministically (≈$0 model spend) so the full history stays queryable for
retrieval and back-testing; only the agentic stages are gated.

The unit throughout is the **agent cell**, and both roles fan out the same way:
one predict cell per (predictor, event) and one evaluate cell per (evaluator,
event) — a judge grades *every* predictor for its event in a single invocation,
so cross-evaluation multiplies the `evaluation.json` count but not the cell
count. A case therefore costs **`P + E` cells, not `P × E`**, and at the shipped
`P = E = 3` that is **6 cells per case**, not 12.

That identity is the seam between the two dials, and the two halves of it grow
differently. Raising `P` adds predict *cells* — one more per event, priced at
that engine's own rate. It adds no evaluate cell, because `E` is fixed; it makes
each existing evaluate cell **larger**, since every judge now reads one more
prediction. Cell count is linear in `P`; evaluate cell *size* is the part that
is not measured, and *Registry size `P`* below bounds it.

Full 14-court scope is the reference ceiling, held at `P = E = 3`:

```
predictions  ≈ 48,000 events   × 3 predictors (P) × $2.50   ≈ $360K
evaluations  ≈ 42,000 resolved × 3 evaluators (E) × $2.50   ≈ $315K
                                                              ────────
full scope                                                    ≈ $675K / yr
```

At any other `P` the whole block re-cuts on `per-case(P)` rather than on the
`$2.50` design-mix cell rate. And it prices a scope change that is **deferred**
— see *Deferred scope, unpriced* — so read it as a reference ceiling, not a plan.

The SCOTUS gate is roughly 1/8 of that — ≈5,500 cert decisions per term:

```
predict   ≈ 5,500 × 3 (P) × $2.50   ≈ $41K
evaluate  ≈ 5,500 × 3 (E) × $2.50   ≈ $41K
                                     ───────
full cert gate                       ≈ $83K / yr
```

That is the whole-docket ceiling, both fee streams. The gate never selects an
IFP petition, so the pool it can rank-fill is the 1,498 paid petitions:
`1,498 × ≈$15 ≈ $22K / yr` (see *What there is to predict: measured volumes*).
Read that as the **first-distribution slice**, not as the cost of the state it
describes — the CVSG, arrival, interim and merits moments ride beside it and
carry the whole-Term bill to ≈$28K (*What `N` can ever buy*, below).

**Capacity `N`: the funding knob.** `N` is the depth dial, and within the gate
[salience.md](salience.md)'s
capacity `N` bounds *how many* — the tournament runs on the top-`N` salient
petitions per conference plus a few always-include carve-outs, so inference spend
is `events(N) × per-case(P)`. One fully-tournamented case at the shipped
`P = E = 3`:

```
PLANNING BASIS — the Term-wide rate the pipeline is funded on
  predict:   P = 3 cells, measured over the first post-freeze
             fan-out (27 events, merits-heavy)            =  $6.79
  evaluate:  E = 3 cells, scaled assumption               ≈  $7.84-8.18
                                                             ───────────
  per case                                                ≈ $14.6-15.0
  per case ≈ $15   (the planning rate, three engines cross-evaluated)

MEASURED BASIS — one matched population, six interim events
  predict:   those six events' own predict cells          =  $6.76
  evaluate:  those six events' own evaluate cells         =  $6.44 / $6.69
                                                             ───────────
  per case (matched)                                      ≈ $13.20 / $13.45
```

**The two bases answer different questions, and neither is a substitute for the
other.** The planning basis prices *a Term*: an all-stage predict figure plus an
evaluate half the ledger cannot yet supply, so the gap is filled by assumption.
The measured basis prices *six interim events*: every cell in it is measured, on
the same events, at the same registry size, under one process label — but it is one
stage, `n = 6`, and its evaluate half ran under a superseded grading process.

- The **planning basis** assumes the evaluate half **scales by the whole predict
  move** (`$5.57 → $6.79`, ≈+22%): `$6.43 × 1.218 ≈ $7.84` on the pooled
  pre-freeze anchor, `$6.71 × 1.218 ≈ $8.18` on the better-matched proc-v2 one.
  That is where `$15` comes from, and `$15` remains **the stated planning rate**
  — it is what the ceilings above, the scenario table below, and the plan seams'
  per-cell rates are all priced on.
- The **measured basis** is the only fully-measured per-case figure the ledger
  contains. It is *not* a cross-stage sum: the `$6.76` predict half is those same
  six events' own predict cells, not the Term-wide `$6.79`. That is what makes it
  a measurement rather than an assembly — and also what confines it to the
  interim stage.

So the pair does not bracket a Term rate; one prices a Term on an assumption, the
other prices a corner of it on evidence. Where they are shown side by side below,
the measured column answers "what would a Term cost if it were interim moments
all the way down" — which it is not.

Note what the +22% contains: it is the whole predict move, and only its mix half
is measured. Applying it assumes evaluate's stage mix broadens as predict's has
*and* that whatever level effect sits in the residual applies to judging too.
Both remain assumptions; the interim-stage measurement above bears on neither,
since the anchor it would be differenced against does not cover that stage.

The +22% is also **two differently-built means**. `$5.57` sums per-engine means
over an *incomplete* 410-cell grid (138 / 132 / 140 cells by engine); `$6.79` is
a *complete*-grid per-event mean. Matched to the complete grid, the pre-freeze
figure is `$5.65` over 132 events and the move is **+20%**, not +22%. The `$15`
rate keeps the +22% factor — it is the one the plan seams transcribe — but the
factor is ~2 points generous, which is a small offset against the `$7.02`
independent predict reading pulling the other way.

Three numbers to hold apart. **$13.20–13.45** is the matched measured basis, over
six interim events. **$14.6–15.0** is the Term expectation once the scaling is
applied, the band running from the pooled anchor to the proc-v2 one. **$15** is
the planning rate. Divided across the design mix of six cells, `$15` is the
**$2.50 per-cell rate** the whole-docket ceilings above are priced on.

So: fund against `$15`, and do not treat any of the gaps as headroom.

Against the *assumed* evaluate half on the `$6.79` anchor, `$15` clears the band
by ~2.5% at the pooled reading and effectively nil (~0.2%) at the
better-matched one. Swap in the **independent** predict reading — `$7.02`, the
48 events the anchor does not contain — and the band becomes `$14.86–15.20`:
`$15` sits **inside** it, ~1.3% short at the top. That is the reading to plan
against, because it is the one no anchor-selection can flatter.

Against the matched interim measurement `$15` carries **≈11–14%**. That is not a
third reading of one quantity — it is a Term rate held against one stage's
measured cost, and interim is ~11–12% of the Term.

Two gaps pointing opposite ways, neither settled: the wider predict population
says the rate may be slightly low, the interim gradings say the evaluate half may
be high. Hold `$15`, and read both as reasons to want the cert-stage `proc-v4`
grading run rather than as slack to spend.

**The re-anchor trigger is half met.** It asks for a post-freeze evaluate
measurement, and one exists — stamped, attributable, and below the projection.
Two things still block the re-anchor. It covers **one stage**, and the stage it
covers is not the one the Term is mostly made of. And it ran under evaluator
digests `proc-v4` has **superseded**, on a prompt change that bears directly on
judge token count. **The re-anchor waits on a `proc-v4` evaluate fan-out reaching
the cert stage**; that run, not a fuller ledger, is what settles it.

Which is also why the measured basis rides beside the planning rate rather than
replacing it. The plan seams' per-cell rate table is a transcription of these
figures and its per-event sums are pinned by test, so re-anchoring is a code
change that re-prices every plan — deliberately visible, deliberately not
something a document can do on its own.

So `N ≈ inference_budget / (≈$15 per fully-tournamented case)`. Tier-1 salience
scoring is itself ≈$0 (a deterministic pure function of corpus features, no model
call), so the gate spends nothing to *decide* what the tournament runs on. Raising
`N` deepens the salience-ranked slice; it never reshuffles the ranking.

**What `N` can ever buy.** That `≈$22K` is `N`'s own ceiling — the
first-distribution slice it rank-fills — and so the phase policy's switch point.
The *whole-Term* bill in that state is larger, because four channels ride beside
`N` rather than inside it: CVSG re-forecasts, the arrival slice, the
reserve-bounded interim stream, and the merits stage, whose volume the Court
sets.

```
cert-stage  1,498 first distribution + 20 CVSG + 98 arrival  = 1,616 events
other            98 interim + 127 merits                     =   225 events
                                                               ───────────
                                                               1,841 events

cert-stage  1,616 × $15          ≈ $24.2K / yr  (N's own slice within it ≈ $22K)
whole Term  1,841 × $14.6-15.0   ≈ $27-28K / yr   planning basis
            1,841 × $13.20-13.45   ≈ $24-25K / yr   measured (interim, n=6)
plus the ≈$5.5K floor            ≈ $33K / yr all-in  ( ≈$30K measured, interim )
```

**Every figure in that block is an upper bound.** 1,498 is itself an upper bound
on the pool — `OUT_OF_SCOPE_RULES` and the snapshot-aware bare-import rule cut it
further (*What there is to predict: measured volumes*) — so the state costs at
most this, over at most 1,841 events. One thing can carry it past the bound:
deliberate re-forecasting (`skip_predicted=False`), whose multiplier on the
relist-selected population runs above the docket-wide 1.46 (*A re-queue is not a
re-run*). The bound holds for the shipped default, where a relist costs runner
minutes rather than inference.

The four beside-`N` channels are held at their measured sizes, since none is set
by `N`. One of them is a spend step in its own right, and one can never be:

- **`interim_reserve_slots` is the cheapest step at the switch point.** The
  reserve is set to `5` against the ≈13 concurrent slots OT2025-to-date's arrival
  rate implies, so raising it to 13 scales the whole interim slice:
  `98 × (13/5 − 1) ≈ +157 events ≈ +$2.4K/yr` at the planning rate (≈$2.1K on
  the measured basis). That is **cheaper than the cheapest `P` step below** at
  the `m`-at-ceiling corner those steps are costed on (≈$5.3–6.2K a year for an
  ablation-class engine); at `m` = 0 a cheap fourth predictor would undercut it,
  which is one more reason `m` is the figure worth measuring. It is also where
  the interim stream stops being a ladder-ordered subsample of the substantive
  stream and becomes the stream. The step belongs *at* the switch point rather
  than before it because the reserve is defined inside `N`: while `N` binds,
  every added slot costs a cert pick.
- **`salience.arrival_sample_rate` is not a dial at all.** The 1-in-20 draw runs
  under a registration-fixed key and is effectively frozen once the cohort runs;
  moving it declares a new pre-registered population rather than widening an
  existing one ([salience.md](salience.md)). Money cannot buy arrival coverage.
- The merits stage is the Court's own volume, and CVSG is a rate on the paid
  pool — neither answers to funding.

**Registry size `P`: the breadth dial.** Past that switch point the money goes to
`P`, and `P` prices differently from
`N`. `N` multiplies a **fixed** per-case rate; `P` changes the rate itself:

```
per-case(P)  =  Σ over the registry of predict_i     (P cells, one per registry entry)
             +  Σ over the judges  of evaluate_j(P)  (E = 3 cells, each growing with P)
```

Both halves are sums, and the asymmetry is in what `P` does to each: it adds a
term to the first sum and enlarges every term of the second.

**The predict half is a sum over the registry, not a multiple of an average.**
The per-provider table below measures the three engines at `$4.27` /
`$1.88` / `$0.64` an event — a **6.7× spread** (6.9× on the wider complete-grid
post-freeze population, `$0.64–4.40`, so the figures below understate the top
corner slightly), so *which* engine is added matters more than *that* one is. A fourth predictor adds its own line to that
sum, and — if it is a new engine rather than an ablation variant of one already
there — its own row to the engine rate table under driver #1. Nothing else in
the predict half moves.

**Which is also how the plan seams price it, and the two ways they can be
wrong.** `predict-plan` and `evaluate-plan` cost a matrix from a per-(seam,
engine) rate table drawn from the tables above. The table is keyed on the
resolved **engine**, not on the predictor id, and that cuts both ways:

- A predictor on a **new engine** prices at the `$2.50` design-mix fallback —
  and the plan says so rather than hiding it, counting those cells in
  `cells_at_fallback_rate` and carrying a caveat that names the fallback. A
  flagged approximation.
- An **ablation variant** of an engine already in the registry prices at its
  *parent's* rate, and is **not** flagged — the engine key matches, so nothing
  in the plan marks it. But an ablation varies exactly the inputs that set token
  count (prompt bytes, retrieval surface, resolved config), so its true rate is
  the one thing the parent's rate cannot be relied on for. An unmarked
  approximation on the dimension the ablation exists to change.

So a `P = 4` step on a new engine costs a visibly approximate plan, and one on an
ablation costs an invisibly approximate one. Neither is settled until a fan-out
measures the new entry: for a new engine that is a new row in the rate table, and
for an ablation it is a rate an engine-keyed table has nowhere to put.

**The evaluate half grows by an unmeasured margin `m`.** `E` holds at 3, so the
cell count does not move — each judge instead grades one more prediction in the
same invocation. Call `m` the per-case evaluate growth per added predictor,
summed across the three judges. It is **unmeasured, and not measurable from this
ledger** — not because evaluate is unmeasured (48 evaluate cells now sit on the
ledger, 36 of them post-freeze) but because **every one of them ran at `P = 3`**.
`m` is a difference between two registry sizes, and the ledger holds exactly one.

What can be said is the bound. A judge's fixed costs — the prompt, the snapshot,
the case record it reads once — are shared across every prediction it grades, so
`m` should sit below a proportional share; the **fully-linear case** (evaluate
cost proportional to `P`) bounds it above, on each basis:

```
m  ≤  evaluate(3) / 3

  planning basis   $7.84 / 3  ≈  $2.61      measured basis   $6.44 / 3  ≈  $2.15
                   $8.18 / 3  ≈  $2.73                       $6.69 / 3  ≈  $2.23

  0 ≤ m ≤ ≈$2.6-2.7  (planning)             0 ≤ m ≤ ≈$2.15-2.23  (measured)
```

Neither ceiling is a measurement of `m`. The planning one rests on the assumed
+22% uplift; the measured one rests on six interim-stage gradings under a
superseded evaluator digest. Both
inherit everything the evaluate-half rule above says, and re-anchoring that
figure re-cuts `m`'s ceiling with it.

So the `P = 4` step, built on the same two anchors as the `$15` planning rate:

```
                      planning basis (Term)           measured basis (interim)
predict half   $6.79 + p₄                      $6.76 + p₄
               p₄ ∈ $0.64-4.27  (registry spread, both bases)
evaluate half  $7.84-8.18 + m                  $6.44-6.69 + m
               m ∈ $0-2.73                     m ∈ $0-2.23
                ─────────────                   ─────────────
per case(4)    ≈ $15.3-22.0                    ≈ $13.8-20.0
```

A fourth predictor therefore costs **$0.6–7.0 a case** on the planning basis
(`p₄ + m` at the two corners) and **$0.6–6.5** on the measured one — a range wide
enough, either way, that the class of engine added is a budget decision rather
than a rounding one. Annualized at full paid-gate coverage (1,841 events, itself
an upper bound):

| `P` | per-case(`P`) | Full coverage, inference / yr |
|---:|---|---|
| **3** (shipped) | $14.6–15.0 planning · $13.20–13.45 measured (interim, n=6) | ≈$27–28K · ≈$24–25K |
| 4 | $15.3–22.0 · $13.8–20.0 | ≈$28–40K · ≈$26–37K |
| 5 | $15.9–29.0 · $14.5–26.5 | ≈$29–53K · ≈$27–49K |

(Each row takes the corners of the block above `P − 3` times over: the low end
adds the cheapest engine with `m` at zero to the low base — `$14.63` planning,
`$13.20` measured — and the high end adds the dearest engine with `m` at its
ceiling to the high base, `$14.97` / `$13.45`. The annual column multiplies by
1,841 events.)

Read each band's top as a worst-corner bound, not a forecast: it stacks the
dearest engine on the fully-linear `m`, two worst cases at once. But note what it
is a bound *over* — `$4.27` is the dearest **currently-priced** class, not a
ceiling on what a cell can cost: a new frontier engine could price above it, and
hosted web search is billed per call and sits outside the token estimate
entirely, so a search-heavy predictor exceeds any of these figures. Read the
bottom as a bound too — the cheapest engine with `m` at zero, which cannot be
right either. And read the linear bound as an assumption about *shape*: a judge
reading a fourth prediction lengthens its context, and nothing measured here
rules out that pricing superlinearly rather than sublinearly.

**The first `P = 4` fan-out is the re-anchor point** for `m`, the same discipline
the evaluate half already carries: `m` is settled by differencing that run's
evaluate cells against a `P = 3` evaluate measurement on the same stage mix, and
until that pair exists the bands above are arithmetic rather than estimates.
Nothing here should be extrapolated far past `P = 5`.

**Which predictors to add, in value-per-dollar order.** The criterion is not
diversity of opinion — it is **causal attribution**: how much of what the
registry learns from a new entry can be attributed to a named cause, per dollar
spent. A held-constant control buys attribution; a differently-trained model
buys a second opinion whose difference is unattributable to anything. On that
criterion the cheapest class ranks first, which is convenient but not the reason:

1. **Ablation variants of engines already in the registry** — the same engine
   with a changed prompt, config, or retrieval surface. Cheapest to add (no new
   provider account, an existing measured `predict_i` for its parent) and the
   only class where a difference in score is attributable to a named factor,
   because everything except the ablated one is held constant by construction.
   The process digest moves with the prompt bytes and resolved config, so the
   variant partitions from its parent rather than pooling with it
   ([process-version.md](process-version.md)). Note what an ablation is *not*:
   it is the **least** independent addition the registry can take — a variant of
   an engine already in it — so it widens attribution, not coverage. That it
   yields the most per dollar is a design expectation about where the registry's
   open questions sit, not a measured return.
2. **Open-weight models, Bedrock-hosted** — a family the current registry cannot
   reach on the credit stack it runs on. AWS Activate is the runner-up credit
   program in [milestones.md](milestones.md), and its credits apply to AWS
   services — so Bedrock-hosted inference converts a credit line the Anthropic /
   OpenAI / Google registry has no way to spend. Their per-token rates are
   **unmeasured here**; the registry sum takes a new open-weight entry at the
   bottom of the measured spread until a fan-out prices it.
3. **Additional frontier providers** — the dearest line in the registry sum, and
   the one whose forecasts the design expects to overlap most with what three
   frontier engines already produce (an expectation, not a measured correlation
   — the board's agreement figures are inter-*evaluator*, and no inter-predictor
   agreement number exists, [metrics/README.md](../metrics/README.md)). Worth
   adding, last.

**Only the first class is a registry edit.** `engine` is a closed enumeration —
`claude-code`, `codex`, `gemini` — mirrored into the exported predictor schema,
so classes 2 and 3 are **code changes, not config ones**: a fourth engine needs
an entry in the enum, a default model in the pricing table, a retrieval-surface
entry in the process-version registry (indexed rather than looked up, so a new
engine fails loudly until it is declared), a runner, and its own workflow steps.
An ablation variant needs none of that — a registry entry and a prompt. That
adapter cost is real and it is not in any dollar figure above; it reinforces the
ordering rather than qualifying it.

**`E` stays at 3 through all of this** — the policy is stated in *The shape: a
fixed floor plus one dominant scaling line* above. A new predictor being cheap to grade is not an argument for making it a
judge, and no step on the `P` dial moves `E`.

**The interim docket: a quota'd stream, capped at five cases in flight.**
[salience.md](salience.md)'s interim-docket section carries a second selection
problem — stays, injunctions, vacaturs pending certiorari — and the quota is what
keeps it small. Across the 1,365 parsed application dockets of the still-open
OT2025 Term, **82.6%** are
time-extension requests and **4.2%** carry an ask the parser cannot read; both
are filtered out deterministically by
`interim_signals.is_predictable_application` (≈$0, no model call), leaving the
**13.1%** substantive slice as the only population ever predicted (an open Term
over an accumulating cohort — recompute from the statpack's `interim` section
rather than quoting these). The stream is
budgeted as a **bounded reserve defined inside the per-conference spend
envelope**: `salience.interim_reserve_slots` in
[config/tracking.yaml](../config/tracking.yaml), set to `5` and enforced by the
selection pass — the reserve's slots in use shrink the rank fill in the pass's
latest conference cohort (carve-outs above `N` are untouched). At
`per_conference_capacity: 12` a full reserve leaves a rank fill of 7 — far
below the ~37–38-petition mean replay-reconstructable cohort — so a slot in use
displaces a cert pick rather than adding spend at essentially every
capacity-bound conference, as designed; the displacement frequency itself is
unmeasured, because the gate replay runs with no reserve occupancy. Where it
bites, it bites prospectively, pass by pass: sticky already-latched picks are
never de-selected and the pre-scoring fail-open window rides outside the
quota for one cycle,
so a conference's realized count can transiently drift above `N` — the same
bounded drift the carve-outs already produce (see
[salience.md](salience.md)). A selected application occupies its slot until
it resolves, so the reserve's firm effect is the one on *concurrency*: at most
five interim cells are ever in flight, against the ≈13 substantive applications
live at any moment on OT2025-to-date's arrival rate — a floor, since the Term
is open. An unfilled reserve costs nothing. The slice is
predicted, and its base rate is registered and wired — pooled over application
Terms strictly before the case's own, above its own per-pool floor
([salience.md](salience.md)).

**The merits docket: a second cell on a case already funded, unbounded by
design.** A cert grant opens a merits event
([decision-model.md](decision-model.md)), and that event is forecastable, so a
granted docket buys one more predict cell per predictor and one more evaluate
cell when the judgment lands — roughly a second `≈$15` case-equivalent where
the gate funded the cert cell, and slightly more than that: the merits predict
stage measures `$7.47` an event (n=11) against the `$6.79` run mean the planning
rate is built on — the one stage the run separates from the others. At the
projected ~80% grant coverage that second equivalent is
about four merits cases in five; the other ~13 of the 65 open on dockets the
gate never cert-funded, a first case-equivalent rather than a second. (This
~80% stays a projection: the replay's measured 0.76–0.81 is grant-*family*
recall, and GVRs and summary reversals open no merits cell, so the
merits-opening rate is a different denominator the replay does not report.) Unlike
the interim stream this carries **no reserve and no quota**: nothing in the
selection pass bounds merits cells. That
is deliberate rather than overlooked, and it rests on the population being
self-limiting — the Court grants on the order of sixty cases a Term, each cell
is minted once and occupies nothing until its judgment lands, and the grant is
the outcome the whole cert tournament is ranked on, so declining to forecast it
would be the odd choice. The per-run cell cap and the ex-post spend gate below
still hold the fan-out, and if the grant cohort ever stops being self-limiting
the honest fix is a reserve of its own, not a wider cap.

**The controls, and the one that reads the bill.** Capacity `N`, the per-run cell
cap (`predict.max_predict_cells_per_run`), the live cycle's sweep cap, and the
per-cell attempt caps are all **ex ante** — each bounds one decision or one run,
and none of them knows what has been spent. They therefore compose into a per-run
limit with no per-period limit above it: across the day's scheduled windows, spend
is bounded only by how many cells happen to be owed, which is exactly the quantity
that becomes large at a long conference. The `spend` section of
[`config/tracking.yaml`](../config/tracking.yaml) is the bound above them — a
trailing-window ceiling on **measured** cost, read from the committed `usage.json`
ledger by both plan seams before either mints a matrix. Reaching it **defers**:
the predict queue and the evaluate backlog are untouched and re-derive next cycle.

The shipped value is **$2,500 over a 30-day trailing window** — ~1.7× the
Term's average month (≈$1.40–1.45K: the 838–865 events/Term at the $15
planning rate, spread over the ~9 months the Term spans; on a 12-month spread
the multiple is ~2.3×, so the claim is conservative). What it protects against
is chiefly a **burst**, and the margin against a sustained *rate* is thin. The
shipped steady state cannot reach the ceiling: the mean month sits at ≈$1.4K
and the heaviest month's build-up below at ≈$2.0K. A **regression to a
non-binding cap can**: it burns $2.0–2.7K per 30 days (the prior 150/200
replay selected 1,228–1,349/Term ≈ $18.4–20.2K, and the 150-cap scenario above
funds ≈$24K/Term), a trailing sum whose upper end asymptotes *above* the
ceiling rather than below it. Deferring there is defensible — a non-binding cap
*is* a mis-set capacity knob, which is exactly what the backstop is for — but
it does mean the ceiling is not purely a burst detector at this planning rate,
and `ceiling_usd` is worth re-sizing at the next re-anchor. What a mis-set
capacity knob does *fast* is mint whole cohorts in single runs: one unbound
long-conference cohort is 148–193 replay-weighted petitions (raw cohorts reach
369) × 3 predict cells ≈ **$1.1–2.8K in a day**, against a measured legitimate
peak day of ≈$400 — so the backstop fires within days of a runaway burst.
The heaviest legitimate month clears, with limited room: the capped
component is deliberately flattened to ≈ the mean month (the `C` = 60 build-up
below, ≈$900), the **uncapped** carve-out band adds $230–290 in a typical month
(unbounded by construction — the one channel that can legitimately run hot),
the steady interim/merits stream ≈$370, and the one-time merits backlog drain
is small — a dry-run over the committed corpus finds **31 mintable grants**
(≈$230–460 with their briefed moments; the un-adjudicated population behind
that measurement is 674 grant-opening rows, which is why the sweep is bounded
rather than trusted) — totalling ≈$1.75–2.0K, which leaves ≈$0.5–0.75K of
window for the lagging ledger.
Two limits it is set *with* rather than against. A ceiling of `0` disables
the backstop (the code default, so a missing section can never wedge the
pipeline — a cost control that wedges when misconfigured is worse than none).
And the ledger **lags** — a cell's `usage.json` reaches `data/`
only when its run's collect PR merges — so the figure it compares is a *floor* on
spend inside the window, never a live balance.
Two consequences of a breach belong beside the value. Deferral never destroys
queued work, but it can destroy a **claim**: a forward cert cell deferred past
its petition's resolution is permanently outside the headline strata —
refused outright at provisioning where the record already shows the
resolution, re-minted as a retrospective cell where only the clock does, and
excluded from every scored stratum in the mis-provisioned case whose record
still claims forward ([`metrics/README.md`](../metrics/README.md)) — a genuine breach trades forward coverage, which is why the
ceiling sits above every legitimate month rather than at the envelope's
average. And the ceiling reads **all** measured spend, replay and backtest
campaigns included — money is money by design — so a large iteration campaign
inside one window can itself defer forward cells; time such campaigns away
from conference-dense weeks.

**Monthly spend by provider.** The per-case cost splits across the three API
bills — one predict cell and one evaluate cell per provider per case — so at a
cadence of `C` tournamented cases per month each provider's bill is its per-case
line × `C`:

| Provider (engine) | Predict $/case | Evaluate $/case | $/case | Share | At `C` = 60/mo |
|-------------------|---------------:|----------------:|-------:|------:|---------------:|
| Anthropic (`claude-fable-5`) | $4.27 | $5.70 | $9.97 | ≈68% | ≈$600 |
| OpenAI (`gpt-5.6-sol`) | $1.88 | $1.25 | $3.13 | ≈21% | ≈$188 |
| Google (`gemini-3.1-pro-preview`) | $0.64 | $0.88 | $1.52 | ≈10% | ≈$91 |
| **Total** | **$6.79** | **$7.84** | **≈$14.6** | | **≈$0.9K** |

(As in the stage table, totals sum the unrounded means, so a column can differ
from its displayed entries by a cent. The evaluate column uses the **pooled**
`$6.43` anchor — the cautious one; on the proc-v2 anchor every evaluate entry
rises ≈4%.)

**This table is the predict half's registry sum, written out.** Its predict
column *is* `Σ predict_i` at `P = 3`, and the **6.7× spread** between $4.27 and
$0.64 is why *Registry size `P`* treats a fourth predictor's class rather than
its existence as the budget question. Raising `P` adds a row here — a new
provider bill if the engine is a new provider's, or a second line on an existing
one for an ablation variant — though an ablation's parent rate is exactly what
its own cells cannot be trusted to cost. The evaluate column does **not** gain a
row when `P` rises (`E` holds at 3); each of its three entries grows by that
engine's share of `m` instead, which is the part no measurement covers at any
registry size.

**The two columns are not the same kind of number.** The predict column is
measured over the 27 events of the first post-freeze fan-out — 27 cells per
engine, all four stages — and is corroborated at `$6.80–6.81` once the wider
post-freeze population is reweighted to the Term's stage mix; the
410-cell pre-freeze cert-era ledger behind $5.57 remains the larger-sample cert
reference. The evaluate column is **projected, not measured**: it is the pooled
four pre-freeze cert-stage graded events with the **aggregate** ≈+22% applied
flat to each engine.

That flat application is the weakest thing in the table, and both the predict
data and the post-freeze evaluate rows say which way it is wrong. Engine by
engine the predict move was strongly non-uniform — claude **+17%**, codex
**+36%**, gemini **+17%** — so scaling the evaluate split by one aggregate factor
**over-weights Anthropic and under-weights OpenAI**. Matching each engine to its
own predict move instead gives claude-judge $5.48, codex-judge $1.40,
gemini-judge $0.85, and shares of ≈67% / ≈22% / ≈10%. The two post-freeze
evaluate runs, averaged, measure **claude-judge $4.47, codex-judge $1.37,
gemini-judge $0.72** — same direction, larger gap: combined with the predict
column that is a split of ≈**66% / ≈24% / ≈10%** against the table's ≈68 / ≈21 /
≈10. So the measured interim rows put the split **≈3 points off the table's on
each of the two large providers** — Anthropic over-weighted, OpenAI
under-weighted, in the direction the predict data already indicated — while
**Google's ≈10% is stable across all three constructions**, which is the more
useful fact about it. Read that as an offset, not an error: those figures rest on
six interim gradings under a superseded digest, and combine an all-stage predict
column with an interim-only evaluate one. The flat factor is kept because it is the one the `$15`
planning rate is built from. Roughly
**roughly seven dollars in ten go to Anthropic** on the table's own projected
split, nearer two in three on the interim-measured one — size that provider's
spend limit on the larger figure, which is the conservative one, and expect a limit
breach there to cost a third of a run's coverage
(the other engines are billed independently). The `C` = 60 column is a
reference month built from the caps — the long-conference cycle at its
24-petition cap plus three regular conferences at the 12 cap (24 + 3 × 12 =
60; `C` counts cases per month) — roughly a *mean* Term month, not a peak. At
the $15 planning rate that capped component is ≈60 × $15 ≈ **$900** (≈$790–810
on the measured basis); the floor/CVSG carve-outs ride above
the caps and add on the order
of $230–290/month at the planning rate in relist-heavy months. The caps make
the capped component insensitive to the one cohort whose realized size is not
yet observed — the long conference's summer backlog — though the carve-out
channel carries no such bound; both together sit inside the ≈$12.6–13.0K
bootstrapping inference envelope.

### 2. CourtListener API (membership for pull throughput)

Historical loading walks the supremecourt.gov docket JSON — $0, no rate limit.
Pull spends the rate-limited REST budget; the free default (5/min · 50/hr ·
125/day, ≈40 dockets/day) is raised by a paid Free Law Project membership
([free.law/membership](https://free.law/membership/)):

| Tier | Price | Limits (min / hr / day) | ≈ dockets/day |
|------|-------|--------------------------|---------------|
| Free | $0 | 5 / 50 / 125 | ≈40 |
| Tier 2 | $25/mo ($250/yr) | 15 / 150 / 600 | ≈200 |
| Tier 3 | $50/mo ($500/yr) | 20 / 250 / 1,000 | ≈330 |
| Tier 4 | $100/mo ($1,000/yr) | 25 / 300 / 1,400 | ≈460 |

The pilot holds **Tier 4 ($1,000/yr)**: the four daily pull windows (≈120
targeted refreshes/day, ≈360 requests) commit about a quarter of the
1,400/day ceiling, leaving ≈1,000 requests/day of standing headroom for
opinion enrichment and one-off backfills — at Tier 2 the same windows would
commit ≈360 of 600, making enrichment and backfills compete with the
rotation. The membership raises the ceiling — the
client still throttles to whatever `FEDCOURTS_COURTLISTENER_RPM` / `_RPH` /
`_RPD` are set to, so the tier change is live only once those variables match
the held tier.

> **Line item: $1,000/yr** (Tier 4 annual).

### 3. GitHub Actions & Codespaces

The repo is public, so standard 2-core GitHub-hosted runners — where every
`run:*` stage and its agent execute — are **free and unlimited**
([Actions pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)).
Actions turns non-zero only if a job is pinned to a **larger runner** (4-core+
bills per-minute even on a public repo) or the repo is flipped back to private.
Codespaces is development-only:
[120 free core-hours/mo](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
(Free) / 180 (Pro), then $0.18/hr (2-core) + $0.07/GB-mo storage.

> **Line item: ≈$0/mo Actions; $0–50/mo Codespaces (dev).**

### 4. S3 corpus storage

The raw-fact corpus (a payload-free index plus a per-case content store) lives in
a private S3 bucket ([S3 Standard, us-east-1](https://aws.amazon.com/s3/pricing/):
$0.023/GB-mo storage; egress free for the first 100 GB/mo account-wide, then
$0.09/GB). GitHub-hosted runners are Azure-hosted, so every byte a workflow reads
out of the bucket is S3 internet egress. Storage (≈10–100 GB) is ≈$0.25–2.50/mo;
predict/evaluate cells make ranged point queries (≈10–50 MB and a few hundred
GETs each), so the dominant term is the **recurring full pulls** by the
scan-shaped writers and analytics — ≈250–300 blob pulls/mo, which at today's
≈1 GB blob is ≈250–300 GB/mo, just over the free tier ⇒ ≈$15/mo, scaling
linearly with the blob (≈$230/mo at a 10 GB blob, where the lever is moving those
consumers to ranged/incremental reads).

> **Line item: ≈$15/mo at today's ≈1 GB blob; ≈$230/mo at a 10 GB blob.**

### 5. Misc fixed costs — the non-scaling floor

A flat **$350/mo** bucket for the individual-use items carried as one line: the
domains (`modelmirror.ai`, `fedcourts.ai`), the email provider, the **Claude Max
dev subscription** ($200/mo, interactive dev only, never automation — see driver
#1), and other small fixed items. A deliberate buffer over the actual items; its
defining property is that it **does not scale** with events, corpus size, or
predictor count.

> **Line item: $350/mo flat** (a fixed floor, not a variable).

## Deferred scope, unpriced

Two expansions are named here so they are not read as omissions. Both are
deliberately carried **without figures**, and neither is on the `N`-then-`P`
path above.

**Widening past the SCOTUS-docket gate.** Predicting the originating courts of
appeals, or a rotating appeals sample, is the ~1-year scope decision in
[milestones.md](milestones.md) — held open until a Term of cost and calibration
data is in hand, alongside the academic / B2B / public-artifact fork. The
14-court reference ceiling under driver #1 sizes that decision's extreme at
`P = E = 3`; nothing between today's gate and that extreme is planned or costed.
Under the phase policy the `P` dial is spent out **before** a scope widening is
considered at all — breadth of forecast comes before breadth of docket. A scope
change is also not a pure budget question: cross-court figures are not
comparable, so widening buys events at the cost of a pooled population
([salience.md](salience.md)).

**Free Law Project's partnership-gated services.** Three ingestion upgrades wait
on an established relationship with Free Law Project rather than on engineering
([milestones.md](milestones.md); *The planned end-state* in
[data-pipeline.md](data-pipeline.md)): a hosted Postgres **replica** under FLP's
replication agreement, docket-alert **webhooks**, and **opinion bodies served
from the replica**. They stay **qualitative and unpriced, pending Free Law
Project's terms** — the only CourtListener figures in this document are the
public membership tiers under driver #2, and the pilot's funded line stays
Tier 4.

Two of the three are also not cost-justified at the current scope, which is the
substantive reason they are deferred rather than merely unpriced. The
**replica** buys full field coverage, replication-lag currency, and freedom from
request caps — but the live channel polls supremecourt.gov without rate limits
and already owns the freshness budget at $0, and Tier 4 leaves ≈1,000
requests/day of standing headroom, so at SCOTUS-gated scope it would be paying
to relieve a constraint that does not bind. **Webhooks** replace polling for
liveness, which matters mainly once the gate widens past the one court whose own
site the live channel already polls. The third — **opinion bodies from the
replica** — would retire the content store's opinion-text path, so its case is a
storage and read-path one rather than a coverage one, and it moves with the
replica. All three become live questions at the scope decision, not before.

## Summary: scaling `N`, then `P`

The non-inference lines — misc floor ($350/mo), CourtListener ($1,000/yr), S3
(≈$15/mo, the one line that grows with the corpus blob), Codespaces ($0–50/mo),
Actions ($0) — sum to a near-constant **≈$5.5K/yr floor**. Everything above it
is inference `= events(N) × per-case(P)`. `N` moves the cert rank fill — much the
largest single channel — while **343 events ride beside it**, unbought by `N`:
20 CVSG re-forecasts and the ~98-case arrival cohort, which are
cert-stage but not `N`'s, plus ~98 interim (bounded by `interim_reserve_slots`)
and ~127 merits (every granted petition, whatever `N` is). `P` moves the rate
every one of those events is priced at, whichever channel produced it. So a
scenario states both dials: "how much of the cert rank fill, plus the 343 events
that ride beside it, times how many engines".

Where a row shows two figures, the first is the **planning basis** (`$15` a case,
the rate to fund against) and the second the **measured basis** — and that second
figure carries a heavy caveat everywhere it appears: it extrapolates a Term from
`$13.20–13.45`, a matched per-case cost measured over **six interim moments on
two application dockets, graded twice, under `proc-v3` evaluator digests that
`proc-v4` has superseded**. It answers "what if a Term were interim moments all
the way down", which it is not. Fund on the first column; read the second as the
open question.

| Scenario | ≈ Annual (planning · measured†) | Inference (= total − ≈$5.5K floor) | Dials, and what they reach |
|----------|----------|----------------------------------|-------|
| Bootstrapping | ≈$18.5K · ≈$17K | ≈$13K · ≈$11–12K | `N` = `per_conference_capacity: 12` (long conference 24), `P` = 3. ≈838–865 forecast events across all three stages, sal-v3 arrival cohort included — a **whole OT2026 Term**, not a slice of one: 613–640 cert (the OT2022–24 gate replay measures 495–522 selected a Term — rank fill plus uncapped carve-outs — plus 20 CVSG re-forecasts and the ~98-case arrival cohort), ~98 interim, ~127 merits. Keeps 0.76–0.81 of the Term's replay-reconstructable grant-family outcomes (0.80–0.84 of selectable ones), mostly via the carve-out band; a cap of 150 keeps 0.944–0.967 (measured, same pool) and would cost ≈$24K |
| Full paid-gate coverage — **the dial switch** | ≈$33K · ≈$30K | ≈$28K · ≈$24–25K | `N` at its ceiling, `P` = 3. All 1,498 paid petitions rank-filled (`1,498 × $15 ≈ $22K` — `N`'s own slice) plus the 343 beside-`N` events: `1,841 × $15 ≈ $28K`, or `× $13.20–13.45 ≈ $24–25K` measured. Both are **upper bounds** — 1,498 is itself one. `N` can buy nothing further, so salience survives here as the public ranking and the replay story rather than as a spend control ([salience.md](salience.md)), and incremental dollars move to `P` — or, cheaper, to `interim_reserve_slots` first: ≈$2.4K buys ~157 more interim events, an **alternative to the first `P` increment** rather than something taken alongside it (the `P` arithmetic in the next row prices engines over 1,841 events, which is the count *before* any reserve step) |
| Initial funding | ≈$100K | ≈$95K | Full paid-gate coverage at `P` = 3 (≈$28K planning · ≈$24K measured), with the remaining **≈$67K · ≈$71K on `P`**. Each added predictor costs `1,841 × (p + m)` a year — at the top of the `m` band, `≈$12.9K` planning / `≈$12.0K` measured for a frontier-class engine, `≈$6.2K` / `≈$5.3K` for an ablation- or open-weight-class one. That funds a registry of roughly **8 to 13 engines** on the planning basis, **8 to 16** on the measured one (whole engines only; the next one up is part-funded in each case). Read it as "many more than four", not as a target — it extrapolates the fully-linear `m` bound far past any run yet produced |
| Well funded | ≈$1M | ≈$995K | Either dial taken far. At the SCOTUS gate this funds a registry of dozens of engines; it is also the band in which the deferred scope decision first becomes affordable (the 14-court reference ceiling is ≈$675K at `P` = `E` = 3). Which it buys is the ~1-year scope call, not a budget one |
| **Floor (all scenarios)** | **≈$5.5K** | **—** | **misc + CourtListener + S3 + Actions; scales with neither `N` nor `P`** |

† The Initial-funding and Well-funded rows carry one figure because they are
*funding levels* rather than derived costs; the basis split appears inside them,
on what the money reaches. Every measured-basis figure inherits the six-interim-
event caveat above.

Two things the ladder makes visible. **Full cert coverage sits well inside the
initial-funding step** — it is the switch row above, at about a third of it —
which is why salience-as-spend-control is a *bootstrapping* argument
specifically. And the second half of that step is not more coverage but more
opinions per event: past the switch, extra funding buys `P`, and the cheapest
useful `P` is an ablation of an engine already in the registry rather than a
fourth frontier bill.

Start at **bootstrapping** with a small `N` and `P` = 3, let the ledger keep
measuring real per-case cost against the ≈$15 planning rate — the matched interim
measurement is the first hint it may be running conservative, on far too narrow a
base to act on — then raise `N` as funding lifts it, and `P` once `N` is spent.
`E` holds at 3 throughout. The funding path to each state — credit programs and
external support — is tracked in [milestones.md](milestones.md).
