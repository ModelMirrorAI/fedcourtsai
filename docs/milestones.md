# Milestones

Where the project is, and what each increment of funding buys. The scaling
plan is six milestones taken in order, each with the annual funding level the
project needs to reach **before committing to it**. Dollar figures are rough
planning estimates built on the rates in [budget.md](budget.md); the ledger
re-measures them as each step lands. (The project's accountable forecasts are
its committed predictions, not this planning document.)

## Where things stand

The pipeline runs end to end at the **bootstrapping** level
([budget.md](budget.md)): three predictors (Anthropic, OpenAI, Google), each
cross-evaluated by three judges, forecasting a salience-ranked slice of the
paid SCOTUS cert docket and every interim and merits event downstream of it.
The dated record of process-version freezes is
[freeze-record.md](freeze-record.md).

Public releases are anchored to the Court's calendar, so predictions publish
*before* outcomes exist and are scored *as* they arrive:

- **Release 1 — the OT2026 long conference (late Sept–Oct 2026).** Cert
  predictions committed before the conference, scored against the opening
  order list ([release-ot2026-long-conference.md](release-ot2026-long-conference.md);
  its reader-facing page is [release-ot2026-public-summary.md](release-ot2026-public-summary.md)).
- **Release 2 — mid-Term (~January 2027).** Timed to the January mop-up
  conference, the last at which a grant can still be argued the same Term.
  First populated leaderboard, plus the pre-registered salience ranking and
  big-case scores.
- **Release 3 — end-of-Term retrospective (~June–July 2027).** The full merits
  docket resolves; the first complete Term of calibration and cost data
  ([release-ot2026-merits.md](release-ot2026-merits.md) is the skeleton and
  evidence plan for its merits part).

None of the releases depends on the funding below. Funding changes how much of
the docket, how many moments, and how many models each release covers.

