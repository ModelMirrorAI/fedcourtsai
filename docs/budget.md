# Budget

A cost forecast, not a spending cap. Figures are USD and rough by design: they
size the project at two funding levels so scope can be chosen with the bill in
view. What each increment of funding buys, step by step, is in
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
- **`P` — how many predictors forecast each event.** Each predictor adds its
  own prediction run, plus the cost of three evaluator models grading that
  prediction. So `P` raises the cost *per event*, by an amount that depends on
  which model is added: measured prediction runs span roughly $0.60 to $4.30
  across the current three.

At today's `P = 3` with three evaluators, one fully predicted and evaluated
event costs roughly **$15–17**. The evaluator count holds at 3 as `P` grows.
Per-run token usage and cost are recorded on the ledger (`usage.json`, rolled
up by `fedcourts usage-summary`), so these rates are re-measured continuously
rather than assumed.

## Scenario 1: Bootstrapping

The current state. Three predictors (Anthropic, OpenAI, Google) forecast a
salience-ranked slice of the paid SCOTUS cert docket plus every interim and
merits event it leads to — on the order of 850–1,100 events a Term.

| | Monthly | Yearly |
|---|---:|---:|
| Model API spend | $2,000 | $24,000 |
| Other spend | $600 | $7,200 |
| **Total** | **$2,600** | **$31,200** |

## Scenario 2: Scaling

The funded target. Every paid SCOTUS petition is forecast at every prediction
moment, by seven model developers' predictors plus prompt-lens variants — the
end state of the four milestones in [milestones.md](milestones.md).

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
