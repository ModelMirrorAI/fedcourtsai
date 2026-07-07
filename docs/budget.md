# Budget

Projected costs to **seed** the corpus with all historical Supreme Court and
courts-of-appeals cases, keep it current with daily **pull**, and run
**predict**/**evaluate** regularly across all fourteen courts. This is a
forecast, not a spending cap: it sizes each cost driver so scope and cadence can
be chosen with the bill in view. For how the phases work, see
[data-pipeline.md](data-pipeline.md) and [pipeline.md](pipeline.md).

All prices are USD, captured mid-2026; treat them as a snapshot and re-check the
linked sources before committing spend. The repo is **public**, so all figures
assume the free public-repo Actions tier, and all model inference is priced on
the **on-demand API** (the pipeline does not use the Batch API today).

## The one thing that matters: inference dominates

Every other line in this budget — runners, storage, API memberships,
subscriptions — sums to a few hundred dollars a month. **Agentic model usage for
prediction and evaluation is one to two orders of magnitude larger** and scales
linearly with how many events are predicted, by how many predictors, scored by
how many evaluators. At full scope it is the entire budget; everything else is
rounding error. So the controlling decisions are *how many events we predict* and
*with how many competing agents* — not which runner tier or storage class we pick.

A second consequence: the flat **Claude Max** subscription cannot absorb
full-scope volume. The subscription is metered by rolling 5-hour and weekly
limits intended for interactive use, and per Anthropic's policy the subscription
OAuth token is meant for Claude Code / claude.ai, not automated CI/CD — they
direct automation at a pay-per-token API key. So the subscription is the right
tool for **development and low-volume piloting**, while sustained pipeline
inference is an **API-metered** cost. The pipeline reflects both modes: interactive
development uses the Max subscription, and every automated stage (`run:predict`,
`run:evaluate`, `run:reconcile`, `run:dev`) authenticates to Claude via the
Anthropic **API key**.

## Cost drivers

### 1. Model usage (the dominant cost)

Three engines run the agentic stages, routed per registry entry
([config/predictors.yaml](../config/predictors.yaml),
[config/evaluators.yaml](../config/evaluators.yaml)):

| Engine | Used by | Billing | Rate (per 1M tokens) |
|--------|---------|---------|----------------------|
| **Claude Code** (`claude-fable-5`) | `claude-baseline`, `claude-judge` (predict/evaluate default) | Anthropic API (workflows); Max subscription for interactive local dev | Subscription: **$200/mo** flat (Max 20x). API: **$10 in / $50 out** |
| **Claude Code** (`claude-opus-4-8`) | all `run:dev`, `run:reconcile` | Anthropic API (workflows) | **$5 in / $25 out** |
| **Codex** (`gpt-5.5`) | `codex-baseline`, `codex-judge` | OpenAI API (pay-per-token) | **$5 in / $30 out** |
| **Gemini** (`gemini-3.1-pro-preview`) | `gemini-baseline`, `gemini-judge` | Gemini API (pay-per-token) | **$2 in / $12 out** (≤200K context) |

Sources: [Claude Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan),
[Claude API pricing](https://platform.claude.com/docs/en/pricing),
[OpenAI API pricing](https://developers.openai.com/api/docs/pricing),
[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

**Per-run cost.** A single predict or evaluate run is an *agentic* job: the agent
reads the prompt, AGENTS.md, the case snapshot, and a handful of retrieved
priors, then writes its artifacts over several tool-use turns. Effective token
usage is therefore much larger than the visible artifacts — roughly **~280–400K
effective input (the large majority served from cache) + ~6K output per run**.

This was once a planning assumption (~$1–2/run); it is now **measured**. Every
predict/evaluate run records its tokens and an estimated cost (at the rates in
this section, kept in `fedcourtsai.pricing`) to a `usage.json` beside its output,
and `fedcourts usage-summary` rolls those up. Across the 82 predict runs to date
(41 per predictor) the cost holds at **≈ $0.50/run** (claude-baseline ~$0.42,
codex-baseline ~$0.56) — roughly a third of the old assumption, because prompt
caching on the stable prefix is working as designed. **Caveats:** this is the
*predict* figure; no event has resolved yet, so **evaluate per-run cost is still
unmeasured**, and **Gemini is newly added and has not yet run**, so its per-run
cost is unmeasured too. The estimates below assume both are comparable (~$0.50)
and should be re-checked against the first real evaluations and Gemini runs —
Gemini's lower token rate ($2/$12 vs Codex $5/$30) makes a flat $0.50 a
conservative ceiling for its share. **Caveat (2026-07):** the measured
claude-baseline figure (~$0.42) was earned on `claude-opus-4-8` ($5/$25);
predict/evaluate now default to `claude-fable-5` ($10/$50), so expect the
Claude share to roughly double (~$0.85/run) until re-measured — re-check
`fedcourts usage-summary` after the first Fable runs.

That ≈ $0.50/run is an **on-demand** figure; one discount produces it:

- **Prompt caching** — automatic on all three engines. The stable prefix (AGENTS.md +
  the prompt template + schema) is byte-identical across runs and is read before
  any per-case facts, so it is served from cache across a run's many tool-use
  turns; cached reads bill at ~0.1× and cache writes at ~1.25× (both in
  `fedcourtsai.pricing`, and recorded per run in `usage.json`). Keep that prefix
  byte-stable to capture it. The predict and evaluate workflows request the
  1-hour cache TTL explicitly: the agentic workflows run against the Anthropic API
  (whose default TTL is only 5 minutes), so the longer TTL keeps the prefix cached
  across a run's tool-use turns; the same 1-hour TTL is free on the Claude Max
  subscription used for interactive dev.

Live pull-triggered predictions are latency-sensitive and run on-demand. The
**Batch API** (50% off, non-latency-sensitive) is not used today; it remains an
available lever for back-testing / bulk re-scoring (see *Levers*).

**Volume.** Scope is all fourteen courts. The courts of appeals terminate
**~42K cases/yr** (~41K filed; [Judicial Business 2025, Table B](https://www.uscourts.gov/data-news/reports/statistical-reports/judicial-business-united-states-courts/judicial-business-2025/us-courts-appeals-judicial-business-2025)),
and SCOTUS docket activity adds **~5K cases/term** with **~70 cert grants**
([SCOTUS Table A-1](https://www.uscourts.gov/sites/default/files/2025-01/supcourt_a1_0930.2024.pdf)).
At roughly one baseline predictable event per docket that is **~45–50K events/yr
≈ ~130/day**.

**Pull cadence does not multiply this.** Pull now runs four windows a day and each
window that finds changed cases files a `run:predict`, so predictions are spread
across up to four runs daily rather than one — but the annual *event* count is the
cost driver, not the number of pull windows. `predict_on_change_only` predicts an
open event once and re-predicts only when the case's facts actually change, so a
higher pull cadence improves freshness/latency without re-billing unchanged cases.
The only second-order cost is an event whose case changes in more than one window
on the same day (predicted more than once); under the SCOTUS gate this is a small
tail, not a multiplier.

**Annual inference at full scope** (every event, all three predictors, all three
evaluators, on-demand), using the model below:

```
predictions  = events/yr × predictors × $/run
evaluations  = resolved_events/yr × (evaluators × predictors) × $/run

≈ 48,000 × 3 × $0.50      ≈ $72K    predictions
≈ 42,000 × (3×3) × $0.50  ≈ $189K   evaluations
                           ───────
                           ≈ $261K / yr   (≈ $22K / mo)
```

That figure is still large: it is what "predict and evaluate *everything, with
everything*" costs, and it is why the levers below exist. Even so, full scope
remains far above all other costs combined, so the prediction *slice* and engine
fan-out stay the controlling decisions.

**Levers** (each is independent; combine them):

| Lever | Effect |
|-------|--------|
| **Gate the prediction scope** — predict only cases that have interacted with SCOTUS (the pilot gate; see below) rather than every event | Linear cut; the biggest dial |
| **One engine per stage** instead of three competing | ~67% predict, more on evaluate (which scales with evaluators × predictors) |
| **Cheaper competitor model** — run one predictor on `claude-haiku-4-5` ($1/$5) or `claude-sonnet-4-6` ($3/$15) | Large cut on that predictor |
| **Batch API** for back-testing / bulk re-scoring (not used today) | ~50% on eligible work |
| **Prompt caching** on the stable prefix (already on) | Up to ~90% of the input portion |
| **`predict_on_change_only`** (already set) | Avoids re-predicting unchanged cases |

The controlling choices are the first two rows: the prediction *slice* and the
engine fan-out. The pilot fixes them explicitly with the SCOTUS-interaction gate
below.

#### The pilot slice: cases that touch SCOTUS

Rather than a fixed sample, the pilot bounds spend with a **gate**: a case becomes
in-scope for predict/evaluate the first time it interacts with the Supreme Court — a
petition for certiorari is the canonical trigger — and stays in-scope for the rest of
its lifecycle, so a granted case's merits events and any remand activity back in the
courts of appeals are covered, while the ~42K/yr appeals cases that never reach
SCOTUS are not. Ingestion is unchanged: seed and pull still assemble all fourteen
courts (deterministic, ~$0 model spend) so the full history stays queryable for
retrieval and back-testing — only the agentic stages are gated. See the prediction
scope in [data-pipeline.md](data-pipeline.md).

The gate is dominated by the cert docket — **~5–6K petitions/term**, each a cert
grant/deny event — plus the ~70–80 merits cases and their downstream events:

```
gated_events/yr ≈ ~5.5K cert decisions + a merits tail
predictions ≈ 5,500 × 3 × $0.50      ≈ $8K
evaluations ≈ 5,500 × (3×3) × $0.50  ≈ $25K
                                      ───────
                                      ≈ $33K / yr   — roughly 1/8 of full scope
```

and it tunes far below that for the first release. The **long-conference batch**
is ~2,000 petitions resolved in one sitting. Sized at the measured ~$0.50/run
on-demand, the head-to-head release the milestones describe (all three predictors,
cross-evaluated, same matrix as the figures above) is predict — 2,000 × 3 ≈ **$3K**
— plus evaluate once the opening order list resolves them — 2,000 × (3×3) ≈ **$9K**
— on the order of **$12–13K for the entire batch** with rerun headroom. A
deliberately lean **single-engine** first release (one predictor, one evaluator)
would instead be ~$2K predict + evaluate, on the order of **$2–3K**. Either is the
entry point the OT2026 cert mini-release is sized against; the steady-state gate
above is where it grows next, still an order of magnitude under full scope.

### 2. CourtListener API (membership for pull throughput)

**Seed** reads CourtListener's free quarterly **bulk** snapshots (public S3,
`--no-sign-request`) — **$0**, no rate limit. The historical mass costs nothing
in API terms.

**Pull** spends the rate-limited REST budget. Since May 2026 the free default is
**5/min · 50/hr · 125/day** (~30–40 dockets/day at ~3 requests each), and higher
throughput is a paid Free Law Project membership
([free.law/membership](https://free.law/membership/)):

| Tier | Price | Limits (min / hr / day) | ≈ dockets/day |
|------|-------|--------------------------|---------------|
| Free | $0 | 5 / 50 / 125 | ~40 |
| Tier 2 | $25/mo ($250/yr) | 15 / 150 / 600 | ~200 |
| Tier 3 | $50/mo ($500/yr) | 20 / 250 / 1,000 | ~330 |
| Tier 4 | $100/mo ($1,000/yr) | 25 / 300 / 1,400 | ~460 |

At all-fourteen-courts scope, new appellate filings alone run **~120/day**, so
the free tier cannot keep the live frontier current and also refresh the active
set. **Tier 3 ($50/mo) is the recommended floor** (covers new filings plus a
healthy refresh rotation); **Tier 4 ($100/mo)** buys comfortable headroom as the
tracked set grows. Above Tier 4 is a custom commercial agreement (unpublished).

The **pilot currently holds Tier 2 ($250/yr, billed annually)**. Pull runs four windows a day, each
refreshing up to `max_cases_per_run` (30) dockets and discovering new filings — so
~120 refreshes/day plus discovery, comfortably inside Tier 2's 15/min · 150/hr ·
600/day (~200 dockets/day): each window's ~30×3 ≈ 90 requests stays under the
hourly ceiling and the four windows stay under the daily one. A slice of every run
(`eligible_refresh_reserve`) is reserved for the stalest predict-eligible cases so
the SCOTUS-touched pilot set rotates fast under the gate. A second slice
(`backfill_reserve`) feeds the interim date backfill — re-fetching dateless
resolved rows and recent-Term cert shells so the back-test clock and the cert
back-test set grow — inside the same per-run cap, so it changes the budget's
*allocation*, never its total. Tier 3+ becomes the floor
only once the gate widens toward keeping all fourteen courts current at the live
frontier. The membership raises the *ceiling*; the client still throttles to
whatever `FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD` are set to in the runner
env (wired in `run-pull.yml` from repo variables, defaulting to the held tier), so
realizing a higher rate means setting those variables — no code change. The
throttle paces, it never stalls: a wait past the client's max-wait setting (an
exhausted hour/day window) raises instead of sleeping, and the run wraps up early
— see the degradation guards in [data-pipeline.md](data-pipeline.md).

> **Line item: $250–1,200/yr** (pilot Tier 2 annual ≈ $250/yr; Tier 3–4 as scope widens).

### 3. GitHub Actions & Codespaces

Every `run:*` stage executes on a GitHub-hosted runner, and the agent runs
*inside* that runner — so predict/evaluate runner-minutes scale with agent
wall-clock (jobs cap at 60 min). The repo is **public**, and on a public repo
**standard GitHub-hosted (2-core) runners are free and unlimited**
([Actions pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)).
The realistic runner-minute footprint, free at every level:

- **Backfill (now):** `run:seed` is the spike — its daily loop runs to a ~4.5h
  budget, so on the order of **~8K runner-min/month** while the backlog loads, then
  drops to quarterly reconciliation.
- **Steady pilot:** `run:pull`'s four daily windows are deterministic and light
  (**~700 min/month**); gated predict/evaluate add roughly **~2–4K min/month**
  depending on SCOTUS activity.
- **September long-conference burst:** ~2,000 petitions × 3 engines is a one-time
  spike of **tens of thousands** of runner-minutes around the conference
  (`max_parallel: 6` bounds concurrency, not the total).

> **Line item: ≈ $0/mo** for Actions. It only turns non-zero if a job is pinned to
> a **larger runner** (4-core+), which bills per-minute even on a public repo
> (Linux 2-core is **$0.006/min**, for reference), or if the repo is flipped back
> to private.

**Codespaces** is development only:
[120 free core-hours/mo](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
(Free) / 180 (Pro), then **$0.18/hr** (2-core) + **$0.07/GB-mo** storage. Realistic
dev usage: **$0–50/mo**.

Artifact/cache storage on Actions is **$0.25/GB-mo** (shared storage) — negligible
here since the corpus lives in DVC/S3, not Actions artifacts.

### 4. S3 / DVC corpus storage

The raw-fact corpus (`corpus/corpus.db`) and metrics live in a **private S3
bucket** behind DVC. [S3 Standard, us-east-1](https://aws.amazon.com/s3/pricing/):
**$0.023/GB-mo** storage, **$0.005/1K** PUTs, **$0.0004/1K** GETs; egress to the
internet is free for the first **100 GB/mo account-wide**, then **$0.09/GB**
(ingress always free).

GitHub-hosted runners execute on **Azure**, so every byte a workflow reads out of
the bucket — a `dvc pull`, a ranged `GET` — is S3 **internet egress** against
that allowance. There is no same-region discount between Actions and S3.

> **Superseded assumption.** This section previously priced workflow egress as
> free on the claim that runners run in the bucket's region. That was wrong —
> GitHub-hosted runners are Azure-hosted — and the error was masked while the
> corpus blob was sub-GB, keeping all transfer inside the free tier. The figures
> below are re-derived under the corrected model and the **ranged-read design**
> (cells query the blob in place; see [data-pipeline.md](data-pipeline.md)).

The corpus is a handful of large blobs, not millions of files (by design). Even a
corpus carrying opinion text for the full backlog is plausibly tens of GB;
DVC keeps historical versions, so budget for a small multiple:

- **Storage:** ~10–100 GB → **≈ $0.25–2.50/mo.**
- **Ingress (`dvc push`):** free, at any scale.
- **Cell reads (ranged):** a predict/evaluate/reconcile cell no longer pulls the
  blob; it makes indexed point queries over HTTP range requests. Measured
  against the real corpus: a snapshot provisioning ≈ 5 GETs / ~1.3 MB; a
  filtered priors retrieval is MB-scale (tens of MB for a broad filter). Budget
  **≈ 10–50 MB and a few hundred GETs per cell**. The September burst — a
  long-conference batch on the order of 1–2K cells — is then
  2,000 × 50 MB ≈ **≤ 100 GB** of burst egress (≈ $0–9 at the margin, most of
  it inside the free tier) plus ~400K GETs ≈ $0.16. Under the superseded
  per-cell full-pull design the same burst would have moved 2,000 × the blob —
  ~4 TB ≈ **$350+** at even a 2 GB blob; the ranged redesign is what keeps this
  term flat as the blob grows.
- **Recurring full pulls (the remaining bulk egress):** the scan-shaped
  consumers still move whole blobs — the writer (`run-pull`, **four windows a
  day** ⇒ ~120 pulls/mo on its own), the plan jobs each triggered run, then
  analytics/cleanup and an occasional deliberate Codespaces exploration or
  integration check. Order **~120–200 full pulls/mo × blob size**: at today's
  ~0.8 GB blob that is ~100–170 GB/mo, **at or above the free tier** ⇒
  ≈ **$0–10/mo**. This term scales linearly with the blob: at a 10 GB blob the
  same cadence moves ~1–2 TB/mo ≈ **$80–170/mo**, making it — not the cells —
  the S3 line's dominant term. If backlog growth takes the blob there, the
  lever is moving the full-pull consumers to ranged/incremental reads, caching
  the blob on the Actions side, or thinning the pull cadence.

> **Line item: ≈ $10/mo at today's blob; ≈ $100/mo at a tens-of-GB blob**
> (driven by the recurring full pulls, per the derivation above). The other thing that
> would change it materially is storing **embeddings** for semantic retrieval
> over the full backlog (a future upgrade) — that adds storage plus a one-time
> embedding compute pass, though CourtListener's bulk set ships ~2 TB of
> precomputed case-law embeddings (free to use, ~$200 one-time S3 egress if
> downloaded), so prefer reusing those over regenerating; size it when that
> lands.

## Monthly and yearly summary

Fixed/baseline costs are small and predictable; the inference line is the
variable that scope controls. Two reference points:

### A. Pilot / low-volume (gated slice, on-demand API)

Development plus the **SCOTUS-interaction gate** at its entry point — the
long-conference cert batch on the on-demand API (see *The pilot slice* above).
Interactive development draws on the Max subscription; the automated predict/eval
batch is API-metered (all three engines).

| Item | Monthly | Yearly |
|------|---------|--------|
| Claude Max 20x (interactive dev) | $200 | $2,400 |
| Predict/eval inference — Claude + Codex + Gemini **API** (gated) | ~$150–1,100 | ~$1.8–13K |
| CourtListener Tier 2 (annual) | ~$21 | $250 |
| GitHub Actions (public repo) | ~$0 | ~$0 |
| Codespaces | ~$0–50 | ~$0–600 |
| S3 / DVC | ~$5 | ~$60 |
| **Total** | **≈ $375–1,375/mo** | **≈ $4.5–16K/yr** |

### B. Full scope (all 14 courts, all three engines, every event)

| Item | Monthly | Yearly |
|------|---------|--------|
| **Model inference (predict + evaluate, on-demand API)** | **≈ $22K** | **≈ $261K** |
| CourtListener Tier 4 | $100 | $1,200 |
| GitHub Actions (public repo) | ~$0 | ~$0 |
| Codespaces | ~$50 | ~$600 |
| S3 / DVC (recurring full pulls at a tens-of-GB blob; see §4) | ~$100 | ~$1,200 |
| **Total** | **≈ $22.2K/mo** | **≈ $264K/yr** |

The gap between A and B is almost entirely the prediction *slice* and the
three-engine fan-out. The budget is governed by choosing where on that line to
operate: start at **A** (the long-conference batch on the on-demand API), measure
real per-run token cost (≈$0.50/run, folded into the figures above), then open the
**SCOTUS-interaction gate** to its steady state (≈$33K/yr inference — roughly 1/8
of B) before deciding, with a year of cost data, whether to widen the gate toward
full scope.

## Possible future options

Not in scope today, but sized here so the trade-offs are explicit when they come up:

- **Batch API for non-latency-sensitive work.** ~50% off predict/evaluate on
  eligible batches (the long conference, back-testing, bulk re-scoring). The
  pipeline runs on-demand today; adopting batch for the cert batch alone would
  roughly halve that entry-point cost.
- **Widen the prediction gate** past SCOTUS-touched cases — e.g. a rotating sample
  of appeals that never reach SCOTUS — once a year of cost data is in hand.
- **Embeddings for semantic retrieval** over the full backlog: a one-time compute
  pass plus ongoing storage (see driver #4), or reuse of CourtListener's shipped
  case-law embeddings.
- **Higher CourtListener tier (3–4 or commercial)** if the gate widens toward
  keeping all fourteen courts current at the live frontier.
