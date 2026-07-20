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
  [data-pipeline.md](data-pipeline.md) and the SCOTUS-docket gate in
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

### The process-version freeze (cutover marker)

The July/August predictions are the **shakedown** — real forward calls under a
process still being corrected. Every cell is stamped with its process version
(see [process-version.md](process-version.md)), and the headline metrics default
to the frozen process, so the shakedown is excluded without being deleted.

The **freeze** is the cutover: a one-line commit that blesses the current
process digest(s) into `FROZEN_PROCESS_DIGESTS`, run when the process is settled
and the first long-conference predictions are about to land. **Record the freeze
commit here when it happens** — it is the marker that separates the shakedown
from the frozen forward record.

- Freeze commit: _not yet frozen — the shakedown is ongoing._

## The near-term target: the OT2026 long-conference cert release

The first public release aims at the **September 2026 long conference**. Before
the Court meets (~late Sept), the pipeline predicts cert outcomes for the
petitions up for that conference; once the opening order list drops (~early
Oct), the realized grants/denies evaluate those predictions. The deliverable is
a blog post / short article — *"We predicted the long conference — here's how
we did"* — with the calibration numbers attached, compared against the
statpack's per-Term cert base rates. It is small, datable, and end-to-end, and
it defines the scope cleanly: the petitions on that conference list are SCOTUS
dockets, exactly the gate the budget sizes for its **bootstrapping** state
([budget.md](budget.md)).

## Following the cohort through the term

The cert release is the entry point, not the end. The ~year that follows is the
richest evaluation set and the real runway, so the sequence after it is what the
project is actually building toward.

- **Follow the granted cohort through the term.** Each cert grant opens a stream
  of downstream events on its SCOTUS docket — emergency / interim-docket
  applications, merits argument, the decision, and the per-justice votes —
  predicted and evaluated as they land. The predict/evaluate loop runs on the
  daily cadence across the OT2026 argument season, and a first leaderboard
  (`metrics/`) ranks predictors on resolved events (Brier and **Brier skill over
  the segment base rate**, accuracy, vote accuracy, reasoning quality), with
  mid-term updates riding the Oct–June grant cadence. This is the ~year of runway
  and the largest evaluation set the project accumulates.
- **The salience / big-case board as a public artifact.** Two pre-registered,
  datable releases land **distinct from the cert calibration numbers**: the
  deterministic **salience ranking** ("the petitions worth forecasting, ranked,
  *before* the conference sat") and the models' **big-case scores** ("how big we
  called them, *before* the term played out"). Both answer the post-hoc *"big
  case"* critique — the git timestamps prove the calls preceded the outcomes — and
  the big-case score adds a **second skill dimension** to the leaderboard: a model
  can read significance well while calling grant/deny only modestly, or the reverse.
- **End-of-term retrospective (~June 2027).** As the term's ~60–70 merits
  decisions land, predictions and evaluations across the full cohort publish as a
  retrospective accuracy report — the **capstone of the year's cohort-follow**, and
  the first full term of cost and calibration data.
- **Get funded at all — model-agnostic, tied to `N`.** Inference dominates the
  budget, so the near-term play is **bootstrapping** on credit programs (Anthropic
  startup credits primary, AWS Activate the runner-up) to run the cert release. The
  milestone proper is a first **external funding event** — a grant, an academic
  collaboration, or a first B2B pilot — that lifts the budget from bootstrapping to
  **initial funding** ([budget.md](budget.md)) and, mechanically, **raises `N`**:
  deepening the salience-ranked slice from the long-conference batch toward most of
  a cert term.
- **The ~1-year decision point.** With a term of cost and calibration data in
  hand, an explicit pivot: academic collaboration, B2B legal-analytics, or holding
  as a public-artifact project. Sustained external support here is the
  **well-funded** state ([budget.md](budget.md)), where `N` can approach the full
  cert gate and the **scope** call opens up — widen past the SCOTUS-docket gate
  toward the originating courts of appeals or a rotating appeals sample, or hold
  the gate as the durable scope. Options kept open until the data is in.

**Housekeeping, in parallel:** verify the S3 egress projections against the split
stores ([budget.md](budget.md)); route the remaining opinion-body reader
(`query --full`) through the content store; unify the index's transport onto the
same boto3 pattern as the content store; finish re-anchoring the budget once
evaluate-side per-run cost is measured (the predict side now is).

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