Between releases, the site's email list is planned to carry two optional
updates a subscriber chooses: a **weekly SCOTUS update** (what resolved against
what each model forecast, and the forecasts newly committed) and an **AI-cases
feed** (new filings and rulings on the AI-case watchlist below, with that
slice's forecasts as an opt-in addition). Each update's body is rendered from
committed data; the only model-written text is an optional ruling summary,
labelled with its model. Each send will be a draft a person approves, and
neither update is scored. They cost almost nothing beyond those summaries, so
they sit outside the scaling plan.

## The scaling plan

| Milestone | Model API / yr (cumulative) | Other / yr | **Funding needed / yr** |
|---|---:|---:|---:|
| Today — bootstrapping | ≈$17K (of the $24K envelope) | $7K | **≈$31K** |
| 1. More prediction events | ≈$22K (of the $24K envelope) | $7K | **≈$31K** |
| 2. The AI-case watchlist | ≈$24K (the whole $24K envelope) | $7K | **≈$31K** |
| 3. All paid cases | ≈$47K | $28K | **≈$75K** |
| 4. A D.C. Circuit slice | ≈$52K | $28K | **≈$80K** |
| 5. Seven model developers | ≈$74K | $28K | **≈$102K** |
| 6. Prompt lenses | up to $120K | $28K | **≈$148K** |

Every column is cumulative: each row is the whole project's annual run rate
at that milestone, not the increment over the row above. The first three rows
sit inside the bootstrapping envelope, so their funding figure is that
envelope rather than the sum of the row. Other spend is assumed to step from the
bootstrapping to the scaling level at milestone 3, when volume starts to grow.
The model-spend column is priced at about $17 per fully evaluated SCOTUS
event, the pinned planning table's total, and $30–60 per lower-court event.
The table prices the gemini pair at `gemini-4-argon`'s first measured cells
doubled for the rate in force from 2026-12-01, about $3.40 of each event;
the scaling is rough from milestone 5, where more predictors change each
engine's share of an event. At milestone 2 the column fills the
bootstrapping envelope, so any further spend inside it would outgrow it. At the about $10 per SCOTUS event [budget.md](budget.md)
measures, today's row is ≈$8.5–11K and milestone 3's ≈$21–27K. The table
stays the planning ceiling until a round of measured cells re-anchors it.

The order is deliberate. New moments are cheap and raise the value of every
case already covered, so they come first. The AI-case watchlist comes next
because it costs little and is built for its audience: at most a few dozen
events a year fit inside the bootstrapping envelope, and it builds the lower-
court machinery the D.C. Circuit slice reuses. Full SCOTUS coverage comes
before more models because the project's claims are coverage claims, and every
later predictor multiplies over the events this step buys. The D.C. Circuit
slice follows full SCOTUS coverage, so it is measured against a finished
baseline, and both lower-court slices come before new models, so their
sourcing and costs are learned at three predictors rather than seven. New
developers come before prompt variants because a baseline for each model has
to exist before a variant of it means anything.

### 1. More prediction events — within bootstrapping (≈$31K / yr)

Add the moments where a case's information set materially changes, starting
with the one the public cares about most:

- **Post-oral-argument** — every argued case, after the transcript is out
  (~60 events a Term). Declared, minted and forecast (`evt-argument-judgment`,
  moment `argued` on the merits stage).
  The live poll already stores each transcript the Court lists, as the
  `argument-transcript` document only this moment's cells are handed.
- **SG brief after a CVSG** — the Solicitor General's recommendation (~20).
  Declared, parsed, minted and forecast (`evt-brief-sg-disposition`, moment
  `sg-brief`).
- **Late-Term authorship elimination** — a fixed calendar date on which every
  still-undecided argued case is re-forecast, once the pattern of who has
  written from each sitting is visible (~25). The pattern is read but not yet
  declared as a moment: the live poll stores the Court's argument sittings, and
  `fedcourts authorship-tally` reads each sitting's authors and undecided cases
  as of a day from the per-opinion record. That record holds OT2020–OT2025,
  and the opinion-record standing sweep on run-seed's daily window keeps the
  current and previous Term in it; the live poll back-fills the sittings of
  every Term from OT2020 on, so the tally reads the Terms that record holds.
  The tally is context, not a claim. The claims it informs are declared as
  distribution claims (`majority-author`, `separate-writers`, *The authorship
  claims* in [outcome-decomposition.md](outcome-decomposition.md)) in a set
  version every merits moment names and the predict prompt elicits, scored
  against strictly-prior baselines; the late-Term moment still owes the eight
  tests.
- **First-relist re-forecast** and **call for response** — the strongest public
  cert-stage signals. Both are declared, parsed and minted. The first relist
  (`evt-order-relist-disposition`, moment `relist`), which fires once per
  petition rather than at every relist, is forecast. The call for response
  (`evt-order-call-for-response-disposition`, moment `response-requested` on
  the cert stage) is switched off: no cell is filed under it until the process
  version whose predict prompt names it, because its first polls open events
  for petitions called long before, and how those count is not yet decided.

These add a few hundred events at most, mainly on the low-volume merits track,
so the cost is engineering rather than inference: each moment is a
pre-registered population with its own base rate, and new inputs (argument
transcripts) move the registered process version.

### 2. The AI-case watchlist — within bootstrapping (≈$31K / yr)

Follow a hand-curated watchlist of 10–20 AI cases — cases where an AI
developer, or an AI system's training, outputs or deployment, is central to a
claim or defense — from the district court up. It exists for its audience: the
evaluation and forecasting communities follow these cases closely, and
little timestamped, structured coverage of them exists. The list and the rule
that admits a case are committed, and a case is added on a dated line. Its
cases carry an `ai` tag that follows them to any appeal or cert petition; the
tag never changes SCOTUS selection.

What the step adds:

- **A district stage.** Court-agnostic trial-court moments, each opening when a
  motion is fully briefed: a motion to dismiss, class certification, summary
  judgment, and final disposition. Outcomes include ruling *in part*, which is
  the usual result, and *no merits decision* for a settlement or voluntary
  dismissal. Nothing is voided: a settlement or a mooted motion is something
  forecasts price in.
- **The AI-cases feed before any forecast.** New filings and rulings on watchlist
  dockets, with links to the public record, ship first; forecasts are added
  once the district moments are registered.
- **Forecasts on a developer's own case.** Several watchlist cases name as a
  party the developer of one of the project's predictors. A comparison of how
  a predictor forecasts its own developer's cases against the other predictors
  is pre-registered before the first such forecast, reported as descriptive at
  watchlist size, and every surface discloses which developer is a party.
- **The lower-court machinery.** Docket ingestion for exactly the listed
  dockets (the one planned exception to the corpus's exclusion of district
  courts), documents from the RECAP archive, a prediction scope keyed on a
  committed slice list, and docket push. The D.C. Circuit slice reuses each.

A case reaches one or two moments in a typical year, so the watchlist is
roughly 10–40 events a year. Lower-court records are larger than SCOTUS ones,
so a fully evaluated event is estimated at ≈$30–60, to be re-measured on the
first events: ≈$1–2K of model spend a year. At the planning table's rates
that upper end already fills the bootstrapping envelope, and if every case
reached all four moments in one year (80 events at $60), it would be ≈$5K
and the step would outgrow it. Most of these dockets are already well
covered in RECAP, so document purchases should be rare. Watchlist forecasts
score in their own stratum and never enter SCOTUS headline figures; the list
is not a coverage claim.

### 3. All paid cases — ≈$75K / yr

Raise the salience gate's capacity until every paid SCOTUS petition not
removed by a deterministic filter (such as the in-forma-pauperis exclusion) is
forecast at every moment, and widen the interim reserve to the full stream of
substantive applications. Roughly 2,100–2,500 events a Term, up from
~850–1,100. At this point salience stops being a spend control and survives
as the public, pre-registered ranking.

### 4. A D.C. Circuit slice — ≈$80K / yr

Forecast a small, pre-registered slice of the U.S. Court of Appeals for the
D.C. Circuit: on the order of 25–50 argued cases a year, chosen by a rule
committed before the first forecast. The slice is a test, not a coverage
claim. It proves circuit sourcing, cost, and resolution end to end before any
wider lower-court work is planned or priced.

The D.C. Circuit fits a first appellate slice. Its docket leans toward agency and
government cases, which often reach the Supreme Court. It runs CM/ECF on
PACER, its opinions are free, and it posts argument audio. The corpus already
ingests `cadc`, so base rates and retrieval history exist.

It reuses the lower-court machinery the AI-case watchlist built. What the
step adds:

- **Three moments per case, around the panel.** A forecast when argument is
  scheduled but the panel is not yet known; another once the court posts the
  panel, about 30 days before argument; and a third after argument. The first
  two are built first. The post-argument moment follows once argument audio
  can be transcribed, since the court posts audio but no transcript.
- **What the panel changes.** The first two forecasts are on the same case and
  record, differing mainly in whether the panel is known. Comparing them
  measures how much knowing who will judge a case moves and improves the
  forecast, prospectively and on the public ledger. At slice size this is a
  description, not a significance test.
- **Circuit outcomes** — affirm, reverse, vacate, remand, or dismiss, in whole
  or in part, or no merits decision at all. Once the panel is known, also each
  judge's vote and whether anyone dissents. Nothing is voided: a panel swap or
  a settlement is something forecasts price in, and a case can be re-predicted
  beside its earlier forecasts, which still score.
- **Circuit documents** — briefs and orders from the RECAP archive, or bought
  from PACER through RECAP Fetch when missing, which returns them to the
  public archive. Roughly $20–40 a case.
- **Docket push** — CourtListener docket-alert webhooks through a small relay,
  since the circuit docket has no free live source. Webhook access is unpriced
  pending Free Law Project's commercial terms, and getting a real quote is one
  aim of this step.

At the ≈$30–60 estimated for a fully evaluated lower-court event, two moments
on about 50 cases is about 100 events a year, ≈$5K of model spend, re-measured
on the first circuit events; the post-argument moment adds about half again,
plus transcription. Circuit forecasts are scored in their own stratum and never
enter SCOTUS headline figures.

### 5. Seven model developers — ≈$102K / yr

Add a baseline predictor for four more developers — **xAI, Moonshot, Meta, and
Alibaba** — each running its most capable model inside its own coding harness
(Grok Build, Kimi Code, Muse Code, Qwen Code), the same way the current three
run. Same prompt, same retrieval tools, so the comparison is like for like.
The new models are inexpensive to run; most of the added cost is three judges
grading four more predictions per event, a margin the first new predictor's
fan-out will measure. New predictors are not judges: the evaluator panel
stays at three.

Each of the four is a new **engine**, not a registry entry. `engine` is a closed
enumeration mirrored into the exported schemas, so a new developer needs an enum
value, a default model in the pricing table, a retrieval-surface entry in the
process-version registry, a client-config emitter for its own MCP dialect, a
usage-log parser with its own `record-usage` file flag, a backend in the pipeline
runner, and its own steps in both cell workflows. That adapter work is in none
of the figures above, and it is why prompt lenses — which are a registry entry plus a prompt template — come
last.

### 6. Prompt lenses — up to ≈$148K / yr

Field three **prompt-lens variants** that instruct a model to reason from one
perspective — **legal/doctrinal, political, economic** — and let the
tournament rank them against the baselines. This tests, prospectively and on a
public ledger, the oldest argument about the Court: whether law or politics
better predicts what it does. Each lens partitions from its parent under its
own process version, so any difference in score is attributable to the prompt
alone. Lenses run on a subset of models sized to the remaining budget (about
three models at full coverage), reaching the **scaling** scenario in
[budget.md](budget.md).

Other ways to spend at this stage, several of them nearly free, to be weighed
against the lenses when the milestone opens:

- **Aggregate predictors** — mean, median, and extremized ensembles of the
  baselines, plus a base-rate floor, committed at prediction time (≈$0).
- **Resampling** — the same predictor run repeatedly on a fixed stratum, to
  measure the within-model noise floor any leaderboard gap must clear.
- **Smaller sibling models** from each developer — does general capability
  track forecasting skill within a family?
- **Retrieval ablations** — closed-book or no-CourtListener variants, which
  double as a contamination probe.
- **A second circuit with different panel practice** — the 4th, 7th and
  Federal Circuits do not announce panels before argument, so every
  pre-argument forecast there is panel-blind. Set beside the D.C. Circuit
  slice, it asks whether courts that reveal panels early are more predictable
  before argument.
- **Open-harness twins** — each model re-run inside one shared open-source
  harness, separating the model's contribution from its vendor harness's.
