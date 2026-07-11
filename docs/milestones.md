# Milestones

A target timeline for fedcourtsai, anchored to the Supreme Court's term calendar
so that public "releases" land when the Court is producing the events worth
predicting. It is a sequence, not a set of dated commitments: the external
anchors — the long conference, the end of term — are fixed; the internal ordering
is load-bearing; the specific timing is our best estimate and, like any forecast
this project makes, will be reported against honestly rather than quietly revised.

## Why anchor to the SCOTUS calendar

The Court runs on a predictable annual cycle, and each phase generates a
different, datable supply of predictable events. Building releases around it means
predictions are published *before* the outcomes exist and evaluated *as* they
arrive — the only honest way to show calibration.

| Phase | Timing | What it supplies to predict |
|-------|--------|------------------------------|
| **Long Conference** | Last week of September | The Court clears ~2,000 cert petitions accumulated over summer — the single largest, most datable burst of cert grant/deny decisions of the year |
| **Term opens** | First Monday in October (**OT2026: Oct 5, 2026**) | Opening order list (long-conference grants/denials); argument calendar begins |
| **Grant cadence** | Order lists, most Mondays after each conference, Oct–June | Steady stream of cert decisions |
| **January "mop-up" conference** | Mid-January | Last grants that can still be argued the same term — a natural cutoff |
| **Term ends** | Late June / early July | The full merits docket resolves — ~60–70 argued cases decided, the richest evaluation set of the year |
| **Summer recess** | July–September | No new merits; time to seed, back-test, and retune |

Sources: [28 U.S.C. § 2](https://www.law.cornell.edu/uscode/text/28/2) (term start),
[SCOTUSblog: the long conference](https://www.scotusblog.com/2025/08/what-is-the-supreme-courts-long-conference/),
[Court procedures](https://www.supremecourt.gov/about/procedures.aspx).

The courts of appeals have no comparable national calendar — they decide
~42K cases/yr on a rolling basis ([Judicial Business 2025](https://www.uscourts.gov/data-news/reports/statistical-reports/judicial-business-united-states-courts/judicial-business-2025/us-courts-appeals-judicial-business-2025))
— so they are the *steady-state* workload, while SCOTUS provides the *release
moments*.

## The near-term target: the OT2026 long-conference cert release

The first public release aims at the **September 2026 long conference**. Before
the Court meets (~late Sept), the pipeline predicts cert outcomes for the
petitions up for that conference; once the opening order list drops (~early Oct),
the realized grants/denies evaluate those predictions. The deliverable is a blog
post / short article: *"We predicted the long conference — here's how we did,"*
with the calibration numbers attached. It is small, datable, and end-to-end —
exactly the right shape for a first pilot. It also defines the pilot's scope
cleanly: the cert petitions on that conference list are SCOTUS dockets, so
predicting them is exactly the SCOTUS-docket gate
the budget sizes — no separate sampling rule to pick.

Everything in the next three months is sequenced to make that release possible.

## Timeline

### Phase 0 — Foundations (before the first cert release)

- **Historical Term walking running.** The `run-pull` historical job walks
  decided October Terms newest-first over supremecourt.gov (no API budget),
  filling the statpack's per-Term base rates and the cert back-test set.
- **Freshness running daily.** Done, and better than planned: the
  supremecourt.gov live channel owns SCOTUS freshness budget-free (discovery,
  conference watchlist, outcomes, documents), while pull's daily CourtListener
  windows do enrichment under the held membership tier.
- **One full cascade proven.** Done — live cases flow through
  `run:predict` → `run:evaluate` on the real triggers, producing valid ledger
  artifacts.
- **Cost instrumentation.** Done — per-run token usage is measured from the
  engines' own logs (`usage.json`, the spend roll-up on the ops dashboard) and
  [budget.md](budget.md) carries measured rates; billing alerts remain a
  provider-console task.

### Phase 1 — Long-conference cert release (OT2026 long conference, late Sept 2026)

- **Historical coverage sufficient for the task**: the bulk-era load plus
  the daily historical Term walker growing per-Term coverage through the live
  channel (a bulk-shaped source would re-enter through the shared normalizer).
- **Prediction scope gated and live.** Per the budget, predict a deliberate
  slice: **SCOTUS dockets only** — the predict fan-out filters on the corpus
  row's court, while
  ingestion stays full-coverage. See *The pilot slice* in [budget.md](budget.md).
- **Cert-grant predictions issued** for the petitions on the long-conference list,
  by the competing predictors, *before* the conference.
- **Mini-release published** once the opening order list resolves them (~early
  Oct): the article + the first head-to-head predictor calibration.

### Phase 2 — Steady state + first leaderboard (across the OT2026 argument season)

- **Full predict/evaluate loop operating** across the chosen slice on the daily
  cadence, with the matrix fan-out and per-run tracking issues working unattended.
- **First leaderboard / metrics artifact** (DVC `metrics/`) ranking predictors on
  the events resolved so far — Brier score, accuracy, vote accuracy, reasoning
  quality. A mid-term "how the predictors are doing" update can ride the
  Oct–Dec argument-and-grant cadence.
- **Corpus completeness spot-checked** against a fresh upstream sample (the
  live channel keeps the prediction-relevant slice current continuously).
- **Data validation live.** Done — the `validate-corpus` verdict (schema
  conformance, corpus integrity, cross-store referential checks) runs on the
  corpus-writer path and surfaces on the ops dashboard as data-health, with
  failures escalated to a single issue.

### Phase 3 — Full-docket release + back-testing (end of OT2026 term, ~June 2027)

- **OT2026 end-of-term release** (late June 2027): predictions and evaluations
  across the full merits docket as the term's ~60–70 decisions land — the richest
  evaluation moment of the year — published as a retrospective accuracy report.
- **Scope decision — widen the gate?** With a year of cost data, decide whether to
  predict past the SCOTUS-docket gate — e.g. the originating courts-of-appeals
  dockets, or a rotating sample of appeals that
  never reach SCOTUS — using the budget's levers, or to hold the gate as the durable
  scope.
- **Back-testing live.** Replay current predictors against historical resolved
  events from the corpus (outcome hidden), scored against known dispositions —
  turning the seeded history into an evaluation asset, and a credible way to vet a
  new predictor before it competes live.

### Beyond a year — the automated-research goal

The long-run aim ([architecture.md](architecture.md)) is a harness that proposes
new predictor designs, registers them in the registry, and lets `run-predict` /
`run-evaluate` run the tournament that ranks them. Nothing in the data or control
flow has to change for it — a predictor is just an id, an engine, and a prompt —
so it is sequenced after the loop and the leaderboard are proven, and after
back-testing gives a cheap way to screen candidates before they spend live budget.

**Infrastructure step, funding-gated: the CourtListener database replica.** Once
the project has the support to pay for Free Law Project's replication agreement
and host a Postgres replica, the ingestion upstreams consolidate onto it — full
field coverage, continuously current, no request caps (see *The planned
end-state* in [data-pipeline.md](data-pipeline.md)). The corpus boundary and
everything downstream of ingestion are unchanged by design; the interim
guardrails in that section are what keep this a swap rather than a rebuild.
