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
is that fixed floor plus one dominant line, and that line has a single dial — the
salience gate's **capacity `N`**, the number of petitions per conference the
tournament actually runs. Funding moves `N`; the whole budget re-cuts as
`fixed floor + N × per-case`.

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
| Interim — substantive applications | 219 | 15.5% of the 1,410 parsed application dockets; 80.4% are extensions and 4.1% unreadable asks |

**A case is forecast more than once.** Each stage asks one question and the case
passes several points at which it can honestly be forecast, each with a
different information set. The moments are separate events, separately scored
and never pooled ([salience.md](salience.md)); each costs one fully-tournamented
case-equivalent.

| Stage | Moment | Events / Term | Coverage of the stage |
|---|---|---:|---|
| cert | first distribution | 495–522 | measured at `per_conference_capacity: 12` by the OT2022–24 gate replay **under sal-v1** — a lower bound for the active sal-v2 gate, whose federal carve-in also reaches conference cohorts (≤ ~14/Term more; unmeasured until a sal-v2 replay refresh): rank fill 398–413 (cumulative through resolution; 380–386 at first distribution) plus uncapped carve-outs 97–115 (below) |
| cert | CVSG | 20 | 1.33% of paid petitions — but 7.0% of the paid census's grants |
| cert | arrival | 95 | the sal-v2 arrival cohort, **beside** `N`, filling forward from the registration-fixed cohort start (the OT2026 docket-year roll — the standing pending backlog never enters): 75 from the 1-in-20 deterministic random slice over ~1,500 paid arrivals (`salience.arrival_sample_rate`) + ~20 from the federal-petitioner carve-in, whose census run passed statistical verification (8/8 complete Terms at 8.1–16.4× lift; per-Term 11–40, so a heavy government-litigation Term runs high; ~14/Term incremental over what CVSG/floor already carve — `docs/salience.md`) |
| interim | arrival | 67 | 5 reserve slots turning over at a 27.1-day mean occupancy |
| interim | response requested | 8 | 12.3% of the 67 selected arrivals |
| interim | response filed | 21 | 30.6% of the 67 |
| merits | grant | 65 | **every** granted petition — the gate is bypassed at this stage |
| merits | briefed | 62 | 96.4% of the 65 grants reach a respondent merits brief, rounded down |
| | **total** | **833–860** | **≈$10.8–11.2K/Term** at the $13 planning rate, arrival slice + carve-in included (≈$11.4K at the bound if the federal carve-in's conference-cohort reach adds its full ~14) |

The later moments differ sharply in how much runway they leave, which is the
figure to read before trusting any of their skill numbers: a merits brief
precedes the judgment by a median 159 days (minimum 44), a requested interim
response by a median 17 (minimum 3), and a *filed* interim response by a median
of only 2 — so a material share of that last moment's cells will classify
retrospective on commit latency alone.

The interim rows carry two selection biases, in opposite directions. The
reserve's ladder orders on response-requested first, so the selected 67 are
enriched in exactly the property the 12.3% rates — read the 8 as biased low
for the selected slice, bounded above by the 67. And the 67 itself divides
slot turnover by the stream's 27.1-day mean occupancy, while the ladder
plausibly favors longer-lived applications (p95 110 days), which would cut
arrivals below 67.

Two denominators are easy to confuse. The **≈5,500** the gate is priced on below
counts cert decisions across both fee streams; the gate excludes IFP at Tier 0
([salience.md](salience.md)), so the pool it can ever select from is at most the
**1,498** paid petitions — an upper bound, because seven further rules in
`OUT_OF_SCOPE_RULES` cut it again, as does the snapshot-aware bare-import rule
that `out_of_scope_reason_full` adds. So the ≈$70K below is the whole-docket
ceiling, and full coverage of what the gate can actually predict is
`1,498 × 6 cells × $2.12 ≈ $19K`.

**The cap is sized to bind, and the gate replay at the shipped capacity
measures that it does.** Raw paid cohorts run a median 34 petitions (p90 82,
max 369); the pool the replay ranks — replay-reconstructable resolved paid
petitions, 1,239–1,358 a Term — runs a mean conference cohort of ~37, and at
`per_conference_capacity: 12` the cap binds **29 of each Term's 33–36
reconstructable first-distribution cohorts** across OT2022–24
(`metrics/salience-replay.json`). The comparison that sized it: a
`per_conference_capacity` of 150 would cut just **8 of 251** raw
cohorts and exclude 5.3% of petitions — selecting **~95%** of the paid docket
and funding ~$21K/Term, a ranking rather than a spend control. The shipped
`12` (long conference `24`) measures at **495–522 selected petitions a Term**
across OT2022–24: rank fill 380–386 at first distribution and 398–413
cumulative through resolution, plus floor/CVSG carve-outs of 97–115 riding
*above* `N` uncapped — landing the escalation program at ≈$9.6–9.9K at the planning
rate (≈$10.8–11.2K with the sal-v2 arrival cohort — the moments
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
days (median 13, p95 110), so 219 arrivals need ≈16 concurrent slots against
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
`date_decided` columns, which are null on 57 of the 219 rows and null
disproportionately on the long-lived ones; the entry-based measure covers 218,
the exception being the one application still pending. And OT2025 is open, so
the arrival count is a partial year divided into a full-year denominator —
saturation is understated, not overstated.

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
**≈$767 total inference spend on the ledger to date**, across the 413 cells the
per-cell figures below draw on.
That estimate is token-derived, so hosted web search — billed per call rather
than per token on all three APIs — sits outside it and makes a searching cell's
recorded cost a mild undercount.
Measured per-cell cost spans **≈$0.25–7.87 by model mix** (blended mean **≈$1.86**
over the 413 cells on the ledger — predict: claude-baseline ≈$3.65, codex ≈$1.38,
gemini ≈$0.55; evaluate, from the one graded event: claude-judge ≈$4.16, codex-judge
≈$0.92, gemini-judge ≈$0.52); the cheapest cells approach ≈$0.25 only when the
byte-stable prefix (AGENTS.md + prompt template + schema) is served from the prompt
cache — automatic on all three engines, billing cached reads at ≈0.1×, and the
reason to keep that prefix stable. Budget the range, not the point. The evaluate
means come from a single event, so treat them as a first measurement rather than a
settled figure; the planning rate below is held deliberately above both.

**One agentic surface sits outside the registry**, and outside the per-cell
accounting above: `run-analytics`'s `qp-topic-label` mode, which runs a single
Claude Code session over the whole extract of stored questions-presented texts
(roughly 1,200 at current coverage) rather than one cell per case. It is a
manual dispatch, not a scheduled or cascade-triggered job, so it spends only
when a maintainer asks for a labeling run; its model is the dispatch's
`label_model` input, defaulting to the cheapest Claude tier because the task is
classification against a fixed sixteen-label vocabulary rather than forecasting.
It writes no `usage.json` — the ledger is keyed by cell, and a labeling run is
not one — so its spend does not appear in the totals above and has to be read
off the run's own engine log until a labeler-shaped accounting exists.

**Scope: the SCOTUS-docket gate.** The pilot predicts and evaluates only SCOTUS
dockets. Ingestion is unchanged — the channels still assemble all fourteen courts
deterministically (≈$0 model spend) so the full history stays queryable for
retrieval and back-testing; only the agentic stages are gated.

The unit throughout is the **agent cell**, and both roles fan out the same way:
one predict cell per (predictor, event) and one evaluate cell per (evaluator,
event) — a judge grades *every* predictor for its event in a single invocation,
so cross-evaluation multiplies the `evaluation.json` count but not the cell
count. Three engines cross-evaluated is therefore **6 cells per case**, not 12.

Full 14-court scope is the reference ceiling:

```
predictions  ≈ 48,000 events   × 3 predictors × $2.12   ≈ $305K
evaluations  ≈ 42,000 resolved × 3 evaluators × $2.12   ≈ $267K
                                                          ────────
full scope                                                ≈ $570K / yr
```

The SCOTUS gate is roughly 1/8 of that — ≈5,500 cert decisions per term:

```
predict   ≈ 5,500 × 3 × $2.12   ≈ $35K
evaluate  ≈ 5,500 × 3 × $2.12   ≈ $35K
                                 ───────
full cert gate                   ≈ $70K / yr
```

That is the whole-docket ceiling, both fee streams. The gate never selects an
IFP petition, so the figure to fund full coverage of what it *can* predict is
the paid pool: `1,498 × ≈$13 ≈ $19K / yr` (see *What there is to predict: measured volumes*).

**Capacity `N`: the funding knob.** Within the gate, [salience.md](salience.md)'s
capacity `N` bounds *how many* — the tournament runs on the top-`N` salient
petitions per conference plus a few always-include carve-outs, so inference spend
is `N × per-case`. One fully-tournamented case:

```
predict:   3 predictor cells × $2.12 = $6.36
evaluate:  3 evaluator cells × $2.12 = $6.36
                                       ──────
per case ≈ $13   (planning rate, three engines cross-evaluated)
```

`$2.12` is a **deliberately conservative** per-cell rate, held above the current
measured blended mean of `$1.86` (413 cells) so the knob does not have to be
re-cut every time the ledger grows. Priced at today's measured per-engine means
the same case is **≈$11** — predict `$5.58` (claude `$3.65` + codex `$1.38` +
gemini `$0.55`) plus evaluate `$5.60` (claude `$4.16` + codex `$0.92` + gemini
`$0.52`). Treat `$13` as the number to fund against and `$11` as the number to
expect; the evaluate half rests on a single graded event, so it is indicative
rather than settled, and the gap is the margin.

So `N ≈ inference_budget / (≈$13 per fully-tournamented case)`. Tier-1 salience
scoring is itself ≈$0 (a deterministic pure function of corpus features, no model
call), so the gate spends nothing to *decide* what the tournament runs on. Raising
`N` deepens the salience-ranked slice; it never reshuffles the ranking.

**The interim docket: a quota'd stream, capped at five cases in flight.**
[salience.md](salience.md)'s interim-docket section carries a second selection
problem — stays, injunctions, vacaturs pending certiorari — and the quota is what
keeps it small. Across the 1,410 parsed application dockets of the walked
OT2025 Term, **80.4%** are
time-extension requests and **4.1%** carry an ask the parser cannot read; both
are filtered out deterministically by
`interim_signals.is_predictable_application` (≈$0, no model call), leaving the
**15.5%** substantive slice as the only population ever predicted. The stream is
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
five interim cells are ever in flight, against the ≈16 substantive applications
live at any moment, and an unfilled reserve costs nothing. The slice
is predicted but not
yet skill-scored: the interim segment base rate publishes only at the
pre-registered resolved-count floor ([salience.md](salience.md)).

**The merits docket: a second cell on a case already funded, unbounded by
design.** A cert grant opens a merits event
([decision-model.md](decision-model.md)), and that event is forecastable, so a
granted docket buys one more predict cell per predictor and one more evaluate
cell when the judgment lands — roughly a second `≈$13` case-equivalent where
the gate funded the cert cell, which at the projected ~80% grant coverage is
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

The shipped value is **$2,500 over a 30-day trailing window** — ~2.1× the
Term's average month (≈$1.2K: the 833–860 events/Term at the $13
planning rate, spread over the ~9 months the Term spans; on a 12-month spread
the multiple is 2.8×, so the claim is conservative). What it protects against
is a **burst, not a rate**. The steady state cannot reach it: even a
regression to a non-binding cap burns $1.8–2.3K per 30 days (the prior
150/200 replay selected 1,228–1,349/Term ≈ $16–17.5K, and the 150-cap
scenario above funds ≈$21K/Term), a trailing sum that asymptotes *below* the
ceiling. What a mis-set capacity knob actually does is mint whole cohorts in
single runs: one unbound long-conference cohort is 148–193 replay-weighted
petitions (raw cohorts reach 369) × 3 predict cells ≈ **$0.9–2.3K in a day**,
against a measured legitimate peak day of ≈$400 — so the backstop fires
within days of a runaway burst and stays silent through any legitimate month.
The heaviest legitimate month clears with room: the capped component is
deliberately flattened to ≈ the mean month (the `C` = 60 build-up below,
≈$780), the **uncapped** carve-out band adds $200–250 in a typical month
(unbounded by construction — the one channel that can legitimately run hot),
the steady interim/merits stream ≈$320, and the one-time merits backlog drain
is small — a dry-run over the committed corpus finds **31 mintable grants**
(≈$200–400 with their briefed moments; the un-adjudicated population behind
that measurement is 674 grant-opening rows, which is why the sweep is bounded
rather than trusted) — totalling ≈$1.55–1.75K, which leaves ≈$0.8–0.95K of
window for the lagging ledger.
Two limits it is set *with* rather than against. A ceiling of `0` disables
the backstop (the code default, so a missing section can never wedge the
pipeline — a cost control that wedges when misconfigured is worse than none).
And the ledger **lags** — a cell's `usage.json` reaches `data/`
only when its run's collect PR merges — so the figure it compares is a *floor* on
spend inside the window, never a live balance.
Two consequences of a breach belong beside the value. Deferral never destroys
queued work, but it can destroy a **claim**: a forward cert cell deferred past
its petition's resolution re-mints as a retrospective cell
([`metrics/README.md`](../metrics/README.md)), permanently outside the
headline strata — a genuine breach trades forward coverage, which is why the
ceiling sits above every legitimate month rather than at the envelope's
average. And the ceiling reads **all** measured spend, replay and backtest
campaigns included — money is money by design — so a large iteration campaign
inside one window can itself defer forward cells; time such campaigns away
from conference-dense weeks.

**Monthly spend by provider.** The per-case cost splits across the three API
bills — one predict cell and one evaluate cell per provider per case, both
columns measured — so at a cadence of `C` tournamented cases per month each
provider's bill is its per-case line × `C`:

| Provider (engine) | Predict $/case | Evaluate $/case | $/case | Share | At `C` = 60/mo |
|-------------------|---------------:|----------------:|-------:|------:|---------------:|
| Anthropic (`claude-fable-5`) | $3.65 | $4.16 | $7.81 | ≈70% | ≈$470 |
| OpenAI (`gpt-5.6-sol`) | $1.38 | $0.92 | $2.30 | ≈21% | ≈$140 |
| Google (`gemini-3.1-pro-preview`) | $0.55 | $0.52 | $1.07 | ≈10% | ≈$64 |
| **Total** | **$5.58** | **$5.60** | **≈$11** | | **≈$0.7K** |

The predict column rests on 138 / 132 / 140 cells per engine and is solid; the
evaluate column is one graded event, so read it as a first measurement. Roughly
**seven dollars in ten go to Anthropic** — size that provider's spend limit
accordingly, and expect a limit breach there to cost a third of a run's coverage
(the other engines are billed independently). The `C` = 60 column is a
reference month built from the caps — the long-conference cycle at its
24-petition cap plus three regular conferences at the 12 cap (24 + 3 × 12 =
60; `C` counts cases per month) — roughly a *mean* Term month, not a peak. At
the $13 planning rate that capped component is ≈60 × $13 ≈ **$780** (≈$660
measured); the floor/CVSG carve-outs ride above the caps and add on the order
of $200–250/month at the planning rate in relist-heavy months. The caps make
the capped component insensitive to the one cohort whose realized size is not
yet observed — the long conference's summer backlog — though the carve-out
channel carries no such bound; both together sit comfortably inside the ≈$11K
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

## Summary: scaling `N` with funding

The non-inference lines — misc floor ($350/mo), CourtListener ($1,000/yr), S3
(≈$15/mo, the one line that grows with the corpus blob), Codespaces ($0–50/mo),
Actions ($0) — sum to a near-constant **≈$5.5K/yr floor**. Everything
above it is inference `= events × per-case`, and `N` is the dial that moves the
cert stage — much the largest of the three. The other stages scale on the
Court's own volume rather than on funding: every granted petition is forecast at
the merits stage whatever `N` is, and the interim stream is bounded by
`interim_reserve_slots`. So a scenario is read as "how much of the *cert* docket,
plus a fixed ~220 events from the other two":

| Scenario | ≈ Annual | Inference (= total − ≈$5.5K floor) | Reach |
|----------|----------|----------------------------------|-------|
| Bootstrapping | ≈$16.5K | ≈$11K | ≈833–860 forecast events across all three stages, sal-v2 arrival cohort included — a **whole OT2026 Term**, not a slice of one: 610–637 cert (`per_conference_capacity: 12`, long conference 24; the OT2022–24 gate replay measures 495–522 selected a Term — rank fill plus uncapped carve-outs — plus 20 CVSG re-forecasts and the ~95-case arrival cohort), ~96 interim, ~127 merits. Keeps 0.76–0.81 of the Term's replay-reconstructable grant-family outcomes (0.80–0.84 of selectable ones), mostly via the carve-out band; a cap of 150 keeps 0.944–0.967 (measured, same pool) and would cost ≈$21K |
| Initial funding | ≈$100K | ≈$95K | ≈7,500 cases — comfortably past the ≈5,500-event whole-docket ceiling (≈$70K uncapped), and several times the ≈1,498 paid petitions the gate can actually select (≈$19K). The cert term is fully covered here, so salience is already a public ranking rather than a spend control |
| Well funded | ≈$1M | ≈$995K | covers all-14-court full scope outright (every event, ≈$570K), with room for deeper panels or more engines |
| **Floor (all scenarios)** | **≈$5.5K** | **—** | **misc + CourtListener + S3 + Actions; does not scale with `N`** |

The ladder is shorter than it looks: the corrected cell count puts **full cert
coverage inside the initial-funding step**, not beyond it. That makes the case for
salience-as-spend-control a *bootstrapping* argument specifically — above that
step it survives as the public ranking and the replay story, which is how
[salience.md](salience.md) frames it.

Start at **bootstrapping** with a small `N`, let the ledger keep measuring real
per-case cost against the ≈$13 planning rate, then raise `N` as funding lifts it. The funding path
to each state — credit programs and external support — is tracked in
[milestones.md](milestones.md).
