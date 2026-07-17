# Budget

A cost forecast, not a spending cap: it sizes each driver so scope and cadence
can be chosen with the bill in view. Prices are USD, a mid-2026 snapshot
(re-check the linked sources before committing spend); the repo is **public**, so
figures assume the free public-repo Actions tier, and all inference is priced on
the **on-demand API**. For how the phases work, see
[data-pipeline.md](data-pipeline.md) and [pipeline.md](pipeline.md).

## The shape: a fixed floor plus one dominant scaling line

Every non-inference line — runners, storage, memberships, subscriptions — sums to
a near-constant **≈$5K/yr floor**. Agentic model usage for prediction and
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
`fedcourtsai.pricing`) to a `usage.json`, rolled up by `fedcourts usage-summary`.
Measured per-run cost spans **≈$0.29–7.87 by model mix** (blended mean **≈$2.12**
over the 160 predict runs on the ledger: claude-baseline ≈$4.06, codex ≈$1.51,
gemini ≈$0.61); the cheapest runs approach ≈$0.30 only when the byte-stable prefix
(AGENTS.md + prompt template + schema) is served from the prompt cache — automatic
on all three engines, billing cached reads at ≈0.1×, and the reason to keep that
prefix stable. Budget the range, not the point; evaluate per-run cost is still
projected (no event has been evaluated yet).

**Scope: the SCOTUS-docket gate.** The pilot predicts and evaluates only SCOTUS
dockets. Ingestion is unchanged — the channels still assemble all fourteen courts
deterministically (≈$0 model spend) so the full history stays queryable for
retrieval and back-testing; only the agentic stages are gated. Full 14-court
scope is the reference ceiling:

```
predictions  ≈ 48,000 events   × 3 predictors × $2.12   ≈ $305K
evaluations  ≈ 42,000 resolved × (3 × 3)      × $2.12   ≈ $801K
                                                          ────────
full scope                                                ≈ $1.1M / yr
```

The SCOTUS gate is roughly 1/8 of that — ≈5,500 cert decisions per term:

```
predict   ≈ 5,500 × 3     × $2.12   ≈ $35K
evaluate  ≈ 5,500 × (3×3) × $2.12   ≈ $105K
                                     ────────
full cert gate                       ≈ $140K / yr
```

**Capacity `N`: the funding knob.** Within the gate, [salience.md](salience.md)'s
capacity `N` bounds *how many* — the tournament runs on the top-`N` salient
petitions per conference plus a few always-include carve-outs, so inference spend
is `N × per-case`. One fully-tournamented case:

```
predict:   3 predictors           × $2.12 = $6.36
evaluate:  3 evaluators × 3 preds  × $2.12 = $19.08
                                            ──────
per case ≈ $25   (measured blended mean, three engines cross-evaluated)
```

so `N ≈ inference_budget / (≈$25 per fully-tournamented case)`. Tier-1 salience
scoring is itself ≈$0 (a deterministic pure function of corpus features, no model
call), so the gate spends nothing to *decide* what the tournament runs on. Raising
`N` deepens the salience-ranked slice; it never reshuffles the ranking.

**Monthly spend by provider.** The per-case cost splits across the three API
bills (measured predict means per engine; evaluate projected at the same
per-run means — each provider's judge scores all three predictions, so three
judge-runs per provider per case), so at a cadence of `C` tournamented cases
per month each provider's bill is its per-case line × `C`. The predict column
sums to $6.18, slightly under 3 × the $2.12 blended mean, because the blended
mean weights engines by run count:

| Provider (engine) | Predict $/case | Evaluate $/case (proj.) | $/case | Share | At `C` = 150/mo |
|-------------------|---------------:|------------------------:|-------:|------:|----------------:|
| Anthropic (`claude-fable-5`) | $4.06 | $12.18 | $16.24 | ≈66% | ≈$2,440 |
| OpenAI (`gpt-5.6-sol`) | $1.51 | $4.53 | $6.04 | ≈24% | ≈$910 |
| Google (`gemini-3.1-pro-preview`) | $0.61 | $1.83 | $2.44 | ≈10% | ≈$370 |
| **Total** | **$6.18** | **$18.54** | **≈$25** | | **≈$3.7K** |

Two-thirds of every inference dollar goes to Anthropic — size that provider's
spend limit accordingly, and expect a limit breach there to cost a third of a
run's coverage (the other engines are billed independently). The `C` = 150
column is a reference month of one conference cohort filled to the
per-conference cap (`C` counts cases per month; a month holds several
conferences, but mid-Term cohorts run well under the cap — median ~11
petitions per conference — so 150/month is a generous Term-month reference).
September's long-conference month is the peak: clearing the summer backlog at
the larger cap is ≈200 × $25 ≈ $5K, the bootstrapping envelope. Until evaluate
goes live only the predict column is being spent (≈$6.18/case, ≈$930 at
`C` = 150).

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

The pilot holds **Tier 2 ($250/yr)**, comfortably covering the four daily pull
windows (≈120 targeted refreshes/day) under the SCOTUS gate; Tier 3 ($50/mo)
becomes the floor only once the gate widens toward keeping all fourteen courts
current at the live frontier. The membership raises the ceiling — the client still
throttles to whatever `FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD` are set to.

> **Line item: $250–1,200/yr** (pilot Tier 2 annual; Tier 3–4 as scope widens).

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

The non-inference lines — misc floor ($350/mo), CourtListener ($250–1,200/yr), S3
(≈$15/mo, the one line that grows with the corpus blob), Codespaces ($0–50/mo),
Actions ($0) — sum to a near-constant **≈$5K/yr floor**. Everything
above it is inference `= N × per-case`, so funding moves a single dial: `N`, where
`N ≈ inference_budget ÷ (≈$25 per fully-tournamented case)`. Each order of
magnitude in funding buys roughly ten times the tournamented cases:

| Scenario | ≈ Annual | Inference (= total − ≈$5K floor) | Reach |
|----------|----------|----------------------------------|-------|
| Bootstrapping | ≈$10K | ≈$5K | the OT2026 long-conference cert release — ≈200 petitions, all three engines cross-evaluated (the `long_conference_capacity` cap) |
| Initial funding | ≈$100K | ≈$95K | ≈3,800 fully-tournamented cases — most of a cert term (the full ≈5,500-event gate runs ≈$140K uncapped, 3×3); salience still a spend control at this `N` |
| Well funded | ≈$1M | ≈$995K | approaches all-14-court full scope (every event, 3×3 ≈$1.1M); the cert gate is fully covered, so salience becomes the public ranking, not a spend control |
| **Floor (all scenarios)** | **≈$5K** | **—** | **misc + CourtListener + S3 + Actions; does not scale with `N`** |

Start at **bootstrapping** with a small `N`, let the ledger measure real per-case
cost against the ≈$25 estimate, then raise `N` as funding lifts it. The funding path
to each state — credit programs and external support — is tracked in
[milestones.md](milestones.md).
