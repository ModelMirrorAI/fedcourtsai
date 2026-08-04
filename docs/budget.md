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

**The interim docket: a budgeted stream with no new spend.**
[salience.md](salience.md)'s interim-docket section carries a second selection
problem — stays, injunctions, vacaturs pending certiorari — and it changes this
budget by nothing. In its 26-application OT2023–OT2024 spread sample, roughly
**85% (22 of 26)** are time-extension requests, filtered out deterministically by
`interim_signals.is_predictable_application` (≈$0, no model call); only the
substantive slice — **3 of 26 in that sample, ≈12%** — is ever predicted. The
stream is budgeted as a **bounded reserve inside the existing per-conference
spend envelope**, not a new line: `salience.interim_reserve_slots` in
[config/tracking.yaml](../config/tracking.yaml), set to `5` and enforced by the
selection pass — the reserve's slots in use displace the lowest-ranked cert
rank-fill picks in the pass's latest conference cohort (carve-outs above `N`
are untouched), so it trades slots inside `N` rather than adding a line, and
target total spend stays as published above and below. The trade is
prospective, pass by pass: sticky already-latched picks are never de-selected
and the pre-scoring fail-open window rides outside the quota for one cycle,
so a conference's realized count can transiently drift above `N` — the same
bounded drift the carve-outs already produce (see
[salience.md](salience.md)). A selected application occupies its slot until
it resolves, so the reserve also bounds the *concurrent* interim cells in
flight; an unfilled reserve displaces nothing and returns to cert. The slice
is predicted but not
yet skill-scored: the interim segment base rate publishes only at the
pre-registered resolved-count floor ([salience.md](salience.md)).

**The merits docket: a second cell on a case already funded, unbounded by
design.** A cert grant opens a merits event
([decision-model.md](decision-model.md)), and that event is forecastable, so a
granted docket buys one more predict cell per predictor and one more evaluate
cell when the judgment lands — roughly a second `≈$13` case-equivalent on top of
the cert cell already spent on it. Unlike the interim stream this carries **no
reserve and no quota**: nothing in the selection pass bounds merits cells. That
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

Two limits to set it with rather than against. It is **off by default** (a ceiling
of `0`), because a cost control that wedges the pipeline when misconfigured is
worse than none. And the ledger **lags** — a cell's `usage.json` reaches `data/`
only when its run's collect PR merges — so the figure it compares is a *floor* on
spend inside the window, never a live balance. Leave the gap between the ceiling
and the number you genuinely cannot exceed.

**Monthly spend by provider.** The per-case cost splits across the three API
bills — one predict cell and one evaluate cell per provider per case, both
columns measured — so at a cadence of `C` tournamented cases per month each
provider's bill is its per-case line × `C`:

| Provider (engine) | Predict $/case | Evaluate $/case | $/case | Share | At `C` = 150/mo |
|-------------------|---------------:|----------------:|-------:|------:|----------------:|
| Anthropic (`claude-fable-5`) | $3.65 | $4.16 | $7.81 | ≈70% | ≈$1,170 |
| OpenAI (`gpt-5.6-sol`) | $1.38 | $0.92 | $2.30 | ≈21% | ≈$345 |
| Google (`gemini-3.1-pro-preview`) | $0.55 | $0.52 | $1.07 | ≈10% | ≈$160 |
| **Total** | **$5.58** | **$5.60** | **≈$11** | | **≈$1.7K** |

The predict column rests on 138 / 132 / 140 cells per engine and is solid; the
evaluate column is one graded event, so read it as a first measurement. Roughly
**seven dollars in ten go to Anthropic** — size that provider's spend limit
accordingly, and expect a limit breach there to cost a third of a run's coverage
(the other engines are billed independently). The `C` = 150 column is a
reference month of one conference cohort filled to the per-conference cap (`C`
counts cases per month; a month holds several conferences, but mid-Term cohorts
run well under the cap — median ~11 petitions per conference — so 150/month is a
generous Term-month reference). September's long-conference month is the peak:
clearing the summer backlog at the larger cap is ≈200 × $13 ≈ **$2.6K** at the
planning rate (≈$2.2K measured), comfortably inside the ≈$5K bootstrapping
envelope — the headroom is deliberate, since the long conference is the one
cohort whose size is not yet observed.

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
`N ≈ inference_budget ÷ (≈$13 per fully-tournamented case)`. Each order of
magnitude in funding buys roughly ten times the tournamented cases:

| Scenario | ≈ Annual | Inference (= total − ≈$5K floor) | Reach |
|----------|----------|----------------------------------|-------|
| Bootstrapping | ≈$10K | ≈$5K | ≈390 fully-tournamented cases: the OT2026 long-conference cert release (≈200 petitions at the `long_conference_capacity` cap, ≈$2.6K) **plus** the Term's first regular conferences from the same envelope |
| Initial funding | ≈$100K | ≈$95K | ≈7,500 cases — more than the whole ≈5,500-event cert gate, which runs ≈$70K uncapped. The cert term is fully covered here, so salience is already a public ranking rather than a spend control |
| Well funded | ≈$1M | ≈$995K | covers all-14-court full scope outright (every event, ≈$570K), with room for deeper panels or more engines |
| **Floor (all scenarios)** | **≈$5K** | **—** | **misc + CourtListener + S3 + Actions; does not scale with `N`** |

The ladder is shorter than it looks: the corrected cell count puts **full cert
coverage inside the initial-funding step**, not beyond it. That makes the case for
salience-as-spend-control a *bootstrapping* argument specifically — above that
step it survives as the public ranking and the replay story, which is how
[salience.md](salience.md) frames it.

Start at **bootstrapping** with a small `N`, let the ledger keep measuring real
per-case cost against the ≈$13 planning rate, then raise `N` as funding lifts it. The funding path
to each state — credit programs and external support — is tracked in
[milestones.md](milestones.md).
