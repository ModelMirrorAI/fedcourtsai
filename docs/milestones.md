# Milestones

Where the project stands and what it is aiming at, anchored to the Supreme
Court's term calendar so public "releases" land when the Court is producing the
events worth predicting. It is a sequence, not a set of dated commitments: the
external anchors — the long conference, the end of term — are fixed; the
internal ordering is load-bearing; the specific timing is a working estimate,
shared for transparency. (The project's accountable forecasts are its
committed predictions, which are evaluated against real outcomes — not this
planning document.)

## Why anchor to the SCOTUS calendar

The Court runs on a predictable annual cycle, and each phase generates a
different, datable supply of predictable events. Building releases around it
means predictions are published *before* the outcomes exist and evaluated *as*
they arrive — the only honest way to show calibration.

| Phase | Timing | What it supplies to predict |
|-------|--------|------------------------------|
| **Long Conference** | Last week of September | The Court clears ~2,000 cert petitions accumulated over summer — the single largest, most datable burst of cert grant/deny decisions of the year |
| **Term opens** | First Monday in October (**OT2026: Oct 5, 2026**) | Opening order list (long-conference grants/denials); argument calendar begins |
| **Grant cadence** | Order lists, most Mondays after each conference, Oct–June | Steady stream of cert decisions |
| **January "mop-up" conference** | Mid-January | Last grants that can still be argued the same term — a natural cutoff |
| **Term ends** | Late June / early July | The full merits docket resolves — ~60–70 argued cases decided, the richest evaluation set of the year |
| **Summer recess** | July–September | No new merits; time to load history, back-test, and retune |

Sources: [28 U.S.C. § 2](https://www.law.cornell.edu/uscode/text/28/2) (term start),
[SCOTUSblog: the long conference](https://www.scotusblog.com/2025/08/what-is-the-supreme-courts-long-conference/),
[Court procedures](https://www.supremecourt.gov/about/procedures.aspx).

## Where the pipeline stands

The machinery for the first release is running:

- **Ingestion is live on all three channels.** The daily historical Term
  walker grows per-Term coverage of decided petitions (supremecourt.gov, no
  API budget) for the statpack's per-Term base rates and the cert back-test
  set; the supremecourt.gov live channel owns SCOTUS freshness budget-free
  (discovery, the conference watchlist, outcomes, filed-document text); pull's
  daily CourtListener windows do targeted enrichment under the held membership
  tier.
- **The corpus split is on in production**: the writers keep a payload-free
  index and mirror bulk payloads to the per-case content store, and forward
  cells provision from the store (see
  [data-pipeline.md](data-pipeline.md)).
- **Prediction scope is gated and live**: SCOTUS dockets only, with the shared
  deterministic exclusions — see the prediction scope in
  [data-pipeline.md](data-pipeline.md) and *The pilot slice* in
  [budget.md](budget.md).
- **The cascade runs on its real triggers**: live cases flow through
  `run:predict` → `run:evaluate`, producing valid ledger artifacts, with
  per-run cost measured from the engines' own logs (`usage.json`, the spend
  roll-up on the ops dashboard) and data validation surfacing as data-health.
- **Predictors are vetted by cert back-test**: the maintainer-triggered
  `run-backtest` workflow replays predictors over decided petitions (outcomes
  hidden) — iteration signal for prompts, retrieval, and calibration, never
  claimable performance.
- **The forward record begins with the OT2026 cert cycle.** The ledger holds
  SCOTUS events and realized outcomes; forward predictions and their
  evaluations accumulate from here, so the published record is consistent with
  the current design end to end.

## The near-term target: the OT2026 long-conference cert release

The first public release aims at the **September 2026 long conference**. Before
the Court meets (~late Sept), the pipeline predicts cert outcomes for the
petitions up for that conference; once the opening order list drops (~early
Oct), the realized grants/denies evaluate those predictions. The deliverable is
a blog post / short article — *"We predicted the long conference — here's how
we did"* — with the calibration numbers attached, compared against the
statpack's per-Term cert base rates. It is small, datable, and end-to-end, and
it defines the scope cleanly: the petitions on that conference list are SCOTUS
dockets, exactly the gate the budget sizes.

## After the release

- **Steady state across the OT2026 argument season**: the predict/evaluate
  loop on the daily cadence, a first leaderboard (`metrics/`) ranking
  predictors on resolved events — Brier score, accuracy, vote accuracy,
  reasoning quality — with a possible mid-term update riding the Oct–Dec
  grant cadence.
- **Post-cutover follow-ups**: verify the S3 egress projections against the
  split stores ([budget.md](budget.md)); route the remaining opinion-body
  reader (`query --full`) through the content store; unify the index's
  transport onto the same boto3 pattern as the content store; re-anchor the
  budget once evaluate-side per-run cost is measured.
- **End-of-term release (~June 2027)**: predictions and evaluations across the
  full merits docket as the term's ~60–70 decisions land, published as a
  retrospective accuracy report.
- **Scope decision — widen the gate?** With a year of cost data, decide whether
  to predict past the SCOTUS-docket gate — e.g. the originating
  courts-of-appeals dockets, or a rotating sample of appeals that never reach
  SCOTUS — using the budget's levers, or to hold the gate as the durable scope.

## Beyond a year — the automated-research goal

The long-run aim is a harness that proposes new predictor designs, registers
them in the registry, and lets `run-predict` / `run-evaluate` run the
tournament that ranks them. Nothing in the data or control flow has to change
for it — a predictor is just an id, an engine, and a prompt — so it is
sequenced after the loop and the leaderboard are proven, and after back-testing
gives a cheap way to screen candidates before they spend live budget.

**Partnership-gated architecture: Free Law Project.** Several ingestion
upgrades wait on an established relationship (and, for some, funding) with
Free Law Project rather than on engineering:

- **Database replication** — a hosted Postgres replica under FLP's replication
  agreement consolidates the ingestion upstreams: full field coverage,
  continuously current, no request caps (see *The planned end-state* in
  [data-pipeline.md](data-pipeline.md)).
- **Webhooks** — CourtListener's docket-alert webhooks could replace polling
  for liveness (relevant mainly if the scope ever widens past SCOTUS, whose
  own site the live channel already polls without limits).
- **Opinion bodies from the replica** — would obviate storing opinion text in
  the content store and close out the remaining opinion-body read path.

The corpus boundary and everything downstream of ingestion are unchanged by
design under all of these.
