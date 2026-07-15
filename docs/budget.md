# Budget

Projected costs to load the corpus's historical Supreme Court mass, keep it
current with daily **pull** and **live** windows, and run
**predict**/**evaluate** regularly. This is a
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

**The shape, in one line: a fixed floor plus three scaling lines.** A deliberate
**~$500/mo misc floor** (domains, email, the Claude Max dev subscription — the
fixed individual-use items, driver #5) carries the costs that do not grow with the
work (dev-usage Codespaces varies a little beside it, but with dev hours, not the
workload). Above it, exactly three lines scale with the work, in order: **inference**
(dominant), then the volume-linked **CourtListener membership** and **S3**. And
inference itself now has a single dial — the salience gate's **capacity `N`**, the
number of petitions per conference the tournament actually runs (the *how many we
predict*). `N` is what funding moves, so the whole budget re-cuts as
`fixed floor + N × per-case + volume lines` — worked out under *Capacity `N`* below.

A second consequence: the flat **Claude Max** subscription cannot absorb
full-scope volume. The subscription is metered by rolling 5-hour and weekly
limits intended for interactive use, and per Anthropic's policy the subscription
OAuth token is meant for Claude Code / claude.ai, not automated CI/CD — they
direct automation at a pay-per-token API key. So the subscription is the right
tool for **development and low-volume piloting**, while sustained pipeline
inference is an **API-metered** cost. The pipeline reflects both modes: interactive
development uses the Max subscription, and every automated stage (`run:predict`,
`run:evaluate`) authenticates to Claude via the
Anthropic **API key**.

## Cost drivers

### 1. Model usage (the dominant cost)

Three engines run the agentic stages, routed per registry entry
([config/predictors.yaml](../config/predictors.yaml),
[config/evaluators.yaml](../config/evaluators.yaml)):

| Engine | Used by | Billing | Rate (per 1M tokens) |
|--------|---------|---------|----------------------|
| **Claude Code** (`claude-fable-5`) | `claude-baseline`, `claude-judge` (predict/evaluate default) | Anthropic API (workflows); Max subscription for interactive local dev | Subscription: **$200/mo** flat (Max 20x — dev only, in the misc floor #5). API: **$10 in / $50 out** |
| **Codex** (`gpt-5.6-sol`) | `codex-baseline`, `codex-judge` | OpenAI API (pay-per-token) | **$5 in / $30 out** |
| **Gemini** (`gemini-3.1-pro-preview`) | `gemini-baseline`, `gemini-judge` | Gemini API (pay-per-token) | **$2 in / $12 out** (≤200k context; steps up beyond) |

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
this section, kept in `fedcourtsai.pricing`) to a `usage.json` beside its
output, and `fedcourts usage-summary` rolls those up. The **pilot round**
measured this at scale across models: over its ~155 predict runs, claude-baseline
ran **~$0.55/run** on `claude-opus-4-8` but **~$2.59/run** on `claude-fable-5`
(the 2× token rate plus heavier retrieval); codex-baseline held near
**~$0.91–1.01/run** on `gpt-5.5`/`gpt-5.6-sol`; gemini-baseline measured
**~$0.52/run** on `gemini-3.1-pro-preview` and — counterintuitively —
**~$0.99/run** on the cheaper-rated `gemini-3.5-flash` (the flash runs burned
more tokens than the rate saved). The pilot's blended mean was ≈ **$1.54/run**;
prompt caching on the stable prefix is what keeps the sub-Fable figures near the
original $0.50 expectation.

The **clean-slate cutover cleared that pilot ledger**, so the committed ledger is
rebuilding from the first clean round — **9 predict runs so far**, three per engine:
claude-baseline ~$3.62/run, codex-baseline ~$1.25/run, gemini-baseline ~$0.75/run
(on the `claude-fable-5` / `gpt-5.6-sol` / `gemini-3.1-pro-preview` defaults), a
**~$1.87/run blended mean**. That is still thin, and the Fable-heavy mean sits well
above the historical **~$0.50/run** anchor the full-scope estimates below use — so
those estimates are the *optimistic* end; the *Capacity `N`* section budgets the
measured range explicitly. Re-anchor as the clean ledger accumulates and the
evaluate side is measured. **Caveats:** these are *predict* figures; no event has
been evaluated yet, so **evaluate per-run cost is unmeasured**. **Model defaults
(2026-07):** codex `gpt-5.6-sol` (priced identically to `gpt-5.5` at $5/$30);
gemini `gemini-3.1-pro-preview` — the Pro tier is the like-for-like comparator
against the other engines' frontier defaults, and its measured cost undercut
flash's despite the higher rate, so the per-token "cheaper lever" reading of
flash did not survive measurement. Re-check `fedcourts usage-summary` as runs
accumulate on the defaults.

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
| **Gate the prediction scope** — predict only SCOTUS dockets (the gate; see below) rather than every event | Linear cut; the biggest dial |
| **Salience rank-and-cap to capacity `N`** — within the SCOTUS gate, run the tournament only on the top-`N` salient petitions per conference | The finer dial; `N` is the funding knob (see *Capacity `N`*) |
| **One engine per stage** instead of three competing | ~67% predict, more on evaluate (which scales with evaluators × predictors) |
| **Cheaper competitor model** — run one predictor on `claude-haiku-4-5` ($1/$5) or `claude-sonnet-4-6` ($3/$15) | Large cut on that predictor |
| **Batch API** for back-testing / bulk re-scoring (not used today) | ~50% on eligible work |
| **Prompt caching** on the stable prefix (already on) | Up to ~90% of the input portion |
| **`predict_on_change_only`** (already set) | Avoids re-predicting unchanged cases |

The controlling choices are the first two rows: the prediction *slice* and the
engine fan-out. The pilot fixes them explicitly with the SCOTUS-docket gate
below.

#### The pilot slice: SCOTUS dockets

Rather than a fixed sample, the pilot bounds spend with a **gate**: only SCOTUS
dockets are in-scope for predict/evaluate. A granted case's merits events on its
SCOTUS docket are covered; its originating court-of-appeals docket (remands
included) and the ~42K/yr appeals cases that never reach
SCOTUS are not — the gate keeps spend off pro-se petitions' lower-court
shadows and every other docket the cert model does not score. Ingestion is unchanged: the ingestion channels still assemble all
fourteen courts (deterministic, ~$0 model spend) so the full history stays queryable for
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

#### Capacity `N`: the funding knob

The SCOTUS gate bounds *which court*; within it, [salience.md](salience.md)'s
**capacity `N`** bounds *how many* — the tournament runs on the top-`N` salient
petitions per conference plus a few always-include carve-outs, so inference spend
is `N × per-case` and `N` is the single dial funding moves. Raising `N` deepens
the salience-ranked slice; it never reshuffles the ranking.

**Unit cost, per fully-processed case** — the full three-engine, cross-evaluated
tournament, at the ~$0.50/run cache-served anchor:

```
predict:   3 predictors            × $0.50 = $1.50
evaluate:  3 evaluators × 3 preds   × $0.50 = $4.50
                                             ──────
per fully-tournamented case ≈ $6   (consistent with $33K ÷ ~5,500 gated events)
```

The $0.50/run is the **optimistic anchor** (prompt-cached, cheaper models). The
measured clean-ledger mean has run higher — **~$1.87/run blended** over the first
9 predict runs (claude-baseline ~$3.62 on `claude-fable-5`, codex ~$1.25, gemini
~$0.75) — which puts the same fully-tournamented case (12 runs: 3 predict + 9
evaluate) near **~$22**. So the real unit is **~$6–22/case by model mix**, and a
deliberately lean **single-engine,
single-evaluator** release is **~$1/case** (1 × $0.50 predict + 1 × 1 × $0.50
evaluate). Budget the range, not the point — and note evaluate per-run cost is
still projected (no event has been evaluated yet).

**`N` as the funding knob** — read the dial straight off the unit cost:

```
N ≈ inference_budget / (~$6–22 per case)
```

Reference points at the **$6 anchor**:

- **$10K** (well within an Anthropic startup / AWS Activate credit grant) →
  **~1,600 fully-tournamented cases** — most of the ~2,000-petition long
  conference (the full batch runs ~$12–13K, sized above).
- **$33K** → the full steady-state cert gate (~5,500 events) with **no cap** — at
  which point salience is purely the public ranking, not a spend control.

At the measured **~$22/case** those same budgets buy **~450** and **~1,500** cases,
so the credit-grant capacity is only honest stated as a range: **$10K → ~450–1,600
cases**. The **cheaper-competitor** lever (one predictor on a smaller model —
`claude-haiku-4-5` at $1/$5, `claude-sonnet-4-6` at $3/$15) reads here as a
**capacity multiplier**: it stretches a fixed credit grant over *more* cases, not
merely a per-run cost saving.

**Tier-1 salience scoring itself is ≈ $0** — a deterministic pure function of
corpus features, no model call. The optional cheap-model questions-presented
enrichment pass, if enabled, adds a small per-eligible-case cost (one cheap-model
call per Tier-0 survivor, well under the tournament's per-case cost); it is off by
default, so the salience gate spends nothing to *decide* what the tournament runs
on.

### 2. CourtListener API (membership for pull throughput)

**Historical** loading walks the supremecourt.gov docket JSON — **$0**, no
rate limit. The historical SCOTUS mass costs nothing in API terms.

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
refreshing up to `max_cases_per_run` (30) dockets — ~120 refreshes/day of
targeted enrichment (CourtListener discovery is off;
the budget-free supremecourt.gov live job owns SCOTUS freshness and
onboarding), comfortably inside Tier 2's 15/min · 150/hr ·
600/day (~200 dockets/day): each window's ~30×3 ≈ 90 requests stays under the
hourly ceiling and the four windows stay under the daily one. A slice of every run
(`eligible_refresh_reserve`) is reserved for the stalest SCOTUS dockets so
the in-scope set rotates fast under the gate. Tier 3+ becomes the floor
only once the gate widens toward keeping all fourteen courts current at the live
frontier. The membership raises the *ceiling*; the client still throttles to
whatever `FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD` are set to in the runner
env (wired in `run-pull.yml` from repo variables, defaulting to the held tier), so
realizing a higher rate means setting those variables — no code change. One
caveat to the arithmetic: the predict/evaluate cells' MCP retrieval uses the
same CourtListener token but does not pass through this in-process governor,
so agent lookups draw from the same per-token quota the pull math above
treats as pull's alone — a retrieval-heavy run consumes headroom the governor
cannot see. The throttle paces, it never stalls: a wait past the client's
max-wait setting (an
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

- **Historical walking:** `run-pull`'s daily historical job runs to a ~1h50m
  budget — order **~2–3K runner-min/month** at the daily cadence, dropping to
  near zero once every configured Term's frontier is reached.
- **Steady pilot:** `run-pull`'s eight daily forward windows (four CourtListener
  enrichment + four supremecourt.gov live polls) are deterministic and light
  (**~1.5K min/month**); gated predict/evaluate add roughly **~2–4K min/month**
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
here since the corpus lives in S3, not Actions artifacts.

### 4. S3 corpus storage

The raw-fact corpus (`corpus/corpus.db` and the per-case content store) lives
in a **private S3 bucket**.
[S3 Standard, us-east-1](https://aws.amazon.com/s3/pricing/):
**$0.023/GB-mo** storage, **$0.005/1K** PUTs, **$0.0004/1K** GETs; egress to the
internet is free for the first **100 GB/mo account-wide**, then **$0.09/GB**
(ingress always free).

GitHub-hosted runners execute on **Azure**, so every byte a workflow reads out of
the bucket — a full `corpus-pull`, a ranged `GET` — is S3 **internet egress**
against that allowance. There is no same-region discount between Actions and S3.

> **Superseded assumption.** This section previously priced workflow egress as
> free on the claim that runners run in the bucket's region. That was wrong —
> GitHub-hosted runners are Azure-hosted — and the error was masked while the
> corpus blob was sub-GB, keeping all transfer inside the free tier. The figures
> below are re-derived under the corrected model and the **ranged-read design**
> (cells query the blob in place; see [data-pipeline.md](data-pipeline.md)).

> **Split is live; figures not yet measured.** The projections below were sized
> against the single full corpus blob. The corpus split (payload-free index +
> per-case content store) is now live in production, so they remain projections
> pending confirmation against measured transfer — the post-cutover egress check
> that compares real S3 egress + request counts to these numbers.

The corpus is a handful of large blobs, not millions of files (by design). Even a
corpus carrying opinion text for the full backlog is plausibly tens of GB; the
content-addressed remote keeps historical versions (add-only), so budget for a
small multiple:

- **Storage:** ~10–100 GB → **≈ $0.25–2.50/mo.**
- **Ingress (`corpus-push`):** free, at any scale.
- **Cell reads (ranged):** a predict/evaluate cell never pulls the
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
  consumers still move whole blobs — the corpus-writer jobs (`run-pull`,
  **eight windows a day** across its pull + live jobs ⇒ ~240 pulls/mo on their
  own), then analytics and an occasional deliberate Codespaces exploration (a
  maintainer's local cleanup sweep included) or integration check. The
  predict/evaluate **plan** jobs no longer pull — they read the index in place
  over the ranged backend, like the cells, so they fall under *Cell reads*
  above, not here. Order **~250–300 full pulls/mo × blob size**: at today's
  ~1.0 GB blob that is ~250–300 GB/mo, **just above the 100 GB free tier** ⇒
  ≈ **$15/mo**. This term scales linearly with the blob: at a 10 GB blob the
  same cadence moves ~2.5–3 TB/mo ≈ **$230/mo**, making it — not the cells —
  the S3 line's dominant term. If backlog growth takes the blob there, the
  lever is moving the full-pull consumers to ranged/incremental reads, caching
  the blob on the Actions side, or thinning the pull cadence.

> **Line item: ≈ $15/mo at today's ~1 GB blob; ≈ $230/mo at a 10 GB blob**
> (driven by the recurring full pulls, per the derivation above). The other thing that
> would change it materially is storing **embeddings** for semantic retrieval
> over the full backlog (a future upgrade) — that adds storage plus a one-time
> embedding compute pass, though CourtListener's bulk set ships ~2 TB of
> precomputed case-law embeddings (free to use, ~$200 one-time S3 egress if
> downloaded), so prefer reusing those over regenerating; size it when that
> lands.

### 5. Misc fixed costs — the non-scaling floor

A flat **$500/mo** bucket for the individual-use, non-scaling items, carried as one
line so the rest of the budget can stay on what actually scales: the domains
(`modelmirror.ai`, `fedcourts.ai`), the email provider, the **Claude Max dev
subscription** (a $200/mo monthly individual plan — interactive dev only, never
automation; see driver #1), and other small fixed items. The $500 is a deliberate
**overestimate** meant to cover the bucket without per-item tracking; its defining
property is that it **does not scale** with events, corpus size, or predictor
count. Everything that scales sits in the three lines above it — inference
(driver #1, dialed by `N`), CourtListener membership (#2), and S3 (#4).

> **Line item: $500/mo flat** (a fixed floor, not a variable).

## Monthly and yearly summary

The budget is a **fixed floor plus three scaling lines**: the ~$500/mo misc floor
(driver #5) is constant, and above it inference (dialed by capacity `N`),
CourtListener membership, and S3 are the only lines that grow. Two reference
points bound the range:

### A. Pilot / low-volume (gated slice, on-demand API)

Development plus the **SCOTUS-docket gate** — the
long-conference cert batch on the on-demand API (see *The pilot slice* above).
Interactive development draws on the Max subscription; the automated predict/eval
batch is API-metered (all three engines).

| Item | Monthly | Yearly |
|------|---------|--------|
| **Misc fixed floor** (domains, email, Claude Max dev sub, small items; #5) | $500 | $6,000 |
| Predict/eval inference — Claude + Codex + Gemini **API** (gated, `N`-capped) | ~$150–1,100 | ~$1.8–13K |
| CourtListener Tier 2 (annual) | ~$21 | $250 |
| Codespaces (dev) | ~$0–50 | ~$0–600 |
| S3 (corpus + content store; recurring full pulls at today's ~1 GB blob) | ~$15 | ~$180 |
| GitHub Actions (public repo) | ~$0 | ~$0 |
| **Total** | **≈ $685–1,685/mo** | **≈ $8–20K/yr** |

### B. Full scope (all 14 courts, all three engines, every event)

| Item | Monthly | Yearly |
|------|---------|--------|
| **Model inference (predict + evaluate, on-demand API)** | **≈ $22K** | **≈ $261K** |
| Misc fixed floor (#5) | $500 | $6,000 |
| CourtListener Tier 4 | $100 | $1,200 |
| Codespaces | ~$50 | ~$600 |
| S3 (recurring full pulls at a ~10 GB blob; see §4) | ~$230 | ~$2,760 |
| GitHub Actions (public repo) | ~$0 | ~$0 |
| **Total** | **≈ $22.9K/mo** | **≈ $272K/yr** |

The gap between A and B is almost entirely the inference line, and within the
SCOTUS gate that line is `N × per-case` — so **`N` is where the budget is
governed**. Start at **A** with a small `N` (the OT2026 long-conference batch on
the on-demand API), let the clean ledger measure real per-case cost against the
~$6–22 range, then raise `N` toward the steady-state gate (≈$33K/yr inference at
`N` = the whole cert docket — roughly 1/8 of B, salience now the public ranking
rather than a spend control) as funding — a credit grant or a first external
event — lifts it. Whether to widen *past* SCOTUS toward full scope stays a
separate, later, year-of-cost-data decision.

## Possible future options

Not in scope today, but sized here so the trade-offs are explicit when they come up:

- **Batch API for non-latency-sensitive work.** ~50% off predict/evaluate on
  eligible batches (the long conference, back-testing, bulk re-scoring). The
  pipeline runs on-demand today; adopting batch for the cert batch alone would
  roughly halve that entry-point cost.
- **Widen the prediction gate** past SCOTUS dockets — e.g. the originating
  courts-of-appeals dockets, or a rotating sample
  of appeals that never reach SCOTUS — once a year of cost data is in hand.
- **Embeddings for semantic retrieval** over the full backlog: a one-time compute
  pass plus ongoing storage (see driver #4), or reuse of CourtListener's shipped
  case-law embeddings.
- **Higher CourtListener tier (3–4 or commercial)** if the gate widens toward
  keeping all fourteen courts current at the live frontier.
