# Budget

A cost forecast, not a spending cap: it sizes each driver so scope and cadence
can be chosen with the bill in view. Published list prices are USD, the rates
`fedcourtsai.pricing` carries, last changed **2026-08-14** — re-check the linked
sources before committing spend; the module flags the promotional rates that
expire on their own date. Measured figures carry their own as-of date where they
appear, since the usage ledger and the metrics pack refresh on different
cadences. The repo is **public**, so figures assume the free public-repo Actions
tier, and all inference is priced on the **on-demand API**. For how the phases
work, see [data-pipeline.md](data-pipeline.md) and [pipeline.md](pipeline.md).

## Figures at a glance

The operative numbers, each derived once in the section named:

| Figure | Value | Derived in |
|---|---|---|
| Planning rate, one fully-tournamented case | **$15** ($2.50 × 6 cells at the design mix) | *The planning rate* |
| Measured blended per-cell cost | ≈$2.04 — the ledger's mix, not the design's; fund on $2.50 (span ≈$0.25–8.30) | *The ledger* |
| Ledger to date (2026-08-29) | ≈$1,410 over 691 collected cells — a floor on provider-side spend | *The ledger* |
| Forecast events per Term, current dials | 838–865 ≈ **$12.6–13.0K/Term** | *Measured volumes* |
| Fixed floor | **≈$5.5K/yr** (+ ≈$0.25K/yr S3 ratchet) | *Summary* |
| Spend backstop | **$2,500 / 30-day trailing window** | *The spend backstop* |
| Full paid-gate coverage (the dial switch) | ≈$28K/yr inference, ≈$33K all-in — upper bounds | *What `N` can ever buy* |
| Whole-docket / 14-court reference ceilings | ≈$83K/yr · ≈$675K/yr | *Scope and the cell identity* |

## The shape: a fixed floor plus one dominant scaling line

Every non-inference line — runners, storage, memberships, subscriptions — sums
to the ≈$5.5K/yr floor, near-constant but for one slow ratchet: retained corpus
history adds ≈$0.25K to each further year the writers run (*4. S3 corpus
storage*). Agentic model usage for prediction and evaluation is one to two
orders of magnitude larger and scales linearly with how many events, by how many
predictors, scored by how many evaluators. So the budget is
`fixed floor + events(N) × per-case(P)`, with **two dials**:

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
([process-version.md](process-version.md)).

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
upper bound on the pool. Past that state raising `N` buys nothing, and
incremental dollars switch to `P` — the ordering the *Scaling plan* below lays
out end to end.

The flat **Claude Max** subscription cannot absorb automated volume — it is
metered for interactive use, and per Anthropic's policy the subscription token
is meant for Claude Code / claude.ai, not CI/CD. So it covers interactive
development, while every automated stage (`run:predict`, `run:evaluate`)
authenticates to Claude via the Anthropic **API key**.

## What there is to predict: measured volumes

Per October Term. The cert and merits lines are the OT2017–2024 **paid**
census, where every row carries `sample_weight` 1: the paid stream is walked
denial-complete, so these are counts rather than reweighted estimates, and the
committed `metrics/statpack.json` carries those Terms unweighted
(`weighted_resolved == resolved` on every paid row). The IFP stream genuinely
is still sampled, which is why the IFP-inclusive figure below is an estimate
and these are not. The interim line is one application year, OT2025 — the last
near-complete one: the OT2026 application year has opened (255 parsed
application dockets to date in the current statpack), so OT2025's cohort no
longer grows materially, while its rates below were measured Term-to-date.

| Bucket | Per Term | What it is |
|---|---:|---|
| Cert — paid modern-cert petitions | 1,498 | at most the pool the gate selects from (11,987 rows over eight Terms) |
| Merits — cert grants opening a proceeding | 65 | paid `granted`, excluding the `gvr` label, which disposes of a petition without opening a proceeding |
| Interim — substantive applications | 179 | 13.1% of OT2025's 1,365 parsed application dockets; 82.6% are extensions and 4.2% unreadable asks — pre-capital-strip statpack figures (the first post-strip refresh reads 227 of 1,467, 15.5%; the freeze record registers that boundary). Recompute from the statpack's `interim` section rather than quoting these |

**A case is forecast more than once.** Each stage asks one question and the
case passes several points at which it can honestly be forecast, each with a
different information set. The moments are separate events, separately scored
and never pooled ([salience.md](salience.md)); each costs one fully-tournamented
case-equivalent.

| Stage | Moment | Events / Term | Coverage basis |
|---|---|---:|---|
| cert | first distribution | 495–522 | the OT2022–24 gate replay at `per_conference_capacity: 12` (see below) |
| cert | CVSG | 20 | 1.33% of paid petitions — but 7.0% of the paid census's grants |
| cert | arrival | 98 | the arrival cohort, beside `N` (see below) |
| interim | arrival | 67 | 5 reserve slots turning over at a 27.1-day mean occupancy |
| interim | response requested | 10 | 15.1% of the 67 selected arrivals — 27 of OT2025's 179 substantive applications (pre-capital-strip; the post-strip denominator is 227, reading 11.9%) |
| interim | response filed | 21 | 30.6% of the 67 selected arrivals — the rate measured over the 219-substantive population the moment was declared against (a coincidental second 67: 67 of those 219 drew a filed response); the response-filed timestamp is published in no artifact, so this one rate cannot be refreshed from the pack |
| merits | grant | 65 | **every** granted petition — the gate is bypassed at this stage |
| merits | briefed | 62 | 96.4% of the 65 grants reach a respondent merits brief, rounded down |
| | **total** | **838–865** | **≈$12.6–13.0K/Term** at the $15 planning rate |

Two of those rows need their derivation spelled out:

- **First distribution, 495–522** is measured by the gate replay **under
  sal-v1** — the one consolidated staleness note for every replay-derived
  figure in this document: `metrics/salience-replay.json` (refreshed
  2026-08-07, OT2022–24) predates the active **sal-v4** gate, so replay figures
  are a lower bound for it. Sal-v4's federal carve-in also reaches conference
  cohorts (≈16.5/Term more under the active caption-v2 rule), unmeasured until
  a caption-banded replay refresh; a refresh moves the selected count, the
  rank-fill split, the recall band, and the Bootstrapping scenario row
  together. The 495–522 decomposes as rank fill 398–413 cumulative through
  resolution (380–386 at first distribution) plus uncapped carve-outs 97–115.
  The escalation program alone — the moments total less the ~98-event arrival
  cohort — lands at ≈$11.1–11.5K at the planning rate, ≈$12.6–13.0K with it.
- **Arrival, 98** is the active scorer's arrival cohort, **beside** `N`,
  filling forward from the registration-fixed cohort start (the OT2026
  docket-year roll — the standing pending backlog never enters): 75 from the
  1-in-20 deterministic random slice over ~1,500 paid arrivals
  (`salience.arrival_sample_rate`) + ~23 from the federal-petitioner carve-in
  under `caption-v2`, whose census run passed statistical verification (8/8
  complete Terms at 9.1–17.7× lift; per-Term 11–41 — [salience.md](salience.md)).

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
enriched in exactly that property — read the 10 as biased low for the selected
slice, bounded above by the 67. Two populations answer the rate and they
differ: 15.1% is OT2025's (27 of its 179), while the whole accumulated
substantive slice the interim estimator pools over runs about a fifth (54 of
263 — `metrics/statpack.json` as refreshed 2026-08-29, the vintage every
accumulated interim count here carries). And the 67 divides slot turnover by
the stream's 27.1-day mean occupancy, while the ladder plausibly favors
longer-lived applications (p95 110 days), which would cut arrivals below 67.

Two denominators are easy to confuse. The **≈5,500** the gate is priced on
below counts cert decisions across both fee streams; the gate excludes IFP at
Tier 0 ([salience.md](salience.md)), so the pool it can ever select from is at
most the **1,498** paid petitions — an upper bound, because seven further rules
in `OUT_OF_SCOPE_RULES` cut it again, as does the snapshot-aware bare-import
rule that `out_of_scope_reason_full` adds. So ≈$83K is the whole-docket
ceiling and ≈$22K the first-distribution slice — the most the capacity dial can
ever buy, not the whole-Term bill of that state (*What `N` can ever buy*).

