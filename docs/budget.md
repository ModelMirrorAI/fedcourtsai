# Budget

Projected costs to **seed** the corpus with all historical Supreme Court and
courts-of-appeals cases, keep it current with daily **pull**, and run
**predict**/**evaluate** regularly across all fourteen courts. This is a
forecast, not a spending cap: it sizes each cost driver so scope and cadence can
be chosen with the bill in view. For how the phases work, see
[data-pipeline.md](data-pipeline.md) and [pipeline.md](pipeline.md).

All prices are USD, captured mid-2026; treat them as a snapshot and re-check the
linked sources before committing spend.

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
tool for **development and low-volume piloting**; sustained pipeline inference at
scale is an **API-metered** cost. The budget reflects both modes.

## Cost drivers

### 1. Model usage (the dominant cost)

Two engines run the agentic stages, routed per registry entry
([config/predictors.yaml](../config/predictors.yaml),
[config/evaluators.yaml](../config/evaluators.yaml)):

| Engine | Used by | Billing | Rate (per 1M tokens) |
|--------|---------|---------|----------------------|
| **Claude Code** (`claude-opus-4-8`) | `claude-baseline`, `claude-judge`, all `run:dev` | Anthropic API (workflows); Max subscription for interactive local dev | Subscription: **$200/mo** flat (Max 20x). API: **$5 in / $25 out** |
| **Codex** (`gpt-5.5`) | `codex-baseline`, `codex-judge` | OpenAI API (pay-per-token) | **$5 in / $30 out** |

Sources: [Claude Max](https://support.claude.com/en/articles/11049741-what-is-the-max-plan),
[Claude API pricing](https://platform.claude.com/docs/en/pricing),
[OpenAI API pricing](https://developers.openai.com/api/docs/pricing).

**Per-run cost.** A single predict or evaluate run is an *agentic* job: the agent
reads the prompt, AGENTS.md, the case snapshot, and a handful of retrieved
priors, then writes its artifacts over several tool-use turns. Effective token
usage is therefore much larger than the visible artifacts. Planning assumption:
**~200K effective input + ~12K output per run**, which is **≈ $1–2 per run** on
either engine before discounts. This is the single most sensitive number in the
budget — replace it with **measured per-run usage from the first real runs**.

Every predict/evaluate run now records its measured tokens and an estimated cost
(at the rates in this section, kept in `fedcourtsai.pricing`) to a `usage.json`
beside its output; `fedcourts usage-summary` rolls those up into an actual \$/run.
Once enough real runs have accumulated, update the assumption above from that
figure. Note the two big discounts that apply to it:

- **Prompt caching** — automatic on both engines. The stable prefix (AGENTS.md +
  the prompt template + schema) is byte-identical across runs and is read before
  any per-case facts, so it is served from cache across a run's many tool-use
  turns; cached reads bill at ~0.1× and cache writes at ~1.25× (both in
  `fedcourtsai.pricing`, and recorded per run in `usage.json`). Keep that prefix
  byte-stable to capture it. The predict and evaluate workflows request the
  1-hour cache TTL explicitly: it is free on the Claude Max subscription and keeps
  the cache from expiring mid-run should Claude auth move to the Anthropic API,
  whose default TTL is only 5 minutes.
- **Batch API (Claude)** — 50% off for non-latency-sensitive work
  (back-testing, bulk re-scoring). Live pull-triggered predictions are
  latency-sensitive and stay on-demand.

**Volume.** Scope is all fourteen courts. The courts of appeals terminate
**~42K cases/yr** (~41K filed; [Judicial Business 2025, Table B](https://www.uscourts.gov/data-news/reports/statistical-reports/judicial-business-united-states-courts/judicial-business-2025/us-courts-appeals-judicial-business-2025)),
and SCOTUS docket activity adds **~5K cases/term** with **~70 cert grants**
([SCOTUS Table A-1](https://www.uscourts.gov/sites/default/files/2025-01/supcourt_a1_0930.2024.pdf)).
At roughly one baseline predictable event per docket that is **~45–50K events/yr
≈ ~130/day**.

**Annual inference at full scope** (every event, both predictors, both
evaluators), using the model below:

```
predictions  = events/yr × predictors × $/run
evaluations  = resolved_events/yr × (evaluators × predictors) × $/run

≈ 48,000 × 2 × $1.6      ≈ $154K   predictions
≈ 42,000 × (2×2) × $1.5  ≈ $252K   evaluations
                          ───────
                          ≈ $400K / yr   (≈ $33K / mo)
```

That figure is deliberately alarming: it is what "predict and evaluate
*everything, with everything*" costs, and it is why the levers below exist. Even
if the per-run assumption is 3× too high, full scope is still ~$130K/yr — far
above all other costs combined.

**Levers** (each is independent; combine them):

| Lever | Effect |
|-------|--------|
| **Gate the prediction scope** — predict only cases that have interacted with SCOTUS (the pilot gate; see below) rather than every event | Linear cut; the biggest dial |
| **One engine per stage** instead of two competing | ~50% |
| **Cheaper competitor model** — run one predictor on `claude-haiku-4-5` ($1/$5) or `claude-sonnet-4-6` ($3/$15) | Large cut on that predictor |
| **Batch API** for back-testing / bulk re-scoring | 50% on eligible work |
| **Prompt caching** on the stable prefix | Up to ~90% of the input portion |
| **`predict_on_change_only`** (already set) | Avoids re-predicting unchanged cases |

> **Recommendation.** The cost *model* — not any single funding source — is the
> point: spend is governed by the prediction *slice* and the engine fan-out, so
> decide those explicitly (the pilot's choice is the SCOTUS-interaction gate below).
> Interactive development uses a Claude Max subscription; all automated pipeline
> inference is API-metered from the outset, so there is no token-source ambiguity as
> volume grows.

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
predictions ≈ 5,500 × 2 × $1.6      ≈ $18K
evaluations ≈ 5,500 × (2×2) × $1.5  ≈ $33K
                                     ───────
                                     ≈ $50K / yr   — roughly 1/8 of full scope
```

and it tunes far below that for the first release. The **long-conference batch**
(~2,000 petitions resolved in one sitting) is not latency-sensitive, so it runs on
the **Batch API** at 50% off behind a single engine — on the order of **$1.5–3K for
the entire batch**. That is the lean entry point the OT2026 cert mini-release is
sized against; the steady-state gate above is where it grows next, still an order of
magnitude under full scope.

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

> **Line item: $600–1,200/yr.**

### 3. GitHub Actions & Codespaces

Every `run:*` stage executes on a GitHub-hosted runner, and the agent runs
*inside* that runner — so predict/evaluate runner-minutes scale with agent
wall-clock (jobs cap at 60 min).
[Actions pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing):
Linux 2-core is **$0.006/min** beyond the plan's included minutes (Free 2,000 /
Pro 3,000 / Team 3,000 per month, **private repos only**); **public repos run
standard runners free**.

At ~130 events/day × 2 engines, predict alone is a few thousand runner-hours a
month:

- **Public repo:** **≈ $0** for Actions.
- **Private repo:** **≈ $1–3K/mo** at full volume — real, but still a fraction of
  inference. The matrix `max_parallel: 4` and `predict_on_change_only` already
  bound it.

The repo's public/private status is therefore a meaningful budget decision; if
private, set a billing budget + alerts (the default spending limit is $0, which
*blocks* runs past the free tier rather than charging silently).

**Codespaces** is development only:
[120 free core-hours/mo](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
(Free) / 180 (Pro), then **$0.18/hr** (2-core) + **$0.07/GB-mo** storage. Realistic
dev usage: **$0–50/mo**.

Artifact/cache storage on Actions is **$0.25/GB-mo** (shared storage) — negligible
here since the corpus lives in DVC/S3, not Actions artifacts.

### 4. S3 / DVC corpus storage

The raw-fact corpus (`corpus/corpus.db`) and metrics live in a **private S3
bucket** behind DVC. [S3 Standard, us-east-1](https://aws.amazon.com/s3/pricing/):
**$0.023/GB-mo** storage, **$0.005/1K** PUTs, **$0.0004/1K** GETs, egress free for
the first 100 GB/mo then $0.09/GB (ingress always free).

The corpus is a handful of large blobs, not millions of files (by design). Even a
corpus carrying opinion text for the full backlog is plausibly tens of GB;
DVC keeps historical versions, so budget for a small multiple:

- **Storage:** ~10–100 GB → **≈ $0.25–2.50/mo.**
- **Requests + egress:** DVC pull/push move whole blobs; daily writers and
  read-only predict/evaluate consumers keep transfer modest. Workflows run in the
  same region as the bucket, so egress to runners is free. **≈ $1–5/mo.**

> **Line item: < $10/mo** under current design. The one thing that would change
> this materially is storing **embeddings** for semantic retrieval over the full
> backlog (a future upgrade) — that adds both storage and a one-time embedding
> compute cost; size it when that lands.

### 5. Often-omitted factors

- **Embedding generation** (future semantic retrieval): a one-time pass over
  millions of dockets is its own inference bill; the CourtListener bulk set also
  *ships* ~2 TB of precomputed case-law embeddings (free to use, ~$200 one-time S3
  egress if downloaded). Prefer reusing those over regenerating.
- **Agent reconcile runs:** ambiguous event-definition / resolution cases spawn
  an agent (`run:pull` reconcile). Low volume by design (deterministic-first), but
  it is non-zero model usage.
- **`run:dev` model usage:** ongoing pipeline development by Claude Code draws on
  the same subscription/API — budget it as part of driver #1, not free.
- **Failed/retried runs:** CI retries, rebases, and re-runs consume runner
  minutes and (for agent stages) tokens. Add ~10–15% headroom.
- **Monitoring/billing hygiene:** set budgets + alerts on the OpenAI key, the
  Anthropic API (if used), and GitHub Actions; the corpus and S3 are cheap but
  the inference and (private-repo) Actions bills are not self-limiting.

## Monthly and yearly summary

Fixed/baseline costs are small and predictable; the inference line is the
variable that scope controls. Two reference points:

### A. Pilot / low-volume (gated slice, API-metered)

Development plus the **SCOTUS-interaction gate** at its entry point — the
long-conference cert batch on the Batch API (see *The pilot slice* above) — sized to
fit within the subscription's interactive limits.

| Item | Monthly | Yearly |
|------|---------|--------|
| Claude Max 20x (interactive dev) | $200 | $2,400 |
| Codex API (gated cert predictions/evals) | ~$100–400 | ~$1.2–5K |
| CourtListener Tier 3 | $50 | $600 |
| GitHub Actions (public repo) | ~$0 | ~$0 |
| Codespaces | ~$0–50 | ~$0–600 |
| S3 / DVC | ~$5 | ~$60 |
| **Total** | **≈ $360–700/mo** | **≈ $4–9K/yr** |

### B. Full scope (all 14 courts, both engines, every event)

| Item | Monthly | Yearly |
|------|---------|--------|
| **Model inference (predict + evaluate, API-metered)** | **≈ $33K** | **≈ $400K** |
| CourtListener Tier 4 | $100 | $1,200 |
| GitHub Actions (private repo; ~$0 if public) | ~$1–3K | ~$12–36K |
| Codespaces | ~$50 | ~$600 |
| S3 / DVC | ~$10 | ~$120 |
| **Total** | **≈ $34–36K/mo** | **≈ $415K/yr** |

The gap between A and B is almost entirely the prediction *slice* and the
two-engine fan-out. The budget is governed by choosing where on that line to
operate: start at **A** (the long-conference batch on the subscription), measure
real per-run token cost, then open the **SCOTUS-interaction gate** to its steady
state (~$50K/yr inference — an order of magnitude under B) before deciding, with a
year of cost data, whether to widen the gate toward full scope.
