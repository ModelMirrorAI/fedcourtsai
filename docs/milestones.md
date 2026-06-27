# Milestones

A target timeline for fedcourtsai, anchored to the Supreme Court's term calendar
so that public "releases" land when the Court is producing the events worth
predicting. Dates are targets, not commitments; the ordering and the calendar
anchors are the load-bearing part. For the system this builds on, see
[architecture.md](architecture.md), [data-pipeline.md](data-pipeline.md), and the
cost envelope in [budget.md](budget.md).

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
cleanly: the cert petitions on that conference list are themselves SCOTUS
interactions, so predicting them is the entry point of the SCOTUS-interaction gate
the budget sizes — no separate sampling rule to pick.

Everything in the next three months is sequenced to make that release possible.

## Timeline

### Within ~1 month (by end of July 2026) — foundations runnable end-to-end

- **Seed backfill running.** The `run:seed` tracking issue is open and the daily
  bulk backfill is loading all fourteen courts against its cursor (free bulk data,
  no API budget). This is the long pole; start it first so it completes well
  before the cert release.
- **Pull running daily.** Forward freshness keeps the live frontier current within
  the CourtListener budget; secure the membership tier the budget calls for.
- **One full cascade proven.** A single case flows seed/pull → `run:predict` →
  `run:evaluate` end-to-end, producing valid ledger artifacts — even if hand-
  triggered. This validates the contract before scale.
- **Cost instrumentation.** Capture real per-run token usage from the first
  predict/evaluate runs and replace the planning assumption in
  [budget.md](budget.md); set billing budgets + alerts.

### Within ~3 months (by the long conference, late Sept 2026) — the cert mini-release

- **Backfill complete** for all fourteen courts; steady state drops to quarterly
  bulk reconciliation.
- **Prediction scope gated and live.** Per the budget, predict a deliberate slice:
  a case becomes in-scope the first time it **interacts with the Supreme Court** (a
  cert petition is the trigger) and stays in-scope for the rest of its lifecycle —
  rather than saturating every event. This needs the gate itself to exist: a
  case-level predict-eligibility latch that the predict fan-out filters on, while
  ingestion stays full-coverage. See *The pilot slice* in [budget.md](budget.md).
- **Cert-grant predictions issued** for the petitions on the long-conference list,
  by the competing predictors, *before* the conference.
- **Mini-release published** once the opening order list resolves them (~early
  Oct): the article + the first head-to-head predictor calibration.

### Within ~6 months (by ~Dec 2026) — steady state + first leaderboard

- **Full predict/evaluate loop operating** across the chosen slice on the daily
  cadence, with the matrix fan-out and per-run tracking issues working unattended.
- **First leaderboard / metrics artifact** (DVC `metrics/`) ranking predictors on
  the events resolved so far — Brier score, accuracy, vote accuracy, reasoning
  quality. A mid-term "how the predictors are doing" update can ride the
  Oct–Dec argument-and-grant cadence.
- **Quarterly reconciliation proven** — the Dec bulk snapshot drives a seed
  reconciliation pass without disrupting pull.
- **Data validation live** — a `validate-corpus` verdict (schema conformance,
  corpus integrity, cross-store referential checks) runs on the corpus-writer path
  and surfaces in the ops dashboard as data-health, with failures escalated to a
  single issue — the automated successor to the manual corpus spot-check.

### Within ~1 year (by mid-2027) — full-docket release + back-testing

- **OT2026 end-of-term release** (late June 2027): predictions and evaluations
  across the full merits docket as the term's ~60–70 decisions land — the richest
  evaluation moment of the year — published as a retrospective accuracy report.
- **Scope decision — widen the gate?** With a year of cost data, decide whether to
  predict past the SCOTUS-interaction gate — e.g. a rotating sample of appeals that
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

## Recurring release rhythm

Once the loop is steady, the calendar yields a repeatable publishing cadence
without inventing new work:

- **Late Sept / early Oct** — long-conference cert release (the anchor).
- **Oct–Apr** — periodic merits-prediction updates as arguments and order lists
  land.
- **Late June** — end-of-term retrospective across the full merits docket.
- **Annually** — predictor leaderboard for the completed term.