**The cap is sized to bind, and the gate replay at the shipped capacity
measures that it does.** Raw paid cohorts run a median 34 petitions (p90 82,
max 369); the pool the replay ranks — replay-reconstructable resolved paid
petitions, 1,239–1,358 a Term — runs a mean conference cohort of ~37, and at
`per_conference_capacity: 12` the cap binds **29 of each Term's 33–36
reconstructable first-distribution cohorts** across OT2022–24. The comparison
that sized it: a capacity of 150 would cut just 8 of 251 raw cohorts and
exclude 5.3% of petitions — selecting ~95% of the paid docket and funding
~$24K/Term, a ranking rather than a spend control. The measured coverage trade
at the shipped 12 (long conference 24): the selection carries **0.76–0.81** of
the Term's replay-reconstructable grant-family outcomes (grant denominators
90/108/91 for OT2022/23/24, GVRs and summary reversals included), resting
mostly on the uncapped carve-out band. Of those grants, 4/6/3 a Term sit on
blind rows — no reconstructable selection moment, so no gate could select them
— leaving selectable denominators of 86/102/88: recall of the *selectable*
outcomes is 0.80–0.84, and 0.944–0.967 is the achievable ceiling at any
capacity. The prior committed replay — run at the then-shipped 150/200 caps
over this same pool, so capacity is the only delta between the two — measured
exactly that ceiling: a cap of 150 selects
everything selectable and buys no coverage the blind rows do not already deny.
(The replay runs with no reserve occupancy; the interim reserve's slots in use
would lower the rank fill — *The interim reserve*, below.)

**A re-queue is not a re-run.** A selected cert petition re-queues on a
distribution transition outside the same-day cooldown
(`salience.relist_requeue_cooldown_days`), and petitions are distributed a raw
mean of 1.46 times each. But `predict_matrix` drops any `(predictor, event)`
cell whose predictor already committed a prediction for that event, at plan
time, before any agent cell is minted — so a relist costs runner minutes,
provisioning, and poll quota, not inference. The one gap is concurrency: the
drop reads the checked-out ledger rather than taking a lock, so two runs
planned before either's collect PR merges both see an unpredicted event and
both mint. Re-forecasting a changed posture is available as a deliberate change
(`skip_predicted=False`); its multiplier is above 1.46, because the funded
population is the relist-selected slice rather than the docket-wide mean.

## Cost drivers

### 1. Model usage (the dominant cost)

Three engines run the agentic stages, routed per registry entry
([config/predictors.yaml](../config/predictors.yaml),
[config/evaluators.yaml](../config/evaluators.yaml)):

| Engine | Used by | Billing | Rate (per 1M tokens) |
|--------|---------|---------|----------------------|
| Claude Code (`claude-fable-5-1`) | `claude-baseline`, `claude-judge` (predict/evaluate default) | Anthropic API (workflows); Max subscription for interactive local dev | Subscription: $200/mo flat (Max 20x — dev only, in floor #5). API: $10 in / $50 out |
| Codex (`gpt-5.6-sol`) | `codex-baseline`, `codex-judge` | OpenAI API (pay-per-token) | $5 in / $30 out |
| Gemini (`gemini-3.1-pro-preview`) | `gemini-baseline`, `gemini-judge` | Gemini API (pay-per-token) | $2 in / $12 out (≤200k context; steps up beyond) |

Sources: [Claude Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan),
[Claude API pricing](https://platform.claude.com/docs/en/pricing),
[OpenAI API pricing](https://developers.openai.com/api/docs/pricing),
[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

**Scope: the SCOTUS-docket gate.** The pilot predicts and evaluates only SCOTUS
dockets. Ingestion is unchanged — the channels still assemble all fourteen
courts deterministically (≈$0 model spend) so the full history stays queryable
for retrieval and back-testing; only the agentic stages are gated.

#### The ledger and per-cell cost

A predict or evaluate run is *agentic* — the agent reads the prompt, AGENTS.md,
the case snapshot, and retrieved priors, then writes its artifacts over several
tool-use turns — so effective token usage (≈280–400K input, the large majority
cache-served, plus ≈6K output) far exceeds the visible artifacts. Every run
records its tokens and estimated cost (rates kept in `fedcourtsai.pricing`) to
a `usage.json`, rolled up by `fedcourts usage-summary` — **≈$1,410 total
inference spend on the ledger** as of 2026-08-29, across the 691 cells the
per-cell figures below draw on (641 predict, 50 evaluate).

That estimate is token-derived, so hosted web search — billed per call rather
than per token on all three APIs — sits outside it and makes a searching cell's
recorded cost a mild undercount. The ledger also counts **collected cells
only**: a cell's `usage.json` reaches `data/` on its run's collect PR, so a
stranded run — one whose cells burned tokens but whose output never landed —
spends against the provider bill and never appears here. Every measured figure
below is therefore a floor on provider-side spend, not a reconciliation of it.

Measured per-cell cost spans **≈$0.25–8.30 by model mix**, blended mean
**≈$2.04**. The cheapest cells approach ≈$0.25 only when the byte-stable prefix
(AGENTS.md + prompt template + schema) is served from the prompt cache —
automatic on all three engines, billing cached reads at ≈0.1×, and the reason
to keep that prefix stable. **The $2.04 is the ledger's mix, not the design's**:
641 of the 691 cells are predict, and evaluate cells cost more, so the mean the
funding knob has to cover is the one at the design mix of three predict and
three evaluate cells per case — **$2.44–2.49** ($14.6–15.0 ÷ 6, derived under
*The planning rate*). The planning rate is set at the top of that mean's band
($2.50 a cell), not above the top of the per-cell *range*, which no cell budget
could be.

#### Per-cell cost is keyed on the stage

The first predict fan-out to land after the pre-registration freeze instant
([process-version.md](process-version.md)) — run `20260816T111104Z`, 81 cells
over 27 events — is the anchor measurement covering the arrival, interim, and
merits moments rather than cert alone. ("Post-freeze" throughout this document
names the August cohort stamped after the 2026-08-16 `proc-v3` instant; the
`proc-v5` and `proc-v6` re-blesses have since re-based the frozen partition, so
these are measurement cohorts, not claimable-partition members. Every measured
Claude figure in this document was produced on `claude-fable-5`; the point
release holds its rate, so the dollar figures carry to the current default and
only the token volumes rest on the two being comparable.)

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
arrival moment**, on 11 events against 12. The other stages are not separated
at these `n` — the interim row is a single event whose $5.49 sits inside both
the cert-arrival per-event range ($4.66–$8.94) and the merits one
($5.45–$10.77); the wider post-freeze population below reads interim at $6.41
over 12 events, so it is not the cheap stage this single draw suggested. That
wider read narrows the one finding without unseating it: merits still runs
above cert, $7.60 against $6.68, by ≈$0.9 rather than ≈$1.2.

The larger-sample reference is the pre-freeze cert-era ledger — **410 predict
cells over 137 events** (an incomplete grid: 138 / 132 / 140 cells by engine,
132 events carrying all three) at claude-baseline ≈$3.65, codex ≈$1.38, gemini
≈$0.55, a per-event **$5.57** — every one of them the cert first-distribution
moment. The gap between that $5.57 and the run's $6.79 is **half
decomposable**: the mix half is measured (the arrival and, dominantly, merits
moments enter a population the pre-freeze ledger measures as
first-distribution only), while the level half is not — at the same moment the
run's three events average $6.66, ≈+20%, but each sits inside the pre-freeze
per-event range ($2.98–$10.04, mean $5.61, SD $1.25 over the 132 complete
events, one cell per engine per event; the complete-grid $5.65 below sums the
re-run cells instead), and drawing three pre-freeze events at random clears $6.66 about 7% of
the time. The two cohorts also straddle a process boundary: all 410 pre-freeze
cells **predate process stamping** entirely, while the run cells carry a
process digest defined over prompt bytes and resolved config — the very inputs
that set token count. Treat **≈+20% as an upper bound on any level effect**,
not a measurement of one. Plan against $6.79 and expect it to move.

**The wider post-freeze predict population corroborates $6.79, but only once it
is mix-matched.** Across all post-freeze predict cells (as of 2026-08-29) the
complete-grid population is 76 events at **$6.99** an event — but that
population is ~46% cert, ~16% interim and ~38% merits, against a Term of ~73% /
~12% / ~15%, so the raw figure is what a *merits-heavy* run costs, not a Term
rate:

```
complete-grid post-freeze predict, by stage   cert    $6.68  (n=35)
                                              interim $6.41  (n=12)
                                              merits  $7.60  (n=29)
reweighted by the Term's mix (613-640 cert / 98 interim / 127 merits)
                                              ≈ $6.78-6.79 an event
```

The same objection lands on $6.79 itself — the anchor run was 11/27 merits, and
reweighted the same way it reads $6.44. And the check is not independent:
27 of the 76 events *are* the anchor fan-out. Over the 49 events it does not
contain, the per-stage rates — cert $6.91 (n=20), interim $6.50 (n=11), merits
$7.68 (n=18) — reweight to **$6.98**: independent corroboration of the
magnitude, not of the point, some 3% above $6.79. That direction matters below:
it eats what little headroom the planning rate has rather than adding to it.

#### Evaluate cost: narrower, weaker, and mid-re-anchor

The evaluate side is measured on a narrower base, and its cohorts do not pool —
they split the same way the predict cells do:

| Evaluate cohort | Events | `claude-judge` | `codex-judge` | `gemini-judge` | Per event |
|---|---:|---:|---:|---:|---:|
| `proc-v2` stamped, pre-freeze (run `20260814T033644Z`) | 3 | $4.86 | $1.07 | $0.79 | $6.71 |
| unstamped, pre-freeze (run `20260718T000134Z`) | 1 | $4.16 | $0.92 | $0.52 | $5.60 |
| pre-freeze pooled | 4 | $4.68 | $1.03 | $0.72 | $6.43 |
| `proc-v3` stamped, post-freeze (run `20260824T231401Z`) | 6 | $4.16 | $1.51 | $0.77 | $6.44 |
| `proc-v3` stamped, post-freeze (run `20260825T024608Z`) | 6 | $4.79 | $1.22 | $0.68 | $6.69 |

The four pre-freeze events are all cert-stage, so that anchor is stage-narrow
whichever row is read — and the pooled row crosses a process boundary (three
stamped events, one unstamped), the same pooling defect the predict side is
careful to avoid, with the single month-older unstamped event pulling the
pooled figure down ≈4%. **$6.71 is the better-matched pre-freeze anchor and
$6.43 the more cautious one**, which is why the per-case figure below is a band.

**The two post-freeze rows are one six-event population read twice** — both
runs graded the same six interim moments (two application dockets × three
moments each), independently and without seeing each other's output. The second
adds no coverage, but the pair is the ledger's only clean run-to-run variance
measurement under one process: ≈4% ($6.44 against $6.69). Grading those six
events twice cost $13.13 an event of *coverage* — not the steady state a
per-case rate models, but not a number to lose either.

Three qualifications bound these rows. **n = 6**, on two application dockets.
**One stage**: all six moments are interim, against a Term whose forecast
events run ~73–74% cert. And the gradings are attributable but for one partial
cell — 105 of the two runs' 108 `evaluation.json` records carry `proc-v3`
evaluator digests, the three exceptions sitting on that cell — yet what they
are attributable *to* is digests `proc-v4` retired over a batch of
judge-prompt changes — the
token-relevant one being the judge-workspace prune, which hides the committed
`predictions/` and `evaluations/` trees from a judge cell's working tree.
(`proc-v5` carried those evaluator digests forward byte-identical; `proc-v6`
moves the evaluate prompt's bytes for all three judges, so none of these
gradings ran under the currently blessed evaluator process and every figure
here is a measurement cohort.)

**The newest grading is one moment on since-superseded digests, and is too
partial to re-price anything.** Run `20260829T040550Z` graded one interim
moment under `proc-v4`: claude-judge **$4.91**, gemini-judge **$0.49**; the
codex-judge cell failed there and again in its retry run (`20260829T080658Z`),
so the event has no per-event total. One event, on a third application docket
(the six `proc-v3` moments sit on two others), with an incomplete grid — and
no direction readable: both measured cells fall inside, or within a dime of,
the per-event ranges the two `proc-v3` runs already spanned ($3.26–5.28 /
$4.15–5.18 for claude-judge, $0.58–1.20 / $0.57–0.85 for gemini-judge), so the
prune's projected downward move is neither confirmed nor refuted — the same
single-draw discipline the predict side's interim row carries. A population to
re-read at the next evaluate fan-out, not a correction to apply.

What none of this establishes is the tempting reading: the interim rows are
**not** evidence that the assumed ≈+22% uplift below failed to appear, because
the pre-freeze anchors they would be compared against are cert-stage, and no
pre-freeze interim-stage evaluate measurement exists. The first stamped
evaluate measurements come in *below* what the uplift assumption projects, at a
stage the anchor does not cover — a signal to check, not a correction. That is
why the figures below carry a **measured-basis** reading beside the
planning-rate one rather than replacing it.

#### The planning rate, and the re-anchor that would move it

One fully-tournamented case at the shipped `P = E = 3`:

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

The two bases answer different questions. The planning basis prices *a Term*:
an all-stage predict figure plus an evaluate half the ledger cannot yet supply,
filled by assumption — the evaluate half **scales by the whole predict move**
(`$5.57 → $6.79`, ≈+22%): `$6.43 × 1.218 ≈ $7.84` on the pooled pre-freeze
anchor, `$6.71 × 1.218 ≈ $8.18` on the better-matched proc-v2 one. The
measured basis is the only fully-measured per-case figure the ledger contains —
but it prices six interim events under superseded evaluator digests, so it
answers "what would a Term cost if it were interim moments all the way down",
which it is not. Fund on the first; read the second as the open question.

Two caveats on the +22%. Only its mix half is measured — applying it assumes
evaluate's stage mix broadens as predict's has *and* that whatever level effect
sits in the residual applies to judging too. And it joins two
differently-built means: matched to the complete grid, the pre-freeze figure is
$5.65 over 132 events and the move is +20%, not +22%. The $15 rate keeps the
+22% factor — it is the one the plan seams transcribe — but the factor is ~2
points generous, a small offset against the $6.98 independent predict reading
pulling the other way.

Three numbers to hold apart. **$13.20–13.45** is the matched measured basis,
over six interim events. **$14.6–15.0** is the Term expectation once the
scaling is applied. **$15** is the planning rate; divided across the design mix
of six cells it is the **$2.50 per-cell rate** the ceilings are priced on.

**Fund against $15, and do not treat any of the gaps as headroom.** Against the
assumed evaluate half on the $6.79 anchor, $15 clears the band by ~2.5% at the
pooled reading and effectively nil at the better-matched one. Swap in the
independent $6.98 predict reading and the band becomes $14.82–15.16 — $15 sits
inside it, ~1.1% short at the top, and that is the reading no anchor-selection
can flatter. Against the matched interim measurement $15 carries ≈11–14% — but
that holds a Term rate against one stage's measured cost, and interim is
~11–12% of the Term. Two gaps pointing opposite ways, neither settled: the
wider predict population says the rate may be slightly low, the interim
gradings say the evaluate half may be high.

**The re-anchor trigger is unmet on both halves.** It waits on an evaluate
fan-out under the currently blessed grading digests **reaching the cert stage**
— the stage the Term is mostly made of. No grading anywhere ran under a blessed
evaluator digest: the partial interim measurement above is the closest, and its
digests are superseded. That run, not a fuller ledger, is what settles it — and
re-anchoring is deliberately a code change, not a document edit: the plan
seams' per-cell rate table is a transcription of these figures and its
per-event sums are pinned by test, so a re-anchor re-prices every plan
visibly.

#### Scope and the cell identity

The unit throughout is the **agent cell**, and both roles fan out the same way:
one predict cell per (predictor, event) and one evaluate cell per (evaluator,
event) — a judge grades *every* predictor for its event in a single invocation,
so cross-evaluation multiplies the `evaluation.json` count but not the cell
count. A case therefore costs **`P + E` cells, not `P × E`** — at the shipped
`P = E = 3`, **6 cells per case**. That identity is the seam between the two
dials: raising `P` adds predict cells at the new engine's own rate, adds no
evaluate cell (`E` is fixed), and makes each existing evaluate cell *larger*,
since every judge reads one more prediction — the unmeasured margin `m` under
*Registry size `P`*.

Full 14-court scope is the reference ceiling, held at `P = E = 3`:

```
predictions  ≈ 48,000 events   × 3 predictors (P) × $2.50   ≈ $360K
evaluations  ≈ 42,000 resolved × 3 evaluators (E) × $2.50   ≈ $315K
                                                              ────────
full scope                                                    ≈ $675K / yr
```

It prices a scope change that is deferred (*Deferred scope, unpriced*) — a
reference ceiling, not a plan. The SCOTUS gate is roughly 1/8 of it — ≈5,500
cert decisions per term, both fee streams:

```
predict   ≈ 5,500 × 3 (P) × $2.50   ≈ $41K
evaluate  ≈ 5,500 × 3 (E) × $2.50   ≈ $41K
                                     ───────
full cert gate                       ≈ $83K / yr
```

The gate never selects an IFP petition, so the pool it can rank-fill is the
1,498 paid petitions: `1,498 × 6 cells × $2.50 ≈ $22K/yr` — the
first-distribution slice, `N`'s own ceiling.

#### Capacity `N`: the funding knob

`N ≈ inference_budget / (≈$15 per fully-tournamented case)`. Tier-1 salience
scoring is itself ≈$0 (a deterministic pure function of corpus features, no
model call), so the gate spends nothing to *decide* what the tournament runs
on. Raising `N` deepens the salience-ranked slice; it never reshuffles the
ranking.

**What `N` can ever buy.** The ≈$22K first-distribution slice is `N`'s own
ceiling and so the phase policy's switch point. The whole-Term bill in that
state is larger, because four channels ride beside `N` rather than inside it —
CVSG re-forecasts, the arrival slice, the reserve-bounded interim stream, and
the merits stage, whose volume the Court sets:

```
cert-stage  1,498 first distribution + 20 CVSG + 98 arrival  = 1,616 events
other            98 interim + 127 merits                     =   225 events
                                                               ───────────
                                                               1,841 events

cert-stage  1,616 × $15          ≈ $24.2K / yr  (N's own slice within it ≈ $22K)
whole Term  1,841 × $14.6-15.0   ≈ $27-28K / yr   planning basis
            1,841 × $13.20-13.45 ≈ $24-25K / yr   measured (interim, n=6)
plus the ≈$5.5K floor            ≈ $33K / yr all-in  ( ≈$30K measured )
```

Every figure in that block is an upper bound — 1,498 is itself one. One thing
can carry it past the bound: deliberate re-forecasting (`skip_predicted=False`),
whose multiplier on the relist-selected population runs above the docket-wide
1.46. The bound holds for the shipped default, where a relist costs runner
minutes rather than inference.

The four beside-`N` channels are held at their measured sizes, since none is
set by `N`. One is a spend step in its own right, and one can never be:

- **`interim_reserve_slots` is the cheapest step at the switch point.** The
  reserve is set to `5` against the ≈13 concurrent slots OT2025's arrival rate
  implies, so raising it to 13 scales the whole interim slice:
  `98 × (13/5 − 1) ≈ +157 events ≈ +$2.4K/yr` at the planning rate (≈$2.1K
  measured). That is cheaper than the cheapest `P` step below at the
  `m`-at-ceiling corner (≈$6.2K planning / ≈$5.3K measured a year for an
  ablation-class engine); at
  `m` = 0 a cheap fourth predictor would undercut it — one more reason `m` is
  the figure worth measuring. It is also where the interim stream stops being
  a ladder-ordered subsample and becomes the stream. The step belongs *at* the
  switch point rather than before it, because while `N` binds every added slot
  costs a cert pick (the reserve is defined inside `N`, below).
- **`salience.arrival_sample_rate` is not a dial at all.** The 1-in-20 draw
  runs under a registration-fixed key and is effectively frozen once the
  cohort runs; moving it declares a new pre-registered population rather than
  widening an existing one ([salience.md](salience.md)). Money cannot buy
  arrival coverage.
- The merits stage is the Court's own volume, and CVSG is a rate on the paid
  pool — neither answers to funding.

#### Registry size `P`: the breadth dial

Past the switch point the money goes to `P`, and `P` prices differently: `N`
multiplies a fixed per-case rate, while `P` changes the rate itself:

```
per-case(P)  =  Σ over the registry of predict_i     (P cells, one per registry entry)
             +  Σ over the judges  of evaluate_j(P)  (E = 3 cells, each growing with P)
```

**The predict half is a sum over the registry, not a multiple of an average.**
The provider table below measures the three engines at $4.27 / $1.88 / $0.64 an
event — a **6.7× spread** (6.9× on the wider complete-grid post-freeze
population, $0.64–4.39) — so *which* engine is added matters more than *that*
one is. A fourth predictor adds its own line to the sum and, if it is a new
engine, its own row to the engine rate table.

**Which is also how the plan seams price it, and the two ways they can be
wrong.** `predict-plan` and `evaluate-plan` cost a matrix from a per-(seam,
engine) rate table drawn from the tables above, keyed on the resolved
**engine**, not the predictor id:

- A predictor on a **new engine** prices at the $2.50 design-mix fallback — a
  flagged approximation: the plan counts those cells in
  `cells_at_fallback_rate` and carries a caveat naming the fallback.
- An **ablation variant** of an engine already in the registry prices at its
  *parent's* rate, and is **not** flagged — but an ablation varies exactly the
  inputs that set token count (prompt bytes, retrieval surface, resolved
  config), so its true rate is the one thing the parent's rate cannot be
  relied on for. An unmarked approximation on the dimension the ablation
  exists to change.

Neither is settled until a fan-out measures the new entry.

**The evaluate half grows by an unmeasured margin `m`** — the per-case evaluate
growth per added predictor, summed across the three judges. It is unmeasured
and not measurable from this ledger: every evaluate cell on it ran at `P = 3`,
and `m` is a difference between two registry sizes. What can be said is the
bound — a judge's fixed costs (the prompt, the snapshot, the case record read
once) are shared across every prediction it grades, so `m` should sit below a
proportional share; the fully-linear case bounds it above, on each basis:

```
m  ≤  evaluate(3) / 3

  planning basis   $7.84 / 3  ≈  $2.61      measured basis   $6.44 / 3  ≈  $2.15
                   $8.18 / 3  ≈  $2.73                       $6.69 / 3  ≈  $2.23

  0 ≤ m ≤ ≈$2.6-2.7  (planning)             0 ≤ m ≤ ≈$2.15-2.23  (measured)
```

Neither ceiling is a measurement of `m`; re-anchoring the evaluate half re-cuts
both with it. The `P = 4` step, built on the same anchors as the $15 rate:

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
and **$0.6–6.5** on the measured one — wide enough that the *class* of engine
added is a budget decision rather than a rounding one. Annualized at full
paid-gate coverage (1,841 events, itself an upper bound):

| `P` | per-case(`P`) | Full coverage, inference / yr |
|---:|---|---|
| **3** (shipped) | $14.6–15.0 planning · $13.20–13.45 measured (interim, n=6) | ≈$27–28K · ≈$24–25K |
| 4 | $15.3–22.0 · $13.8–20.0 | ≈$28–40K · ≈$26–37K |
| 5 | $15.9–29.0 · $14.5–26.5 | ≈$29–53K · ≈$27–49K |

(Each row takes the corners of the block above `P − 3` times over; the annual
column multiplies by 1,841 events.) Read each band's top as a worst-corner
bound, not a forecast — but note what it bounds *over*: $4.27 is the dearest
**currently-priced** class, not a ceiling on what a cell can cost. A new
frontier engine could price above it, and hosted web search is billed per call
outside the token estimate, so a search-heavy predictor exceeds any of these
figures. The linear `m` bound is an assumption about *shape* — nothing measured
here rules out a judge's lengthening context pricing superlinearly. Nothing
here should be extrapolated far past `P = 5`.

**The first `P = 4` fan-out is the re-anchor point for `m`**: `m` is settled by
differencing that run's evaluate cells against a `P = 3` evaluate measurement
on the same stage mix, and until that pair exists the bands above are
arithmetic rather than estimates.

**Which predictors to add, in value-per-dollar order.** The criterion is not
diversity of opinion — it is **causal attribution**: how much of what the
registry learns from a new entry can be attributed to a named cause, per dollar
spent. On that criterion the cheapest class ranks first, which is convenient
but not the reason:

1. **Ablation variants of engines already in the registry** — the same engine
   with a changed prompt, config, or retrieval surface. Cheapest to add (no new
   provider account, an existing measured rate for its parent) and the only
   class where a difference in score is attributable to a named factor, because
   everything except the ablated one is held constant by construction. The
   process digest moves with the prompt bytes and resolved config, so the
   variant partitions from its parent rather than pooling with it
   ([process-version.md](process-version.md)). Note what an ablation is *not*:
   it is the least independent addition the registry can take, so it widens
   attribution, not coverage.
2. **Open-weight models, Bedrock-hosted** — a family the current registry
   cannot reach on the credit stack it runs on. AWS Activate is the runner-up
   credit program in [milestones.md](milestones.md), and its credits apply to
   AWS services — so Bedrock-hosted inference converts a credit line the
   Anthropic / OpenAI / Google registry has no way to spend. Per-token rates
   unmeasured here; the registry sum takes a new open-weight entry at the
   bottom of the measured spread until a fan-out prices it.
3. **Additional frontier providers** — the dearest line in the registry sum,
   and the one whose forecasts the design expects to overlap most with what
   three frontier engines already produce (an expectation, not a measured
   correlation — no inter-predictor agreement number exists,
   [metrics/README.md](../metrics/README.md)). Worth adding, last.

**Only the first class is a registry edit.** `engine` is a closed enumeration —
`claude-code`, `codex`, `gemini` — mirrored into the exported predictor schema,
so classes 2 and 3 are code changes, not config ones: a fourth engine needs an
enum entry, a default model in the pricing table, a retrieval-surface entry in
the process-version registry (indexed rather than looked up, so a new engine
fails loudly until it is declared), a runner, and its own workflow steps. An
ablation
variant needs a registry entry and a prompt. That adapter cost is real, is in
no dollar figure above, and reinforces the ordering.

**`E` stays at 3 through all of this** (*The shape*, above). A new predictor
being cheap to grade is not an argument for making it a judge, and no step on
the `P` dial moves `E`.

#### The interim reserve and the merits stage

**The interim docket is a quota'd stream, capped at five cases in flight.**
Across OT2025's 1,365 parsed application dockets, 82.6% are time-extension
requests and 4.2% carry an ask the parser cannot read; both are filtered out
deterministically by `interim_signals.is_predictable_application` (≈$0, no
model call), leaving the 13.1% substantive slice as the only population ever
predicted. (Pre-capital-strip figures: the docket-number strip admits 102
previously unparsed OT2025 application dockets, and the first post-strip
statpack reads 1,467 parsed / 80.5% extensions / 15.5% substantive — the
boundary the freeze record registers.) The stream is budgeted as a **bounded reserve defined inside the
per-conference spend envelope**: `salience.interim_reserve_slots` in
[config/tracking.yaml](../config/tracking.yaml), set to `5` and enforced by the
selection pass — slots in use shrink the rank fill in the pass's latest
conference cohort (carve-outs above `N` are untouched). At
`per_conference_capacity: 12` a full reserve leaves a rank fill of 7, far below
the ~37-petition mean reconstructable cohort, so a slot in use displaces a cert
pick rather than adding spend at essentially every capacity-bound conference,
as designed; the displacement *frequency* is unmeasured, because the gate
replay runs with no reserve occupancy. At capacity 12 the reserve claims about
40% of the rank-fill limit — a materially larger share of a small `N` than of a
large one, worth revisiting alongside it; at `N ≤ 5` only the always-include
carve-outs would be funded.

Where the quota bites, it bites prospectively, pass by pass: sticky
already-latched picks are never de-selected and the pre-scoring fail-open
window rides outside the quota for one cycle, so a conference's realized count
can transiently drift above `N` — the same bounded drift the carve-outs already
produce ([salience.md](salience.md)). A selected application occupies its slot
until it resolves, so the reserve's firm effect is on *concurrency*: at most
five interim cells in flight, against the ≈13 substantive applications live at
any moment on OT2025's arrival rate. An unfilled reserve costs nothing. The
slice is predicted, and its base rate is registered and wired — pooled over
application Terms strictly before the case's own, above its own per-pool floor
([salience.md](salience.md)).

Two bounds on the interim figures. Lifespans run from each docket's first entry
to its disposing entry rather than the `date_filed` / `date_decided` columns
(null on a substantial minority of rows, disproportionately the long-lived
ones); an entry-based lifespan exists only for a resolved application, so the
measure covered 218 of the 219 rows it was taken over. And the arrival counts
were taken while the application year was still open — a partial year divided
into a full-year denominator, so saturation is understated, not overstated.

**The merits docket: a second cell on a case already funded, unbounded by
design.** A cert grant opens a merits event
([decision-model.md](decision-model.md)), and that event is forecastable — so a
granted docket buys one more predict cell per predictor and one more evaluate
cell when the judgment lands: roughly a second ≈$15 case-equivalent where the
gate funded the cert cell, and slightly more (the merits stage measures $7.47
an event, n=11, against the $6.79 run mean — the one stage the anchor run
separates). At the projected ~80% grant coverage that second equivalent is
about four merits cases in five; the other ~13 of the 65 open on dockets the
gate never cert-funded, a first case-equivalent rather than a second. (The ~80%
stays a projection: the replay's 0.76–0.81 is grant-*family* recall, and GVRs
and summary reversals open no merits cell, so the merits-opening rate is a
denominator the replay does not report.) Unlike the interim stream this carries
**no reserve and no quota** — deliberately: the population is self-limiting
(the Court grants on the order of sixty cases a Term), each cell is minted once
and occupies nothing until its judgment lands, and the grant is the outcome the
whole cert tournament is ranked on. The per-run cell cap and the spend backstop
still hold the fan-out; if the grant cohort ever stops being self-limiting the
honest fix is a reserve of its own, not a wider cap.

#### The spend backstop

Capacity `N`, the per-run cell cap (`predict.max_predict_cells_per_run`), the
live cycle's sweep cap, and the per-cell attempt caps are all **ex ante** —
each bounds one decision or one run, and none knows what has been spent. They
compose into a per-run limit with no per-period limit above it: across the
day's scheduled windows, spend is bounded only by how many cells happen to be
owed, exactly the quantity that becomes large at a long conference. The `spend`
section of [config/tracking.yaml](../config/tracking.yaml) is the bound above
them — a trailing-window ceiling on **measured** cost, read from the committed
`usage.json` ledger by both plan seams before either mints a matrix. Reaching
it **defers**: the predict queue and the evaluate backlog are untouched and
re-derive next cycle.

The shipped value is **$2,500 over a 30-day trailing window** — ~1.7× the
Term's average month (≈$1.40–1.45K: 838–865 events/Term at the $15 planning
rate over the ~9 months the Term spans; on a 12-month spread the multiple is
~2.3×, so the claim is conservative).

What it protects against is chiefly a **burst**; the margin against a sustained
*rate* is thin. The shipped steady state cannot reach the ceiling — the mean
month sits at ≈$1.4K, the heaviest month's build-up at ≈$2.0K. A regression to
a non-binding cap *can*: it burns $2.0–2.7K per 30 days (the prior 150/200
replay selected 1,228–1,349/Term ≈ $18.4–20.2K, and the 150-cap comparison
funds ≈$24K/Term), a trailing sum whose upper end asymptotes above the ceiling.
Deferring there is defensible — a non-binding cap *is* a mis-set capacity knob
— but it means the ceiling is not purely a burst detector at this planning
rate, and `ceiling_usd` is worth re-sizing at the next re-anchor. What a
mis-set capacity knob does *fast* is mint whole cohorts in single runs: one
unbound long-conference cohort is 148–193 replay-weighted petitions (raw
cohorts reach 369) × 3 predict cells ≈ **$1.1–2.8K in a day**, against a
measured legitimate peak day of ≈$400 — the backstop fires within days of a
runaway burst.

The heaviest legitimate month clears, with limited room: the capped component
is deliberately flattened to ≈ the mean month (the `C` = 60 build-up under the
provider table, ≈$900); the uncapped carve-out band adds $230–290 in a typical
month — unbounded by construction, the one channel that can legitimately run
hot; the steady interim/merits stream is ≈$370; and the one-time merits backlog
drain is small — a dry-run over the committed corpus finds 31 mintable grants
(≈$230–460 with their briefed moments; the un-adjudicated population behind
that measurement is 674 grant-opening rows, which is why the sweep is bounded
rather than trusted). Total ≈$1.75–2.0K, leaving ≈$0.5–0.75K of window for the
lagging ledger.

Two limits it is set *with* rather than against. A ceiling of `0` disables the
backstop (the code default, so a missing section can never wedge the pipeline —
a cost control that wedges when misconfigured is worse than none). And the
ledger **lags** — a cell's `usage.json` reaches `data/` only when its run's
collect PR merges — so the figure it compares is a floor on spend inside the
window, never a live balance.

Two consequences of a breach belong beside the value. Deferral never destroys
queued work, but it can destroy a **claim**: a forward cert cell deferred past
its petition's resolution is permanently outside the headline strata — refused
outright at provisioning where the record already shows the resolution,
re-minted as retrospective where only the clock does, and excluded from every
scored stratum in the mis-provisioned case whose record still claims forward
([metrics/README.md](../metrics/README.md)). A genuine breach trades forward
coverage, which is why the ceiling sits above every legitimate month rather
than at the envelope's average. And the ceiling reads all **committed** spend —
deliberate re-forecast and re-grade campaigns included, money is money by
design — so a large iteration campaign inside one window can itself defer
forward cells; time such campaigns away from conference-dense weeks. The one
iteration surface it cannot see is a cert back-test campaign, whose cells
never reach the ledger (*Backtest campaigns*, below): there the dispatch
itself is the only bound.

#### Monthly spend by provider

The per-case cost splits across the three API bills — one predict cell and one
evaluate cell per provider per case — so at a cadence of `C` tournamented cases
per month each provider's bill is its per-case line × `C`. The Anthropic line
was measured on `claude-fable-5` and carries to the current default unchanged:
the point release holds that rate.

| Provider (engine) | Predict $/case | Evaluate $/case | $/case | Share | At `C` = 60/mo |
|-------------------|---------------:|----------------:|-------:|------:|---------------:|
| Anthropic (`claude-fable-5-1`) | $4.27 | $5.70 | $9.97 | ≈68% | ≈$600 |
| OpenAI (`gpt-5.6-sol`) | $1.88 | $1.25 | $3.13 | ≈21% | ≈$188 |
| Google (`gemini-3.1-pro-preview`) | $0.64 | $0.88 | $1.52 | ≈10% | ≈$91 |
| **Total** | **$6.79** | **$7.84** | **≈$14.6** | | **≈$0.9K** |

(Totals sum unrounded means, so a column can differ from its entries by a
cent. The evaluate column uses the pooled $6.43 anchor — the cautious one; on
the proc-v2 anchor every evaluate entry rises ≈4%.)

The predict column *is* `Σ predict_i` at `P = 3`, and its 6.7× spread is why
*Registry size `P`* treats a fourth predictor's class rather than its existence
as the budget question. The evaluate column is **projected, not measured**: the
pooled pre-freeze cert-stage anchor with the aggregate ≈+22% applied flat to
each engine.

That flat application is the weakest thing in the table, and the data says
which way it is wrong. Engine by engine the predict move was strongly
non-uniform — claude +17%, codex +36%, gemini +17% — so one aggregate factor
over-weights Anthropic and under-weights OpenAI; matching each engine to its
own move gives shares of ≈67% / ≈22% / ≈10%. The two post-freeze evaluate runs,
averaged, measure claude-judge $4.47, codex-judge $1.37, gemini-judge $0.72 —
same direction, larger gap: combined with the predict column, ≈66% / ≈24% /
≈10% against the table's ≈68 / ≈21 / ≈10. So the measured interim rows put the
split ≈3 points off on each of the two large providers, while Google's ≈10% is
stable across all three constructions — the more useful fact. Read that as an
offset, not an error: it rests on six interim gradings under superseded
digests. The flat factor is kept because it is the one the $15 rate is built
from.

**Roughly seven dollars in ten go to Anthropic** on the table's projected
split, nearer two in three on the interim-measured one — size that provider's
spend limit on the larger figure, the conservative one, and expect a limit
breach there to cost a third of a run's coverage (the other engines are billed
independently). The `C` = 60 column is a reference month built from the caps —
the long-conference cycle at its 24-petition cap plus three regular conferences
at 12 (24 + 3 × 12 = 60) — roughly a *mean* Term month, not a peak. At the $15
rate that capped component is ≈$900 (≈$790–810 measured); the floor/CVSG
carve-outs ride above the caps and add on the order of $230–290/month in
relist-heavy months. The caps make the capped component insensitive to the one
cohort whose realized size is not yet observed — the long conference's summer
backlog — though the carve-out channel carries no such bound; both together sit
inside the ≈$12.6–13.0K bootstrapping inference envelope.

#### The qp-topic labeler: the one agentic surface outside the registry

`run-analytics`'s `qp-topic-label` mode runs a single Claude Code session over
one extract of stored questions-presented texts rather than one cell per case —
a manual dispatch, spending only when a maintainer asks for a labeling run,
with the dispatch's `label_model` input defaulting to the cheapest Claude tier
because the task is classification against a fixed sixteen-label vocabulary
rather than forecasting. Its model choices price off the same
`fedcourtsai.pricing.MODEL_RATES` table every cell is quoted from:

| Labeler model | Role | Rate (per 1M tokens) |
|---------------|------|----------------------|
| Haiku 4.5 | the `label_model` default | $1 in / $5 out |
| `claude-sonnet-4-6` | the step-up for a labeling pass the default reads poorly | $3 in / $15 out |
| `claude-fable-5` | the frontier tier the dispatch offers, priced like a predict/evaluate cell's model | $10 in / $50 out |

**Accounting.** Measured qp-topic spend to date is **zero on every ledger**: no
`qp-topic-label` dispatch has produced an artifact yet, and the mode writes no
`usage.json` — the ledger is keyed by cell, and a labeling run is not one — so
a completed run's spend is read off its own engine log until a labeler-shaped
accounting exists. The projected line is bounded rather than measured, and
small: a ceiling-sized run at the default tier lands in **single-digit
dollars** (derivation below), `claude-sonnet-4-6` is 3× the rate and
`claude-fable-5` 10×, putting the top of the range in tens of dollars. Quote
the tier, not a point figure. Because the mode is manual-dispatch-only, its
annual line at any plausible refresh cadence is at most tens of dollars —
carried inside the misc floor's buffer (driver #5) rather than as its own
line, and the first completed run's engine log replaces the estimate. For this
mode the artifact, not the money, is what a mis-sized dispatch loses.

**What one labeling run costs, bounded.** The extract is capped at the
labeling ceiling `fedcourts qp-corpus` enforces (1,200 rows —
`fedcourtsai.pipeline.qp_topics.LABEL_ROW_CEILING`, derived from the labeler
*step's* 40-minute cap, not from the population). Profile of the scoped
extract, measured against the dev blob pulled 2026-08-27 whose newest stored
snapshot is 2026-07-13: 1,187 rows, mean 1,088 characters, median 942, p90
≈1,920, capped at 4,000 — thirteen rows of headroom against the ceiling, so on
the writer lane the guard is expected to fire. (That snapshot stamp bounds the
figure — QP presence is a document-fetch artifact — and the blob's stored
documents predate the corpus split, so it undercounts what the writer lane
holds.) A ceiling-sized run is ≈1.3 MB of question text ≈ 0.33M input tokens
read once (~4 characters a token); what it bills is a multiple of that, and
the multiple is the soft part: the session re-sends context across the
prompt's ~120 turns, so a labeler that streams slices runs a few times the
once-read figure while one that accumulates the whole transcript runs an order
of magnitude above it. Output is roughly 0.1–0.2M tokens. With cache reads at
a tenth of the input rate (cache writes at 1.25×), the default model lands in
single-digit dollars.

The Haiku row is a **known defect**, not a rounding note: `run-analytics`
offers the dated id `claude-haiku-4-5-20251001` (and defaults to it), while
`MODEL_RATES` holds only the undated `claude-haiku-4-5`. The rate is the same,
but `record-usage` refuses an unpriced model — it exits rather than recording a
zero — so the mismatch is latent only because a labeling run writes no
`usage.json` today. Wiring a labeler-shaped accounting up without first
reconciling the two spellings makes the run fail at the recording step.

#### Backtest campaigns: iteration spend off the ledger

The cert back-test (`run-backtest`, [pipeline.md](pipeline.md)) replays
predictors over decided petitions with the outcome hidden — iteration signal,
never claimable performance ([metrics/README.md](../metrics/README.md)). Its
cost model is the predict half alone: ~one cert-stage predict cell per
predictor per replayed petition, scored mechanically against the hidden
outcome, so no evaluate cells at all. A default label-triggered campaign
replays 25 petitions × 3 predictors ≈ 75 cells — **≈$140–170** at the measured
cert per-event rates ($5.57 pre-freeze to $6.66–6.68 on the post-freeze
anchors) — and model spend scales linearly with the dispatch's `--limit`, which
is the campaign's only size cap. The dispatch path defaults to the free
offline `stub` engine, so an accidental dispatch spends nothing; applying the
label is the real-engine spend decision. The salience-gate replay is
deterministic and token-free.

**Accounting.** Campaign cells run under a runner-scratch working tree and are
discarded — only the metrics report lands, via a reviewed PR — so backtest
spend reaches **no committed ledger**: it is invisible to `usage-summary`, to
every measured figure in this document, and to the spend backstop's trailing
window (*The spend backstop*, above). Read a campaign's actual spend off its
own run's engine logs. Measured to date there is nothing to read: no
`metrics/cert-backtest.json` has landed (the committed `metrics/backtest.json`
is the token-free deterministic reference-predictor replay, a different
artifact), and no real-engine campaign's spend is recorded anywhere in-repo. Budget campaigns explicitly when planning an iteration push
— a prompt-tuning series of, say, ten default-sized campaigns is ≈$1.4–1.7K of
provider spend the window never sees — and time them away from
conference-dense weeks for the same reason the backstop paragraph gives for
the campaigns it *can* see.

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
targeted refreshes/day, ≈360 requests) commit about a quarter of the 1,400/day
ceiling, leaving ≈1,000 requests/day of standing headroom for opinion
enrichment and one-off backfills — at Tier 2 the same windows would commit ≈360
of 600, making enrichment and backfills compete with the rotation. The
membership raises the ceiling — the client still throttles to whatever
`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD` are set to, so the tier change
is live only once those variables match the held tier.

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

The raw-fact corpus (a payload-free index plus a per-case content store) lives
in a private S3 bucket ([S3 Standard, us-east-1](https://aws.amazon.com/s3/pricing/):
$0.023/GB-mo storage; egress free for the first 100 GB/mo account-wide, then
$0.09/GB). GitHub-hosted runners are Azure-hosted, so every byte a workflow
reads out of the bucket is S3 internet egress. **Storage** is the retained
index history, which dwarfs the content store enough that the two are carried
as one line (the store itself is unmeasured; it scales with case churn, not run
count). Every push adds an immutable ~1.1 GB object and none is ever removed
(*Index retention: keep every version* in [data-pipeline.md](data-pipeline.md)),
so the index prefix accretes ≈430 GB/mo. The lifecycle transition to Glacier
Instant Retrieval ($0.004/GB-mo) holds only the last 30 days in Standard — a
constant ≈430 GB, ≈$10/mo — and bills everything older at a tenth of that, so
the line rises ≈$2/mo for each further month of history. It is the one floor
component with no asymptote: ≈$10/mo today, ≈$28/mo at a year of history,
≈$48/mo at two (≈$225 over year one, ≈$465 over year two). At a 10 GB blob the
same arithmetic gives ≈$90/mo constant and ≈$16/mo per month.

**Reads** mostly ignore the tier: a pull resolves the current pointer, whose
object is Standard in any ordinary week, since the pointer moves ~13×/day. A
pull of a pinned historical pointer — or of a current one after a writer pause
past 30 days — reads from Glacier IR and pays $0.03/GB retrieval on top of
egress, ≈$0.13 for a full blob; rare and deliberate, by design.
Predict/evaluate cells make ranged point queries (≈10–50 MB and a few hundred
GETs each), so the dominant read term is the **recurring full pulls** by the
scan-shaped writers and analytics — ≈250–300 blob pulls/mo, at today's ≈1.1 GB
blob ≈275–330 GB/mo against a 100 GB account-wide free tier ⇒ ≈$15–20/mo,
scaling linearly with the blob (≈$230/mo at a 10 GB blob, where the lever is
moving those consumers to ranged/incremental reads).

> **Line item: egress ≈$17/mo at today's ≈1.1 GB blob (≈$230/mo at a 10 GB
> blob); storage ≈$10/mo today, ≈$28/mo at a year of retained history.**

### 5. Misc fixed costs — the non-scaling floor

A flat **$350/mo** bucket for the individual-use items carried as one line: the
domains (`modelmirror.ai`, `fedcourts.ai`), the email provider, the **Claude
Max dev subscription** ($200/mo, interactive dev only, never automation — see
driver #1), and other small fixed items — the qp-topic labeler's occasional
dispatch (driver #1) rides inside the buffer too. A deliberate buffer over the
actual items; its defining property is that it **does not scale** with events,
corpus size, or predictor count.

The one recurring *inference* item carried here rather than in driver #1: the
**daily boot canary** — the `engine-actions-smoke` legs of `integration-test`,
one per engine, on a cron. Each leg sends the engine its production invocation
block on a prompt that asks for a single word, so what it buys is an acceptance
check on the invocation path and what it costs is a boot probe: whatever fixed
preamble that CLI loads before the first token of the prompt, plus a short
reply. It belongs in this bucket because it moves with none of the dials driver
#1 does — not `N`, not the corpus, not the number of *predictors* — with one
caveat this bucket's other items do not carry: it is one leg **per engine**, so
it is linear in registry *breadth*. Adding a predictor on an existing engine
costs nothing here; adding an engine adds a probe.

| Engine | Model | ≈ tokens / probe | Rate (in / out per Mtok) | ≈ $/day |
| --- | --- | --- | --- | --- |
| Claude Code | `claude-fable-5-1` | ~20K in (billed as a cache *write*, 1.25×), ~10 out | $10 / $50 | $0.25 |
| Codex | `gpt-5.6-sol` | ~15K in, ~500 out (`effort: high`) | $5 / $30 | $0.09 |
| Gemini | `gemini-3.1-pro-preview` | ~12K in, ~10 out | $2 / $12 | $0.02 |

The model column is what each probe resolves today; the Claude volumes carry
from the measurement on the model before it, per the provenance note above.

That sums to ≈$0.36/day — **≈$0.12/engine/day, so at most ≈$11/mo and ≈$135/yr
at three engines**, "at most" because GitHub drops crons under load and a
skipped window costs nothing. The claude row carries the cache-*creation*
premium and no read discount on purpose: the leg passes the cells'
`ENABLE_PROMPT_CACHING_1H`, and a *daily* cadence against a one-hour TTL never
finds a warm cache, so every probe writes one it will never read.

Treat that as **a bounded tier, not a measurement**, the same way the qp-topic
labeler's line is treated above. Three things it rests on, each of which can
move it:

- **The token counts are estimates.** The canary writes no `usage.json` (there
  is no cell to write one beside), so nothing in the ledger measures it and the
  figure is re-derived from the provider consoles. The preamble's composition
  differs per engine — Claude Code loads `CLAUDE.md` and the `AGENTS.md` it
  imports, codex reads `AGENTS.md` directly, gemini reads neither (no
  `GEMINI.md`, no `contextFileName`) — so `AGENTS.md` growing moves two rows of
  three, and each CLI's own system prompt and tool definitions move all three.
- **The output estimate assumes the probe behaves.** The codex row is the
  softest: reasoning tokens bill at the output rate, and `effort: high` on a
  trivial question is not obviously bounded at 500 — at 2K it is $0.14 rather
  than $0.09. Each leg also runs with the cells' own permissions
  (`bypassPermissions`, `--yolo`, codex's `fedcourts-cell` permission profile
  with network and live search), so "a short reply" is the model obeying *use
  no tools*. The only hard bound is the per-leg
  `timeout-minutes: 10` — and a probe that starts spending it is the same event
  the canary exists to report, so the cost model's assumption fails in the
  instant the canary fires. Read a red canary as a spend signal too.
- **It is outside the spend backstop.** The `$2,500 / 30-day` ceiling above
  reads *measured* cost from the committed `usage.json` ledger, which this line
  never enters — and unlike the other ledger-invisible inference line, which is
  bounded by being manual-dispatch-only, this one spends unattended, up to
  365×/yr. What bounds it is the cron cadence, the three legs the schedule can
  select, and the 10-minute timeout; not `spend.ceiling_usd`.

The same three legs also ride every `scenario=all` dispatch, adding ≈$0.36 to a
promotion suite that already spends three engine-smoke cells' worth — on the
order of $10–20/yr at a plausible 30–50 whole-suite dispatches. Both sit inside
the buffer below, so the floor is unchanged; state them, do not imply them.

> **Line item: $350/mo flat** (a fixed floor, not a variable), the ≈$11/mo
> boot canary inside it.

## Scaling plan: the order of growth

The mid-term plan, stated once as an ordering. Each step is taken roughly to
completion before the next opens, for the same reason the phase policy holds
one dial at a time: every step below changes what the *next* step's spend
buys, so taking them out of order pays full price for a shallower version of
the same artifact. High-level by design — each step gets its own sizing when it
opens, priced by the machinery above.

1. **`N` first: every salient SCOTUS case.** Grow the salience gate's capacity
   until every case and event not deterministically filtered as out-of-scope
   (the IFP/pro-se exclusion and the other `OUT_OF_SCOPE_RULES`) is
   rank-filled — the **full paid-gate coverage** state, ≈$28K/yr inference.
   Coverage claims are claims about `N`, and every later step multiplies over
   the events this one buys. The `interim_reserve_slots` step (5 → 13, ≈+$2.4K)
   belongs at this state's switch point.
2. **Then deepen each event: richer inputs and more moments.** Two moves that
   raise the value of every existing cell before multiplying cells. Enrich
   what predictors and evaluators can read — more per-case documents (briefs,
   appendices) and oral-argument transcripts. And add prediction *moments*:
   new post-filing points where a docket's information set has materially
   changed, and a post-argument moment on the merits track. Both moves touch
   registered seams: enriching what a cell reads moves the retrieval surface
   and prompt bytes the process digests are defined over, re-partitioning the
   record, and a new document channel must enumerate its outcome-revealing
   keys in the snapshot redaction blocklist before a replay can trust it. A
   new moment is a pre-registered population with its own base rate, not a
   config toggle
   ([salience.md](salience.md), [process-version.md](process-version.md)), and
   each adds events at roughly the per-case rate — which is why this step
   follows `N` (the moments multiply over the covered docket) and precedes `P`
   (more engines reading thin inputs buys less than the same engines reading
   rich ones).
3. **Then `P`: more predictors.** In the value-per-dollar order *Registry size
   `P`* derives: ablation variants first, open-weight (Bedrock-hosted) models
   second, additional frontier providers last. The ablation class includes
   **prompt-perspective variants** on the existing registry seam — a predictor
   is an id, an engine, and a prompt, so the same engine can be fielded as,
   e.g., a doctrinal reader instructed to bracket the political posture and
   argue only from the legal materials, a legal-realist counterpart leaning
   into the political and compositional context, or other elicitation
   variants — in the spirit of the automated-researcher framing of Anthropic's
   [automated alignment researchers](https://www.anthropic.com/research/automated-alignment-researchers)
   post (already cited for this registry seam in `README.md`): differently-framed
   agents attacking the same question, ranked by the tournament. Each variant
   partitions from its parent under its own process digest, so the comparison
   is attributable by construction.

`E` holds at 3 throughout, and widening past the SCOTUS gate stays where
*Deferred scope, unpriced* leaves it — after the `P` dial is spent, at the
~1-year decision point. The releases this ordering feeds are in
[milestones.md](milestones.md).

## Deferred scope, unpriced

Two expansions are named here so they are not read as omissions. Both are
deliberately carried **without figures**, and neither is on the scaling path
above.

**Widening past the SCOTUS-docket gate.** Predicting the originating courts of
appeals, or a rotating appeals sample, is the ~1-year scope decision in
[milestones.md](milestones.md) — held open until a Term of cost and calibration
data is in hand, alongside the academic / B2B / public-artifact fork. The
14-court reference ceiling under driver #1 sizes that decision's extreme at
`P = E = 3`; nothing between today's gate and that extreme is planned or
costed. Under the phase policy the `P` dial is spent out **before** a scope
widening is considered at all — breadth of forecast comes before breadth of
docket. A scope change is also not a pure budget question: cross-court figures
are not comparable, so widening buys events at the cost of a pooled population
([salience.md](salience.md)).

**Free Law Project's partnership-gated services.** Three ingestion upgrades
wait on an established relationship with Free Law Project rather than on
engineering ([milestones.md](milestones.md); *The planned end-state* in
[data-pipeline.md](data-pipeline.md)): a hosted Postgres **replica** under
FLP's replication agreement, docket-alert **webhooks**, and **opinion bodies
served from the replica**. They stay qualitative and unpriced, pending Free Law
Project's terms — the only CourtListener figures in this document are the
public membership tiers under driver #2, and the pilot's funded line stays
Tier 4. Two of the three are also not cost-justified at the current scope: the
replica buys freedom from request caps that do not bind (the live channel owns
SCOTUS freshness at $0 and Tier 4 leaves ≈1,000 requests/day of headroom), and
webhooks replace polling that is already free where it matters. All three
become live questions at the scope decision, not before.

## Summary: the scenario ladder

The non-inference lines — misc floor ($350/mo), CourtListener ($1,000/yr), S3
(≈$28/mo today), Codespaces ($0–50/mo on a free allowance), Actions ($0) — sum
to the **≈$5.5K/yr floor** (`$28 × 12 + $4,200 + $1,000 = $5,536`, Codespaces
at $0). "Floor" means it moves with neither `N` nor `P`, not that it is
constant: retained history ratchets the S3 term ≈$0.25K a year (driver #4).
Everything above it is inference `= events(N) × per-case(P)`. `N` moves the
cert rank fill — much the largest single channel — while **343 events ride
beside it**, unbought by `N`: 20 CVSG re-forecasts and the ~98-case arrival
cohort (cert-stage but not `N`'s), ~98 interim (bounded by
`interim_reserve_slots`), ~127 merits (every granted petition, whatever `N`
is). `P` moves the rate every one of those events is priced at. So a scenario
states both dials.

Where a row shows two figures, the first is the **planning basis** ($15 a case,
the rate to fund against) and the second the **measured basis**, which
extrapolates a Term from the six-interim-event measurement (*Evaluate cost*,
above) — it answers "what if a Term were interim moments all the way down",
which it is not. Fund on the first column; read the second as the open
question.

| Scenario | ≈ Annual (planning · measured†) | Inference (= total − ≈$5.5K floor) | Dials |
|----------|----------|----------------------------------|-------|
| Bootstrapping | ≈$18.5K · ≈$17K | ≈$13K · ≈$11–12K | `N` = capacity 12 (long conference 24), `P` = 3: a whole OT2026 Term of ≈838–865 events across all three stages |
| Full paid-gate coverage — **the dial switch** | ≈$33K · ≈$30K | ≈$28K · ≈$24–25K | `N` at its ceiling, `P` = 3: all 1,498 paid petitions rank-filled plus the 343 beside-`N` events = 1,841 (an upper bound) |
| Initial funding | ≈$100K | ≈$94.5K | Full coverage at `P` = 3, remainder on `P`: a registry of roughly 8–13 engines (planning basis) |
| Well funded | ≈$1M | ≈$994.5K | Either dial taken far; the band in which the deferred scope decision first becomes affordable |
| **Floor (all scenarios)** | **≈$5.5K** | **—** | scales with neither dial; the S3 term still ratchets ≈$0.25K/yr |

† Measured-basis figures inherit the six-interim-event caveat above. The
Initial-funding and Well-funded rows carry one figure because they are funding
levels rather than derived costs.

Notes on the rows, once each:

- **Bootstrapping** funds the events the gate replay measures at the shipped
  caps — 613–640 cert (495–522 replay-selected plus CVSG and the arrival
  cohort), ~98 interim, ~127 merits — keeping 0.76–0.81 of the Term's
  replay-reconstructable grant-family outcomes (0.80–0.84 of selectable ones),
  mostly via the carve-out band; a capacity of 150 keeps 0.944–0.967 (measured,
  same pool) and would cost ≈$24K. All replay figures are sal-v1, a lower bound
  for the active sal-v4 gate (*Measured volumes*).
- **At the dial switch**, `N` can buy nothing further, so salience survives as
  the public ranking and the replay story rather than as a spend control
  ([salience.md](salience.md)). Incremental dollars move to `P` — or, cheaper,
  to `interim_reserve_slots` first: ≈$2.4K buys ~157 more interim events, an
  alternative to the first `P` increment rather than something taken alongside
  it (the `P` arithmetic prices engines over 1,841 events, the count *before*
  any reserve step).
- **Initial funding** puts ≈$66.5K (planning basis; ≈$70.5K measured) on `P`
  after full coverage: each added predictor costs `1,841 × (p + m)` a year — at
  the top of the `m` band, ≈$12.9K planning / ≈$12.0K measured for a
  frontier-class engine, ≈$6.2K / ≈$5.3K for an ablation- or open-weight-class
  one — funding roughly 8–13 engines on the planning basis, 8–16 on the
  measured one. Read it as "many more than four", not a target: it extrapolates
  the fully-linear `m` bound far past any run yet produced.
- **Full cert coverage sits well inside the initial-funding step** — the switch
  row is about a third of it — which is why salience-as-spend-control is a
  *bootstrapping* argument specifically. The second half of that step is not
  more coverage but more opinions per event, and the cheapest useful `P` is an
  ablation of an engine already in the registry rather than a fourth frontier
  bill.

Start at **bootstrapping** with a small `N` and `P` = 3, let the ledger keep
measuring real per-case cost against the ≈$15 planning rate, then raise `N` as
funding lifts it, and `P` once `N` is spent — the *Scaling plan* above, with
`E` at 3 throughout. The funding path to each state — credit programs and
external support — is tracked in [milestones.md](milestones.md).
